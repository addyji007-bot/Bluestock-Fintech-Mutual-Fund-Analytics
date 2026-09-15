import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("reports", exist_ok=True)

print("Benchmark Comparison Chart + Tracking Error")
print("-" * 50)

# Top 5 from scorecard
top5_codes = [148567, 120505, 120843, 100033, 120504]

# Load data
nav = pd.read_csv("data/processed/nav_history_cleaned.csv")
nav["date"] = pd.to_datetime(nav["date"])

bench = pd.read_csv("data/raw/10_benchmark_indices.csv")
bench["date"] = pd.to_datetime(bench["date"])

fm = pd.read_csv("data/raw/01_fund_master.csv")
fm.columns = [c.strip().lower() for c in fm.columns]
name_map = dict(zip(fm["amfi_code"], fm["scheme_name"]))

# Filter last ~3 years
cutoff = nav["date"].max() - pd.DateOffset(years=3)
nav = nav[nav["date"] >= cutoff]
bench = bench[bench["date"] >= cutoff]

# Prepare Nifty 50 and Nifty 100 (normalised to 100)
nifty50 = bench[bench["index_name"] == "NIFTY50"][["date", "close_value"]].copy()
nifty100 = bench[bench["index_name"] == "NIFTY100"][["date", "close_value"]].copy()

nifty50 = nifty50.sort_values("date")
nifty100 = nifty100.sort_values("date")
nifty50["norm"] = nifty50["close_value"] / nifty50["close_value"].iloc[0] * 100
nifty100["norm"] = nifty100["close_value"] / nifty100["close_value"].iloc[0] * 100

# Plot
plt.figure(figsize=(14, 7))
plt.plot(nifty50["date"], nifty50["norm"], label="Nifty 50", linewidth=2, linestyle="--", color="black")
plt.plot(nifty100["date"], nifty100["norm"], label="Nifty 100", linewidth=2, linestyle="--", color="gray")

tracking_errors = []

for code in top5_codes:
    fund = nav[nav["amfi_code"] == code][["date", "nav"]].sort_values("date")
    if len(fund) < 10:
        continue
    fund["norm"] = fund["nav"] / fund["nav"].iloc[0] * 100
    name = name_map.get(code, str(code))[:40]
    plt.plot(fund["date"], fund["norm"], label=name, linewidth=1.5)

    # Tracking error vs Nifty 100
    fund_ret = fund.set_index("date")["nav"].pct_change().dropna()
    bench_ret = nifty100.set_index("date")["close_value"].pct_change().dropna()
    common = fund_ret.index.intersection(bench_ret.index)
    if len(common) > 30:
        excess = fund_ret.loc[common] - bench_ret.loc[common]
        te = excess.std() * np.sqrt(252) * 100
        tracking_errors.append({"amfi_code": code, "scheme_name": name, "tracking_error_pct": round(te, 2)})

plt.title("Top 5 Funds vs Nifty 50 & Nifty 100 (Normalised to 100)", fontsize=14)
plt.xlabel("Date")
plt.ylabel("Normalised Value (Start = 100)")
plt.legend(loc="upper left", fontsize=8)
plt.grid(True, alpha=0.3)
plt.tight_layout()

chart_path = "reports/benchmark_comparison.png"
plt.savefig(chart_path, dpi=150)
plt.close()
print(f"Chart saved to: {chart_path}")

te_df = pd.DataFrame(tracking_errors)
print("\nTracking Error vs Nifty 100 (annualised %):")
print(te_df.to_string(index=False))
te_df.to_csv("data/processed/tracking_error.csv", index=False)
print("\nSaved tracking_error.csv")