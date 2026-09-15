import pandas as pd
import numpy as np
from scipy.stats import linregress

print("Computing Alpha & Beta vs Nifty 100")
print("-" * 50)

# Fund daily returns
dr = pd.read_csv("data/processed/daily_returns.csv")
dr["date"] = pd.to_datetime(dr["date"])

# Benchmark
bench = pd.read_csv("data/raw/10_benchmark_indices.csv")
bench["date"] = pd.to_datetime(bench["date"])
nifty100 = bench[bench["index_name"] == "NIFTY100"].copy()
nifty100 = nifty100.sort_values("date")
nifty100["bench_return"] = nifty100["close_value"].pct_change()
nifty100 = nifty100.dropna(subset=["bench_return"])

# Fund names
fm = pd.read_csv("data/raw/01_fund_master.csv")
fm.columns = [c.strip().lower() for c in fm.columns]
name_map = dict(zip(fm["amfi_code"], fm["scheme_name"]))

results = []

for code, group in dr.groupby("amfi_code"):
    merged = pd.merge(
        group[["date", "daily_return"]],
        nifty100[["date", "bench_return"]],
        on="date",
        how="inner"
    ).dropna()

    if len(merged) < 60:
        continue

    slope, intercept, r_value, p_value, std_err = linregress(
        merged["bench_return"], merged["daily_return"]
    )

    beta = slope
    alpha_daily = intercept
    alpha_annual = alpha_daily * 252  # annualised

    results.append({
        "amfi_code": code,
        "scheme_name": name_map.get(code, "Unknown"),
        "alpha_annual": round(alpha_annual * 100, 2),   # in %
        "beta": round(beta, 3),
        "r_squared": round(r_value ** 2, 3),
        "observations": len(merged)
    })

ab_df = pd.DataFrame(results)
ab_df = ab_df.sort_values("alpha_annual", ascending=False).reset_index(drop=True)

print(ab_df.to_string())
print(f"\nTotal schemes: {len(ab_df)}")

ab_df.to_csv("data/processed/alpha_beta.csv", index=False)
print("\nSaved to: data/processed/alpha_beta.csv")