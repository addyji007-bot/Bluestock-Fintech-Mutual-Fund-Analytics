import pandas as pd
import numpy as np

print("Building Fund Scorecard (0-100)")
print("-" * 50)

# Load all metrics
cagr = pd.read_csv("data/processed/cagr_comparison.csv")
sharpe = pd.read_csv("data/processed/sharpe_ratio.csv")
alpha = pd.read_csv("data/processed/alpha_beta.csv")
dd = pd.read_csv("data/processed/max_drawdown.csv")
perf = pd.read_csv("data/processed/scheme_performance_cleaned.csv")
perf.columns = [c.strip().lower() for c in perf.columns]

# Merge
df = cagr[["amfi_code", "scheme_name", "cagr_3yr"]].copy()
df = df.merge(sharpe[["amfi_code", "sharpe_ratio"]], on="amfi_code", how="left")
df = df.merge(alpha[["amfi_code", "alpha_annual"]], on="amfi_code", how="left")
df = df.merge(dd[["amfi_code", "max_drawdown_pct"]], on="amfi_code", how="left")
df = df.merge(perf[["amfi_code", "expense_ratio_pct"]], on="amfi_code", how="left")

# Rank (higher better for return, sharpe, alpha)
df["rank_cagr"] = df["cagr_3yr"].rank(ascending=False, method="min")
df["rank_sharpe"] = df["sharpe_ratio"].rank(ascending=False, method="min")
df["rank_alpha"] = df["alpha_annual"].rank(ascending=False, method="min")

# Inverse ranks (lower expense and less negative DD are better)
df["rank_expense"] = df["expense_ratio_pct"].rank(ascending=True, method="min")  # low expense = better rank
df["rank_dd"] = df["max_drawdown_pct"].rank(ascending=False, method="min")       # less negative = better

n = len(df)

# Convert ranks to 0-100 scores (best rank = 100)
df["score_cagr"] = (n - df["rank_cagr"] + 1) / n * 100
df["score_sharpe"] = (n - df["rank_sharpe"] + 1) / n * 100
df["score_alpha"] = (n - df["rank_alpha"] + 1) / n * 100
df["score_expense"] = (n - df["rank_expense"] + 1) / n * 100
df["score_dd"] = (n - df["rank_dd"] + 1) / n * 100

# Composite
df["fund_score"] = (
    0.30 * df["score_cagr"] +
    0.25 * df["score_sharpe"] +
    0.20 * df["score_alpha"] +
    0.15 * df["score_expense"] +
    0.10 * df["score_dd"]
).round(2)

df = df.sort_values("fund_score", ascending=False).reset_index(drop=True)
df["rank"] = range(1, len(df) + 1)

cols = ["rank", "amfi_code", "scheme_name", "fund_score",
        "cagr_3yr", "sharpe_ratio", "alpha_annual",
        "expense_ratio_pct", "max_drawdown_pct"]

print(df[cols].to_string())
print(f"\nTotal funds scored: {len(df)}")

df.to_csv("data/processed/fund_scorecard.csv", index=False)
print("\nSaved to: data/processed/fund_scorecard.csv")