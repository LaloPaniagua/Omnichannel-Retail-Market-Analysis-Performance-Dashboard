<h1>Omnichannel Retail Market Analysis & Performance Dashboard</h1>

<img width="1024" height="575" alt="image" src="https://github.com/user-attachments/assets/932b7559-3d64-48af-911e-ebd9b0a22167" />


<h2>Project Overview</h2>

This project integrates internal sales data, competitor locations, and U.S. Census Bureau API demographic data to evaluate Foot Locker’s historical performance (2019–2024) and identify optimal states for future retail expansion. The clean, automated Python pipeline processes raw multi-source data into clean, structured tables that feed an executive-facing business intelligence dashboard.


<h2>Key Core Insights Delivered</h2>

<h3>Expansion Priority Index:</h3> Engineered a custom 0-to-6 scoring matrix based on local purchasing power, density of the 18–34 target demographic, and under-penetration of our current footprint.

<h3>Omnichannel Tracking:</h3> Calculated that digital sales hold an 18.24% share of total revenue, mapping the shift toward direct-to-consumer models.

<h3>Risk Mitigation:</h3> Isolated local market leaders (e.g., Hibbett Sports, Scheels) to prevent expanding into highly saturated competitive territories.


<h2>Technical Pipeline Architecture</h2>

The data pipeline consists of three modular scripts built with Python (Pandas, NumPy, OS, Statistics) and the Census Bureau API wrapper:

<img width="1012" height="77" alt="image" src="https://github.com/user-attachments/assets/2b05b74a-2677-4362-89c5-805a3537e639" />

Competitor Classifier (competitorComparison.py): Uses vectorized array indexing (.idxmax()) to dynamically tag the top regional competitor per state while isolating non-numeric fields.

Financial Metrics Synthesizer (financial_metrics_app.py): Models corporate income statements, utilizing conditional masking (np.where) for tax liabilities to prevent logical errors during net-loss periods. Includes a defensive failover loading sequence to handle varied local file paths.

Census Data Ingestion Engine (expansion_analysis_app.py): Aggregate 12 distinct age/gender API vectors to construct our target audience profile. Standardizes regional tracking using padded state FIPS string conversions (.zfill(2)).

<h2>Tech Stack</h2>


* Data Engineering: Python (Pandas, NumPy)

* API Extraction: Census Bureau ACS 5-Year API

* Business Intelligence: PowerBI
