import pandas as pd

print("AMFI Code Validation & Data Quality Summary")
print("-" * 60)

# Load datasets
fund_master = pd.read_csv("data/raw/01_fund_master.csv")
nav_history = pd.read_csv("data/raw/02_nav_history.csv")

print(f"\nFund Master shape: {fund_master.shape}")
print(f"NAV History shape: {nav_history.shape}")

# Identify code columns
fm_code_col = "amfi_code"
nav_code_col = None
for col in ["amfi_code", "scheme_code", "code", "Scheme Code"]:
    if col in nav_history.columns:
        nav_code_col = col
        break

if nav_code_col is None:
    print("\nCould not find scheme code column in nav_history.")
    print("Available columns in nav_history:", nav_history.columns.tolist())
else:
    print(f"\nUsing code column in nav_history: '{nav_code_col}'")

    # Unique codes
    fm_codes = set(fund_master[fm_code_col].dropna().astype(int))
    nav_codes = set(nav_history[nav_code_col].dropna().astype(int))

    print(f"Unique codes in fund_master : {len(fm_codes)}")
    print(f"Unique codes in nav_history : {len(nav_codes)}")

    # Validation
    missing_in_nav = fm_codes - nav_codes
    extra_in_nav = nav_codes - fm_codes

    print(f"\nCodes present in fund_master but missing in nav_history: {len(missing_in_nav)}")
    if missing_in_nav:
        print(sorted(list(missing_in_nav)))

    print(f"Codes present in nav_history but not in fund_master: {len(extra_in_nav)}")

    # Data quality summary
    print("\n" + "-" * 60)
    print("DATA QUALITY SUMMARY")
    print("-" * 60)

    print(f"\n1. Fund Master")
    print(f"   - Total schemes          : {len(fund_master)}")
    print(f"   - Unique fund houses     : {fund_master['fund_house'].nunique()}")
    print(f"   - Missing values         : {fund_master.isnull().sum().sum()}")
    print(f"   - Duplicate rows         : {fund_master.duplicated().sum()}")

    print(f"\n2. NAV History")
    print(f"   - Total records          : {len(nav_history)}")
    print(f"   - Unique schemes         : {nav_history[nav_code_col].nunique()}")
    print(f"   - Missing values         : {nav_history.isnull().sum().sum()}")
    print(f"   - Duplicate rows         : {nav_history.duplicated().sum()}")

    if len(missing_in_nav) == 0:
        print("\nValidation Result: All AMFI codes in fund_master exist in nav_history.")
    else:
        print(f"\nValidation Result: {len(missing_in_nav)} codes from fund_master are missing in nav_history.")