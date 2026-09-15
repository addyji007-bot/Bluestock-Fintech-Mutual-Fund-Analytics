import pandas as pd
import numpy as np
from datetime import timedelta

print("Computing CAGR for 1yr, 3yr, 5yr")
print("-" * 50)

nav = pd.read_csv("data/processed/nav_history_cleaned.csv")
nav["date"] = pd.to_datetime(nav["date"])
nav = nav.sort_values(["amfi_code", "date"])

# Load fund names for readability
fm = pd.read_csv("data/raw/01_fund_master.csv")
fm.columns = [c.strip().lower() for c in fm.columns]
name_map = dict(zip(fm["amfi_code"], fm["scheme_name"]))

results = []

for code, group in nav.groupby("amfi_code"):
    group = group.sort_values("date").reset_index(drop=True)
    latest_date = group["date"].max()
    latest_nav = group.loc[group["date"] == latest_date, "nav"].values[0]

    row = {
        "amfi_code": code,
        "scheme_name": name_map.get(code, "Unknown"),
        "latest_date": latest_date.date(),
        "latest_nav": round(latest_nav, 4)
    }

    for years, label in [(1, "cagr_1yr"), (3, "cagr_3yr"), (5, "cagr_5yr")]:
        target_date = latest_date - timedelta(days=365 * years)
        # Find the closest available date on or before target
        past = group[group["date"] <= target_date]
        if len(past) == 0:
            row[label] = np.nan
            continue
        start_nav = past.iloc[-1]["nav"]
        start_date = past.iloc[-1]["date"]
        actual_years = (latest_date - start_date).days / 365.25
        if actual_years <= 0 or start_nav <= 0:
            row[label] = np.nan
        else:
            cagr = (latest_nav / start_nav) ** (1 / actual_years) - 1
            row[label] = round(cagr * 100, 2)  # in %

    results.append(row)

cagr_df = pd.DataFrame(results)
cagr_df = cagr_df.sort_values("cagr_3yr", ascending=False).reset_index(drop=True)

print(cagr_df[["amfi_code", "scheme_name", "cagr_1yr", "cagr_3yr", "cagr_5yr"]].to_string())
print(f"\nSchemes with valid 5yr CAGR: {cagr_df['cagr_5yr'].notna().sum()}")

cagr_df.to_csv("data/processed/cagr_comparison.csv", index=False)
print("\nSaved to: data/processed/cagr_comparison.csv")