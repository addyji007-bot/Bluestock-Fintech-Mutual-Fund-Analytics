import pandas as pd
import numpy as np

print("Computing Sharpe Ratio (Rf = 6.5%)")
print("-" * 50)

# Load daily returns
dr = pd.read_csv("data/processed/daily_returns.csv")
dr["date"] = pd.to_datetime(dr["date"])

# Load fund names
fm = pd.read_csv("data/raw/01_fund_master.csv")
fm.columns = [c.strip().lower() for c in fm.columns]
name_map = dict(zip(fm["amfi_code"], fm["scheme_name"]))

RF_ANNUAL = 0.065
RF_DAILY = RF_ANNUAL / 252

results = []

for code, group in dr.groupby("amfi_code"):
    rets = group["daily_return"].dropna()
    if len(rets) < 30:
        continue

    mean_daily = rets.mean()
    std_daily = rets.std()

    # Annualised
    rp_annual = mean_daily * 252
    std_annual = std_daily * np.sqrt(252)

    sharpe = (rp_annual - RF_ANNUAL) / std_annual if std_annual > 0 else np.nan

    results.append({
        "amfi_code": code,
        "scheme_name": name_map.get(code, "Unknown"),
        "ann_return_pct": round(rp_annual * 100, 2),
        "ann_std_pct": round(std_annual * 100, 2),
        "sharpe_ratio": round(sharpe, 3)
    })

sharpe_df = pd.DataFrame(results)
sharpe_df = sharpe_df.sort_values("sharpe_ratio", ascending=False).reset_index(drop=True)

print(sharpe_df.to_string())
print(f"\nTotal schemes ranked: {len(sharpe_df)}")

sharpe_df.to_csv("data/processed/sharpe_ratio.csv", index=False)
print("\nSaved to: data/processed/sharpe_ratio.csv")