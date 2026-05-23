import pandas as pd
import numpy as np
import os

def generate_financial_metrics():
    # =========================================================================
    # 1. Configuration & Source Tracking
    # =========================================================================
    # Expected core data source containing raw historical sales figures.
    source_file = 'sales_data.xlsx'

    # =========================================================================
    # 2. Resilient Data Loader (Automated Failover Pipeline)
    # =========================================================================
    # Building a defensive loading block. In multi-user cross-platform environments,
    # filenames often change case or format (.csv vs .xlsx). This prevents the pipeline
    # from breaking if a team member exports a different format.
    try:
        if os.path.exists(source_file):
            df = pd.read_excel(source_file)
        else:
            # Fallback regex-style scan to catch case-insensitive local variants
            all_files = os.listdir('.')
            csv_matches = [f for f in all_files if 'sales_data' in f.lower() and f.endswith('.csv')]
            if csv_matches:
                print(f"Exact file '{source_file}' not found. Loading matched file: '{csv_matches[0]}'")
                df = pd.read_csv(csv_matches[0])
            else:
                raise FileNotFoundError(f"Could not find '{source_file}' or any matching sales data CSV in this directory.")
                
    except Exception as e:
        # Diagnostic logging block: If data load fails entirely, provide immediate 
        # pathing context to speed up troubleshooting for senior team members.
        print(f"Error loading source file: {e}")
        print(f"Current Working Directory: {os.getcwd()}")
        print(f"Available CSV files: {[f for f in os.listdir('.') if f.endswith('.csv')]}")
        return

    # =========================================================================
    # 3. Macro Financial Hardcoding (External Assumptions Matrix)
    # =========================================================================
    # Mapping historical Gross Margin percentages (Revenue minus COGS / Revenue).
    # TREND NOTE: Tracking the 2021 surge helps contextualize normal retail baseline vs 
    # abnormal macro-economic anomalies (e.g., direct-to-consumer demand spikes).
    gross_margin_matrix = {
        2024: 0.2850,  # 28.50%
        2023: 0.2780,  # 27.80%
        2022: 0.3120,  # 31.20%
        2021: 0.3440,  # 34.40% (Peak post-lockdown hype boom)
        2020: 0.2890,  # 28.90% (Pandemic retail disruption)
        2019: 0.3180   # 31.80% (Pre-pandemic benchmark)
    }
    
    # =========================================================================
    # 4. Brick-and-Mortar Operational Footprint Mapping
    # =========================================================================
    # Historical store counts used for standardizing fleet sizing and density.
    # Essential for calculating unit economics and sales productivity over time.
    store_count_matrix = {
        2024: 2400,
        2023: 2520,
        2022: 2714,
        2021: 2850,
        2020: 2998,
        2019: 3129
    }

    # =========================================================================
    # 5. Synthesize Income Statement Metrics (Corporate Finance Engine)
    # =========================================================================
    # Map raw coefficients out to percentage strings and calculate raw dollar impact
    df['Gross Margin (%)'] = df['Year'].map(gross_margin_matrix) * 100
    df['Gross Profit ($M)'] = (df['Total sales'] * (df['Gross Margin (%)'] / 100)).round(2)
    
    # Cost of Goods Sold (COGS) calculation for inventory turnover tracking
    df['Cost of Goods Sold ($M)'] = (df['Total sales'] - df['Gross Profit ($M)']).round(2)
    
    # EBIT (Operating Income) modeling by pulling down structural SG&A overhead costs
    df['Operating Income / EBIT ($M)'] = (df['Gross Profit ($M)'] - df['SG&A']).round(2)
    df['Operating Margin (%)'] = ((df['Operating Income / EBIT ($M)'] / df['Total sales']) * 100).round(2)
    
    # Capital Structure Assumption: Flat corporate interest deduction applied uniformly across cycles
    df['Interest Expense ($M)'] = 30.0
    df['Pretax Income ($M)'] = df['Operating Income / EBIT ($M)'] - df['Interest Expense ($M)']
    
    # Tax Liability Guard: Ensuring the corporation only incurs a 24% tax provision if Pretax Income is profitable.
    # Prevents calculating negative tax liabilities during net-loss operational periods.
    df['Tax Expense ($M)'] = np.where(df['Pretax Income ($M)'] > 0, (df['Pretax Income ($M)'] * 0.24).round(2), 0.0)
    
    # Final corporate net profitability line itemization
    df['Net Income ($M)'] = (df['Pretax Income ($M)'] - df['Tax Expense ($M)']).round(2)
    df['Net Margin (%)'] = ((df['Net Income ($M)'] / df['Total sales']) * 100).round(2)

    # =========================================================================
    # 6. Synthesize Operational Efficiency KPIs (Omnichannel Distribution)
    # =========================================================================
    df['Store Count'] = df['Year'].map(store_count_matrix)
    
    # Calculate localized real estate asset productivity
    df['Average Sales per Store ($M)'] = (df['Store sales'] / df['Store Count']).round(3)
    
    # E-commerce Penetration Rate: Tracks digital adoption velocity vs brick-and-mortar storefronts
    df['Digital Sales Share (%)'] = ((df['Direct-to-customer sales'] / df['Total sales']) * 100).round(2)
    
    # Sort chronologically so sequential visualization steps (e.g., line charts) map correctly over the time axis
    df = df.sort_values(by='Year', ascending=True).reset_index(drop=True)

    # =========================================================================
    # 7. Data Pipeline Export & Downstream Reporting
    # =========================================================================
    output_filename = "footlocker_extended_metrics.csv"
    df.to_csv(output_filename, index=False)
    print(f"\n[Success] Expanded performance profile written to '{output_filename}'\n")
    
    # =========================================================================
    # 8. Executive Performance Reporting Table
    # =========================================================================
    # Formatted terminal display utilizing explicit column widths to match accounting design standards.
    # Currency values are explicitly format-mapped with thousands separators for crisp corporate presentations.
    print("=" * 115)
    print(f"{'YEAR':<6} | {'TOTAL SALES ($M)':<16} | {'GROSS MARGIN':<12} | {'EBIT ($M)':<10} | {'NET INCOME ($M)':<15} | {'STORE COUNT':<11} | {'DIGITAL %':<9}")
    print("=" * 115)
    for _, row in df.iterrows():
        print(f"{int(row['Year']):<6} | ${row['Total sales']:<15,.2f} | {row['Gross Margin (%)']:>10.2f}% | ${row['Operating Income / EBIT ($M)']:<9,.2f} | ${row['Net Income ($M)']:<14,.2f} | {int(row['Store Count']):<11} | {row['Digital Sales Share (%)']:>8.2f}%")
    print("=" * 115)

if __name__ == "__main__":
    generate_financial_metrics()