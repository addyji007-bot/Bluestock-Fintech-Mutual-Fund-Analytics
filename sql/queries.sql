-- ============================================================
-- Bluestock Mutual Fund Analytics - Analytical Queries
-- ============================================================

-- 1. Top 5 funds by AUM
SELECT 
    f.scheme_name,
    f.fund_house,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month (across all schemes)
SELECT 
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- 3. SIP YoY growth (total SIP amount by year)
SELECT 
    d.year,
    COUNT(*) AS sip_count,
    ROUND(SUM(t.amount_inr), 2) AS total_sip_amount
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
WHERE t.transaction_type = 'SIP'
GROUP BY d.year
ORDER BY d.year;

-- 4. Transactions by state (top 10)
SELECT 
    state,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount_inr), 2) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC
LIMIT 10;

-- 5. Funds with expense_ratio < 1%
SELECT 
    f.scheme_name,
    f.fund_house,
    f.plan,
    p.expense_ratio_pct,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct;

-- 6. Top 5 funds by 3-year return
SELECT 
    f.scheme_name,
    f.category,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS excess_return
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 5;

-- 7. SIP vs Lumpsum vs Redemption summary
SELECT 
    transaction_type,
    COUNT(*) AS txn_count,
    ROUND(SUM(amount_inr), 2) AS total_amount,
    ROUND(AVG(amount_inr), 2) AS avg_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount DESC;

-- 8. KYC status distribution
SELECT 
    kyc_status,
    COUNT(*) AS investor_txns,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_transactions), 2) AS pct
FROM fact_transactions
GROUP BY kyc_status;

-- 9. Average NAV of Large Cap funds (latest available date)
SELECT 
    f.scheme_name,
    f.fund_house,
    n.nav AS latest_nav,
    d.full_date
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date_id = d.date_id
WHERE f.sub_category = 'Large Cap'
  AND n.date_id = (SELECT MAX(date_id) FROM fact_nav)
ORDER BY n.nav DESC;

-- 10. Risk-adjusted performance (Sharpe ratio ranking)
SELECT 
    f.scheme_name,
    f.category,
    p.sharpe_ratio,
    p.return_3yr_pct,
    p.std_dev_ann_pct,
    p.risk_grade
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 10;