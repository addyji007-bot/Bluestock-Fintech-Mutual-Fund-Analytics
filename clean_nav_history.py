import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

print("Cleaning nav_history.csv")
print("-" * 50)

# Load
df = pd.read_csv("data/raw/02_nav_history.csv")
print(f"Original shape: {df.shape}")

# Standardise column names
df.columns = [c.strip().lower() for c in df.columns]

# Parse date (format is YYYY-MM-DD)
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")

# Ensure NAV is numeric
df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

# Sort by amfi_code + date
df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# Forward-fill missing NAV within each scheme (for any holiday gaps)
df["nav"] = df.groupby("amfi_code")["nav"].ffill()

# Drop any remaining nulls (should be very few or zero)
null_count = df[["date", "nav"]].isnull().any(axis=1).sum()
print(f"Rows with null date or nav after cleaning: {null_count}")
df = df.dropna(subset=["date", "nav"])

# Remove duplicates
before = len(df)
df = df.drop_duplicates(subset=["amfi_code", "date"], keep="last")
print(f"Duplicates removed: {before - len(df)}")

# Validate NAV > 0
invalid = (df["nav"] <= 0).sum()
print(f"Records with NAV <= 0: {invalid}")
df = df[df["nav"] > 0]

print(f"Final shape: {df.shape}")
print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"Unique schemes: {df['amfi_code'].nunique()}")

# Save
output_path = "data/processed/nav_history_cleaned.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")