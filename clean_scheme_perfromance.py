import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

print("Cleaning scheme_performance.csv")
print("-" * 50)

df = pd.read_csv("data/raw/07_scheme_performance.csv")
print(f"Original shape: {df.shape}")

# Standardise column names
df.columns = [c.strip().lower() for c in df.columns]

# Ensure numeric columns are numeric
numeric_cols = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
    "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
    "aum_crore", "expense_ratio_pct", "morningstar_rating"
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Check expense_ratio range (0.1% – 2.5%)
out_of_range = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
print(f"Expense ratio outside 0.1–2.5: {len(out_of_range)}")
if len(out_of_range) > 0:
    print(out_of_range[["amfi_code", "scheme_name", "expense_ratio_pct"]])

# Flag extreme returns (optional anomaly check)
extreme_returns = df[
    (df["return_1yr_pct"].abs() > 50) |
    (df["return_3yr_pct"].abs() > 50) |
    (df["return_5yr_pct"].abs() > 50)
]
print(f"Extreme return values (>|50%|): {len(extreme_returns)}")

# Remove any rows that became fully null in critical columns
df = df.dropna(subset=["amfi_code", "expense_ratio_pct"])

# Remove duplicates
before = len(df)
df = df.drop_duplicates(subset=["amfi_code"], keep="last")
print(f"Duplicates removed: {before - len(df)}")

print(f"\nFinal shape: {df.shape}")
print(f"Expense ratio range: {df['expense_ratio_pct'].min():.2f}% – {df['expense_ratio_pct'].max():.2f}%")

# Save
output_path = "data/processed/scheme_performance_cleaned.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")