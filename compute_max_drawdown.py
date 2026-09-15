import pandas as pd
import numpy as np

print("Computing Maximum Drawdown")
print("-" * 50)

nav = pd.read_csv("data/processed/nav_history_cleaned.csv")
nav["date"] = pd.to_datetime(nav["date"])
nav = nav.sort_values(["amfi_code", "date"])

fm = pd.read_csv("data/raw/01_fund_master.csv")
fm.columns = [c.strip().lower() for c in fm.columns]
name_map = dict(zip(fm["amfi_code"], fm["scheme_name"]))

results = []

for code, group in nav.groupby("amfi_code"):
    group = group.sort_values("date").reset_index(drop=True)
    group["running_max"] = group["nav"].cummax()
    group["drawdown"] = group["nav"] / group["running_max"] - 1

    max_dd = group["drawdown"].min()
    dd_row = group.loc[group["drawdown"].idxmin()]

    # Find the peak date (last time running_max was updated before the trough)
    peak_date = group.loc[group["date"] <= dd_row["date"], "date"].iloc[
        group.loc[group["date"] <= dd_row["date"], "nav"].idxmax()
        if False else group[group["date"] <= dd_row["date"]]["nav"].idxmax()
    ]  # simplified below

    # Cleaner way
    trough_idx = group["drawdown"].idxmin()
    peak_idx = group.loc[:trough_idx, "nav"].idxmax()

    results.append({
        "amfi_code": code,
        "scheme_name": name_map.get(code, "Unknown"),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "peak_date": group.loc[peak_idx, "date"].date(),
        "trough_date": group.loc[trough_idx, "date"].date(),
        "peak_nav": round(group.loc[peak_idx, "nav"], 4),
        "trough_nav": round(group.loc[trough_idx, "nav"], 4)
    })

dd_df = pd.DataFrame(results)
dd_df = dd_df.sort_values("max_drawdown_pct").reset_index(drop=True)  # most negative first

print(dd_df.to_string())
print(f"\nTotal schemes: {len(dd_df)}")

dd_df.to_csv("data/processed/max_drawdown.csv", index=False)
print("\nSaved to: data/processed/max_drawdown.csv")