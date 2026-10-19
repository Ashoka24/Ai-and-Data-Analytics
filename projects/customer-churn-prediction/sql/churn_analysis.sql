-- Descriptive churn summaries for the synthetic customer dataset.
-- Run from SQLite after loading data/customer_churn.csv into a table named customers.

-- Overall churn rate
SELECT COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS churn_rate_pct
FROM customers;

-- Contract type
SELECT contract, COUNT(*) AS customers,
       SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) AS churned,
       ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers GROUP BY contract ORDER BY churn_rate_pct DESC;

-- Tenure bands
SELECT CASE WHEN tenure_months < 6 THEN '0-5 months'
            WHEN tenure_months < 12 THEN '6-11 months'
            WHEN tenure_months < 24 THEN '12-23 months'
            WHEN tenure_months < 48 THEN '24-47 months'
            ELSE '48+ months' END AS tenure_band,
       COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers GROUP BY tenure_band ORDER BY MIN(tenure_months);

-- Support services
SELECT tech_support, online_security, COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers GROUP BY tech_support, online_security ORDER BY churn_rate_pct DESC;

-- Payment method
SELECT payment_method, COUNT(*) AS customers,
       ROUND(100.0 * AVG(CASE WHEN churn = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS churn_rate_pct
FROM customers GROUP BY payment_method ORDER BY churn_rate_pct DESC;
