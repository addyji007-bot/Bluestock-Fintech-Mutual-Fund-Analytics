import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = "bluestock_mf.db"
SCHEMA_PATH = "sql/star_schema.sql"

print("Loading data into SQLite")
print("-" * 50)

# Remove old DB if exists (clean start)
if Path(DB_PATH).exists():
    Path(DB_PATH).unlink()
    print("Removed existing database")

# Create connection and execute schema
conn = sqlite3.connect(DB_PATH)
with open(SCHEMA_PATH, "r") as f:
    conn.executescript(f.read())
print("Schema created successfully")

# --------------------------------------------------
# 1. Load dim_fund from fund_master
# --------------------------------------------------
fm = pd.read_csv("data/raw/01_fund_master.csv")
fm.columns = [c.strip().lower() for c in fm.columns]

dim_fund = fm[[
    "amfi_code", "scheme_name", "fund_house", "category", "sub_category",
    "plan", "risk_category", "sebi_category_code", "benchmark",
    "expense_ratio_pct", "launch_date", "fund_manager"
]].copy()

dim_fund.to_sql("dim_fund", conn, if_exists="append", index=False)
print(f"dim_fund loaded: {len(dim_fund)} rows")

# --------------------------------------------------
# 2. Build and load dim_date
# --------------------------------------------------
nav = pd.read_csv("data/processed/nav_history_cleaned.csv")
nav["date"] = pd.to_datetime(nav["date"])

txn = pd.read_csv("data/processed/investor_transactions_cleaned.csv")
txn["transaction_date"] = pd.to_datetime(txn["transaction_date"])

all_dates = pd.concat([
    nav["date"],
    txn["transaction_date"]
]).drop_duplicates().sort_values().reset_index(drop=True)

dim_date = pd.DataFrame({"full_date": all_dates})
dim_date["date_id"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["full_date"].dt.year
dim_date["month"] = dim_date["full_date"].dt.month
dim_date["month_name"] = dim_date["full_date"].dt.strftime("%B")
dim_date["quarter"] = dim_date["full_date"].dt.quarter
dim_date["day_of_week"] = dim_date["full_date"].dt.dayofweek
dim_date["day_name"] = dim_date["full_date"].dt.strftime("%A")
dim_date["is_weekend"] = dim_date["day_of_week"].isin([5, 6]).astype(int)
dim_date["full_date"] = dim_date["full_date"].dt.strftime("%Y-%m-%d")

dim_date = dim_date[[
    "date_id", "full_date", "year", "month", "month_name",
    "quarter", "day_of_week", "day_name", "is_weekend"
]]

dim_date.to_sql("dim_date", conn, if_exists="append", index=False)
print(f"dim_date loaded: {len(dim_date)} rows")

# --------------------------------------------------
# 3. Load fact_nav
# --------------------------------------------------
nav["date_id"] = nav["date"].dt.strftime("%Y%m%d").astype(int)
fact_nav = nav[["amfi_code", "date_id", "nav"]].copy()
fact_nav.to_sql("fact_nav", conn, if_exists="append", index=False)
print(f"fact_nav loaded: {len(fact_nav)} rows")

# --------------------------------------------------
# 4. Load fact_transactions
# --------------------------------------------------
txn["date_id"] = txn["transaction_date"].dt.strftime("%Y%m%d").astype(int)
fact_txn = txn[[
    "investor_id", "amfi_code", "date_id", "transaction_type", "amount_inr",
    "state", "city", "city_tier", "age_group", "gender",
    "annual_income_lakh", "payment_mode", "kyc_status"
]].copy()
fact_txn.to_sql("fact_transactions", conn, if_exists="append", index=False)
print(f"fact_transactions loaded: {len(fact_txn)} rows")

# --------------------------------------------------
# 5. Load fact_performance
# --------------------------------------------------
perf = pd.read_csv("data/processed/scheme_performance_cleaned.csv")
perf.columns = [c.strip().lower() for c in perf.columns]

fact_perf = perf[[
    "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
    "std_dev_ann_pct", "max_drawdown_pct", "aum_crore", "expense_ratio_pct",
    "morningstar_rating", "risk_grade"
]].copy()
fact_perf.to_sql("fact_performance", conn, if_exists="append", index=False)
print(f"fact_performance loaded: {len(fact_perf)} rows")

# --------------------------------------------------
# Verification
# --------------------------------------------------
print("\n" + "-" * 50)
print("ROW COUNT VERIFICATION")
print("-" * 50)

tables = ["dim_fund", "dim_date", "fact_nav", "fact_transactions", "fact_performance"]
for t in tables:
    count = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM {t}", conn).iloc[0, 0]
    print(f"{t:25s}: {count:>8}")

conn.close()
print(f"\nDatabase saved as: {DB_PATH}")