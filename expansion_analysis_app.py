import pandas as pd
import numpy
import statistics
from census import Census

def fetch_expansion_analysis():
    # =========================================================================
    # 1. Configuration & Setup
    # =========================================================================
    # Secure API key storage and file path definitions. 
    # TODO for Production: Move API key to an environment variable (.env) for security compliance.
    CENSUS_API_KEY = "6d0f38310f6a8148a35638bbcb5a7f9b10bbd2cd"
    csv_file = "StoresPerState.csv"
    competitor_csv = "Retail Competitor Store Counts 2026.csv"

    # =========================================================================
    # 2. Load Store and Competitor Data
    # =========================================================================
    try:
        # Load internal store footprint data
        df_stores = pd.read_csv(csv_file)
        
        # Using median here instead of mean to protect against outliers (e.g., states with massive store counts like CA or TX)
        median_stores = statistics.median(df_stores['Stores'])
        
        # Format FIPS codes: Ensure state codes are strings and left-padded with zeros (e.g., '5' becomes '05') to match Census Bureau requirements
        states = df_stores['State code'].astype(str).str.zfill(2).tolist()
        
        # Load external competitor landscape data for market share validation
        df_competitors = pd.read_csv(competitor_csv)
    
    except Exception as e:
        # Error handling to prevent script from crashing and to help debug data pipeline issues quickly
        print(f"Error reading CSV files: {e}")
        return

    # Initialize the wrapper for the Census Bureau API
    c = Census(CENSUS_API_KEY)

    # Demographic Variable Mapping (ACS 5-Year Estimates)
    # Target Demographic Definition: Males and Females aged 18 to 34 (prime sneaker/athletic retail demographic)
    age_variables = [
        'B01001_007E', 'B01001_008E', 'B01001_009E', 'B01001_010E', 'B01001_011E', 'B01001_012E', # Male brackets
        'B01001_031E', 'B01001_032E', 'B01001_033E', 'B01001_034E', 'B01001_035E', 'B01001_036E'  # Female brackets
    ]
    
    # Economic indicators to evaluate market purchasing power vs. retail labor costs
    economic_variables = ['B19013_001E', 'B24011_027E'] # Median HH Income, Median Retail Earnings
    all_vars = ['NAME', 'B01001_001E'] + economic_variables + age_variables # B01001_001E = Total State Population

    # =========================================================================
    # 3. Fetch National Benchmarks (For Baseline Comparison)
    # =========================================================================
    print("Fetching National Benchmarks...")
    # Pulling national data to act as our control group/baseline metrics
    national_data = c.acs5.us(fields=['B19013_001E', 'B24011_027E'] + age_variables, year=2024)
    
    natl_df = pd.DataFrame(national_data)
    national_avg_income = natl_df['B19013_001E'].iloc[0]
    
    # Aggregate all the age brackets horizontally to find total national target audience
    national_total_target_pop = natl_df[age_variables].sum(axis=1).iloc[0]

    # =========================================================================
    # 4. Fetch State-Level Data (Iterative API requests)
    # =========================================================================
    print(f"Fetching 2024 data for {len(states)} states...")
    results = []
    for fips in states:
        # Loop through each state FIPS code to extract localized demographic data
        data = c.acs5.state(all_vars, fips, year=2024)
        results.extend(data)

    # =========================================================================
    # 5. Data Processing & Feature Engineering
    # =========================================================================
    df = pd.DataFrame(results)
    
    # Calculate operational baseline for retail wages across our active markets
    national_avg_retail_income = df['B24011_027E'].mean()
    
    # Feature 1: Total target demographic size per state
    df['state_target_pop'] = df[age_variables].sum(axis=1)
    
    # Data Alignment Check: Mapping internal store counts directly to dataframe. 
    # NOTE: Assumes the API return order perfectly matches the CSV row order. Recommend changing to a formal merge on FIPS code in next sprint.
    df['no_stores'] = df_stores['Stores'].values 
    
    # Feature 2: Market Density (Percentage of the state's population that falls into our target demographic)
    df['target_pop_pct'] = (df['state_target_pop'] / df['B01001_001E']) * 100
    
    # Calculate averages from state distributions to use as benchmarks for scoring
    average_target_pop_pct = df['target_pop_pct'].mean()
    average_target_pop = df['state_target_pop'].mean()
    
    # Data Integration: Merging external competitor datasets using 'State Name' as the foreign key
    df = df.merge(df_competitors, left_on='NAME', right_on='State', how='left')
    
    # Data Cleaning: Handle missing values resulting from the left join (null means competitor has 0 presence there)
    competitor_cols = ['Big 5 Sporting Goods', 'Nike Stores (Direct)', 'Scheels', 'Hibbett Sports']
    for col in competitor_cols:
        df[col] = df[col].fillna(0)
        
    # Find the strongest competitor presence in each state to identify the primary market threat
    df['max_competitor_stores'] = df[competitor_cols].max(axis=1)
    
    # Risk Assessment Logic: Flagging states where a single competitor dominates our current footprint by more than 150%
    df['not_competitor_dominated'] = numpy.where(df['max_competitor_stores'] <= 1.5 * df['no_stores'], 1, 0)
    
    # -------------------------------------------------------------------------
    # --- Binary Scoring Matrix (Business Logic Engine) ---
    # -------------------------------------------------------------------------
    # Building a heuristic framework where 1 = Favorable Market Condition, 0 = Unfavorable
    
    # Market Size: Is the target population larger than the average state?
    df['avobe_avrg_targ_pop'] = numpy.where(df['state_target_pop'] > average_target_pop, 1, 0)
    
    # Market Concentration: Is the concentration of 18-34 year olds higher than average?
    df['avobe_avrg_targ_pop_pct'] = numpy.where(df['target_pop_pct'] > average_target_pop_pct, 1, 0)
    
    # Purchasing Power: Does the state exceed the national median household income?
    df['avobe_avrg_income'] = numpy.where(df['B19013_001E'] > national_avg_income, 1, 0)
    
    # Market Opportunity (Under-penetration): Do we currently have fewer stores here than our median footprint?
    df['below_median_no_stores'] = numpy.where(df['no_stores'] < median_stores, 1, 0)
    
    # Labor Cost Index: Are retail wages below average here? (Favorable for lower retail operational overhead)
    df['below_avg_retail_income'] = numpy.where(df['B24011_027E'] < national_avg_retail_income, 1, 0)
    
    # Aggregate Decision Metric: Summing the binary scores to build a prioritization index (0 to 6 scale)
    # Higher scores represent high-priority expansion targets (High Demand, Low Penetration, Favorable Costs, Low Competitive Dominance).
    df['action_logic'] = (
        df['avobe_avrg_targ_pop'] + 
        df['avobe_avrg_targ_pop_pct'] + 
        df['avobe_avrg_income'] + 
        df['below_median_no_stores'] + 
        df['below_avg_retail_income'] + 
        df['not_competitor_dominated']
    )

    # Data Schema Cleanup: Rename cryptic Census API codes to business-friendly labels for stakeholder readability
    df = df.rename(columns={
        'B19013_001E': 'state_median_income',
        'B24011_027E': 'median_income_retail',
        'NAME': 'state_name'
    })

    # =========================================================================
    # 6. Final Export & Summary Reporting
    # =========================================================================
    # Filter for key performance indicators (KPIs) relevant to the executive expansion strategy team
    final_cols = [
        'state_name', 'state_target_pop', 'target_pop_pct', 'state_median_income', 'median_income_retail', 'no_stores', 'action_logic'
    ]
    # Export clean analytical dataset to CSV for Tableau/PowerBI dashboard ingestion
    df[final_cols].to_csv("footlocker_market_analysis.csv", index=False)
    
    # Print high-level metrics for quick stakeholder review
    print("\n--- NATIONAL SUMMARY ---")
    print(f"Total US Population (18-34): {national_total_target_pop:,.0f}")
    print(f"National Avg Income: ${national_avg_income:,.2f}")
    print(f"National Avg Retail Income: ${national_avg_retail_income:,.2f}")
    print(f"Median number of stores per state: {median_stores:,.0f}")
    print("-" * 25)
    # Output the ranked matrix to instantly highlight the best expansion opportunities at the top
    print(df[final_cols].sort_values(by='action_logic', ascending=False))

if __name__ == "__main__":
    fetch_expansion_analysis()
