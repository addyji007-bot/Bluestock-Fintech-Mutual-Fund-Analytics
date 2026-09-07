import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

print("Cleaning nav_history.csv")
print("-" * 50)

#Load 
df = pd.read_csv("data/raw/02_nav_history.csv")
print("Original shape ; " ,df.shape)
print("Columns: ", df.columns.to_list())

# Lowercase the col names
df.columns = [c.strip().lower() for c in df.columns]

# Parse date
date_col = None
for col in ["date", "nav_date", "as_on"]:
    if col in df.columns:
        date_col = col
        break

if date_col is None:
    raise ValueError("No date column found")

df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

# Identify NAV column
nav_col = None
for col in ["nav", "net_asset_value", "nav_value"]:
    if col in df.columns:
        nav_col = col
        break

if nav_col is None:
    raise ValueError("No NAV column found")

# Convert NAV to numeric
df[nav_col] = pd.to_numeric(df[nav_col], errors="coerce")

# Sort
df = df.sort_values(["amfi_code", date_col]).reset_index(drop=True)

# Forward-fill missing NAV within each scheme
df[nav_col] = df.groupby("amfi_code")[nav_col].ffill()

# Remove remaining nulls (if any scheme starts with null)
df = df.dropna(subset=[nav_col, date_col])

# Remove duplicates
before = len(df)
df = df.drop_duplicates(subset=["amfi_code", date_col], keep="last")
print(f"Duplicates removed: {before - len(df)}")

# Validate NAV > 0
invalid = df[df[nav_col] <= 0]
print(f"Records with NAV <= 0: {len(invalid)}")
df = df[df[nav_col] > 0]

print(f"Final shape: {df.shape}")
print(f"Date range: {df[date_col].min()} to {df[date_col].max()}")
print(f"Unique schemes: {df['amfi_code'].nunique()}")

# Save
output_path = "data/processed/nav_history_cleaned.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")

