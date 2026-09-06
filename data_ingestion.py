import pandas as pd
import os

# Path to raw data
RAW_DATA_PATH = "data/raw"

# List of all 10 CSV files
csv_files = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv"
]

print("=" * 100)
print("DAY 1 - DATA INGESTION: Loading all 10 CSV datasets")
print("=" * 100)

# Dictionary to store dataframes
dataframes = {}

for file in csv_files:
    file_path = os.path.join(RAW_DATA_PATH, file)
    
      
    try:
        df = pd.read_csv(file_path)
        dataframes[file] = df
        
        print(f"\nShape: {df.shape}")
        print(f"\nData Types:\n{df.dtypes}")
        print(f"\nFirst 5 rows:\n{df.head()}")
        
        # Quick anomaly checks
        print(f"\n--- Quick Checks ---")
        print(f"Missing values (total): {df.isnull().sum().sum()}")
        print(f"Duplicate rows: {df.duplicated().sum()}")
        
    except Exception as e:
        print(f"Error loading {file}: {e}")

print("\n" + "=" * 100)
print("All files processed")
print("=" * 100)