import pandas as pd
import numpy as np

print("Computing Sortino Ratio (Rf = 6.5%)")
print("-" * 50)

dr = pd.read_csv("data/processed/daily_returns.csv")
dr["date"] = pd.to_datetime(dr["date"])

fm = pd.read_csv("data/raw/01_fund_master.csv")
fm.columns = [c.strip().lower() for c in fm.columns]
name_map = dict(zip(fm["amfi_code"], fm["scheme_name"]))

RF_ANNUAL = 0.065

results = []

for code, group in dr.groupby("amfi_code"):
    rets = group["daily_return"].dropna()
    if len(rets) < 30:
        continue

    mean_daily = rets.mean()
    rp_annual = mean_daily * 252

    # Downside deviation: only negative returns
    downside = rets[rets < 0]
    if len(downside) == 0:
        downside_std_annual = 0.0
    else:
        downside_std_annual = downside.std() * np.sqrt(252)

    sortino = (rp_annual - RF_ANNUAL) / downside_std_annual if downside_std_annual > 0 else np.nan

    results.append({
        "amfi_code": code,
        "scheme_name": name_map.get(code, "Unknown"),
        "ann_return_pct": round(rp_annual * 100, 2),
        "downside_std_pct": round(downside_std_annual * 100, 2),
        "sortino_ratio": round(sortino, 3)
    })

sortino_df = pd.DataFrame(results)
sortino_df = sortino_df.sort_values("sortino_ratio", ascending=False).reset_index(drop=True)

print(sortino_df.to_string())
print(f"\nTotal schemes ranked: {len(sortino_df)}")

sortino_df.to_csv("data/processed/sortino_ratio.csv", index=False)
print("\nSaved to: data/processed/sortino_ratio.csv")