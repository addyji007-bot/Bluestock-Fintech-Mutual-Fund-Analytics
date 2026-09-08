-- ============================================================
-- Bluestock Mutual Fund Analytics - SQLite Star Schema
-- ============================================================

-- Drop existing tables if re-running
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_date;

-- ------------------------------------------------------------
-- Dimension: Fund
-- ------------------------------------------------------------
CREATE TABLE dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    scheme_name         TEXT NOT NULL,
    fund_house          TEXT NOT NULL,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    launch_date         TEXT,
    fund_manager        TEXT
);

-- ------------------------------------------------------------
-- Dimension: Date
-- ------------------------------------------------------------
CREATE TABLE dim_date (
    date_id             INTEGER PRIMARY KEY,          -- YYYYMMDD
    full_date           TEXT NOT NULL,                -- YYYY-MM-DD
    year                INTEGER,
    month               INTEGER,
    month_name          TEXT,
    quarter             INTEGER,
    day_of_week         INTEGER,
    day_name            TEXT,
    is_weekend          INTEGER                       -- 0 or 1
);

-- ------------------------------------------------------------
-- Fact: NAV
-- ------------------------------------------------------------
CREATE TABLE fact_nav (
    nav_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL,
    date_id             INTEGER NOT NULL,
    nav                 REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

CREATE INDEX idx_fact_nav_amfi ON fact_nav(amfi_code);
CREATE INDEX idx_fact_nav_date ON fact_nav(date_id);

-- ------------------------------------------------------------
-- Fact: Transactions
-- ------------------------------------------------------------
CREATE TABLE fact_transactions (
    transaction_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT,
    amfi_code           INTEGER NOT NULL,
    date_id             INTEGER NOT NULL,
    transaction_type    TEXT NOT NULL,                -- SIP / Lumpsum / Redemption
    amount_inr          REAL NOT NULL,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

CREATE INDEX idx_fact_txn_amfi ON fact_transactions(amfi_code);
CREATE INDEX idx_fact_txn_date ON fact_transactions(date_id);
CREATE INDEX idx_fact_txn_type ON fact_transactions(transaction_type);

-- ------------------------------------------------------------
-- Fact: Performance
-- ------------------------------------------------------------
CREATE TABLE fact_performance (
    performance_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL UNIQUE,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           REAL,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- ------------------------------------------------------------
-- Fact: AUM (placeholder – will be populated if AUM data is cleaned later)
-- ------------------------------------------------------------
CREATE TABLE fact_aum (
    aum_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER,
    date_id             INTEGER,
    aum_crore           REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);