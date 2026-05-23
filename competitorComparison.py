import pandas as pd

# =========================================================================
# 1. Data Ingestion
# =========================================================================
# Ingesting raw competitor footprint data. 
df = pd.read_csv('Retail Competitor Store Counts 2026.csv')

# =========================================================================
# 2. Schema Selection & Feature Isolation
# =========================================================================
# Explicitly isolating athletic retail competitors to keep non-numeric dimensions 
# (like 'State') from throwing off mathematical operations or aggregation logic.
store_columns = ['Foot Locker', 'Big 5 Sporting Goods', 'Nike Stores (Direct)', 'Scheels', 'Hibbett Sports']

# =========================================================================
# 3. Market Leader Identification (Feature Engineering)
# =========================================================================
# Utilizing .idxmax() to identify which retailer holds the largest physical footprint in each state.
#
# BUSINESS IMPLICATION: This establishes the "Market Leader" tag for each row, 
# helping the marketing and real estate teams identify which competitor we are battling for local dominance.
#
# EDGE CASE WARNING: If two competitors have an identical maximum store count, .idxmax() defaults to 
# the first column encountered. I should monitor ties in future data validation checks.
df['Most Popular Store'] = df[store_columns].idxmax(axis=1)

# =========================================================================
# 4. Data Pipeline Export & Downstream Readiness
# =========================================================================
# Exporting the enhanced dataset to an unindexed CSV.
# 
# DESIGN CHOICE: index=False prevents pandas from adding an unnamed auto-incremented primary key column.
# This keeps the schema clean and directly compatible with PowerBI / Tableau dashboard connections
# and prevents syntax errors in our Census API expansion script.
df.to_csv('Retail Competitor Store Counts 2026.csv', index=False)