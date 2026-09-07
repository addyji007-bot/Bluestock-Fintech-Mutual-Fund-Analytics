import pandas as pd

# Load fund master
df = pd.read_csv("data/raw/01_fund_master.csv")

print("Fund Master Exploration")
print("-" * 60)

print(f"\nShape: {df.shape}")
print(f"\nColumns:\n{df.columns.tolist()}")

print("\nUnique Fund Houses:")
print(df['fund_house'].nunique() if 'fund_house' in df.columns else "Column 'fund_house' not found")
if 'fund_house' in df.columns:
    print(df['fund_house'].unique()[:20])  # first 20

print("\nUnique Categories:")
if 'category' in df.columns:
    print(df['category'].value_counts())
elif 'scheme_category' in df.columns:
    print(df['scheme_category'].value_counts())
else:
    print("Category column not found. Available columns:", df.columns.tolist())

print("\nUnique Sub-categories (if available):")
if 'sub_category' in df.columns:
    print(df['sub_category'].value_counts())
else:
    print("No sub_category column")

print("\nRisk Grades (if available):")
if 'risk' in df.columns:
    print(df['risk'].value_counts())
elif 'risk_grade' in df.columns:
    print(df['risk_grade'].value_counts())
else:
    print("No risk column found")

print("\nSample of scheme codes (AMFI codes):")
code_col = None
for col in ['scheme_code', 'amfi_code', 'code', 'Scheme Code']:
    if col in df.columns:
        code_col = col
        break

if code_col:
    print(df[code_col].head(10).tolist())
    print(f"\nTotal unique scheme codes: {df[code_col].nunique()}")
else:
    print("Scheme code column not found")