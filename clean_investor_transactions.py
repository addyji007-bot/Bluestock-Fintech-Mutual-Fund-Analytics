import pandas as pd
import os

df = pd.read_csv("data/raw/08_investor_transactions.csv")
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head().to_string())
print("\nData types:")
print(df.dtypes)
print("\nMissing values:")
print(df.isnull().sum())
print("\nUnique transaction_type values:")
print(df["transaction_type"].value_counts() if "transaction_type" in df.columns else "column not found")
print("\nUnique KYC related columns (if any):")
for col in df.columns:
    if "kyc" in col.lower() or "status" in col.lower():
        print(col, "→", df[col].value_counts().to_dict())

os.makedirs("data/processed", exist_ok=True)

print("Cleaning investor_transactions.csv")
print("-" * 50)

df = pd.read_csv("data/raw/08_investor_transactions.csv")
print(f"Original shape: {df.shape}")

# Standardise column names
df.columns = [c.strip().lower() for c in df.columns]

# Parse date
df["transaction_date"] = pd.to_datetime(df["transaction_date"], format="%Y-%m-%d", errors="coerce")

# Ensure amount is numeric and > 0
df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
invalid_amount = (df["amount_inr"] <= 0).sum()
print(f"Records with amount <= 0: {invalid_amount}")
df = df[df["amount_inr"] > 0]

# Standardise transaction_type (already clean, but make consistent)
df["transaction_type"] = df["transaction_type"].str.strip().str.title()
# Map any variations if they appear later
type_map = {
    "Sip": "SIP",
    "Lumpsum": "Lumpsum",
    "Redemption": "Redemption"
}
df["transaction_type"] = df["transaction_type"].replace(type_map)

print("\nTransaction type distribution after cleaning:")
print(df["transaction_type"].value_counts())

# Validate KYC status
valid_kyc = {"Verified", "Pending"}
invalid_kyc = ~df["kyc_status"].isin(valid_kyc)
print(f"\nInvalid KYC status rows: {invalid_kyc.sum()}")
df = df[~invalid_kyc]

# Drop any remaining nulls in critical columns
df = df.dropna(subset=["transaction_date", "amfi_code", "amount_inr", "transaction_type"])

# Remove exact duplicates
before = len(df)
df = df.drop_duplicates()
print(f"Duplicates removed: {before - len(df)}")

print(f"\nFinal shape: {df.shape}")
print(f"Date range: {df['transaction_date'].min().date()} to {df['transaction_date'].max().date()}")

# Save
output_path = "data/processed/investor_transactions_cleaned.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved to: {output_path}")