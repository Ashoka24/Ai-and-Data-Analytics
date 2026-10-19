-- Run after: python scripts/run_analysis.py
-- Database: outputs/sales_analysis.db
-- Revenue is net of discount; profit = revenue - cost.

-- 1. Overall performance
SELECT
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS net_revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND(100.0 * SUM(profit) / NULLIF(SUM(revenue), 0), 2) AS profit_margin_pct
FROM sales;

-- 2. Monthly trend
SELECT month,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 2) AS revenue,
       ROUND(SUM(profit), 2) AS profit
FROM sales
GROUP BY month
ORDER BY month;

-- 3. Regional performance
SELECT region,
       ROUND(SUM(revenue), 2) AS revenue,
       ROUND(SUM(profit), 2) AS profit,
       ROUND(100.0 * SUM(profit) / NULLIF(SUM(revenue), 0), 2) AS margin_pct
FROM sales
GROUP BY region
ORDER BY profit DESC;

-- 4. Product performance: distinguish sales volume from profitability
SELECT product, category,
       SUM(quantity) AS units_sold,
       ROUND(SUM(revenue), 2) AS revenue,
       ROUND(SUM(profit), 2) AS profit
FROM sales
GROUP BY product, category
ORDER BY profit DESC;

-- 5. Discount bands and profitability
SELECT
    CASE
        WHEN discount_pct = 0 THEN '0%'
        WHEN discount_pct <= 0.05 THEN '1-5%'
        WHEN discount_pct <= 0.10 THEN '6-10%'
        WHEN discount_pct <= 0.15 THEN '11-15%'
        ELSE '16-20%'
    END AS discount_band,
    COUNT(*) AS order_lines,
    ROUND(AVG(profit_margin) * 100, 2) AS average_margin_pct,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit
FROM sales
GROUP BY discount_band
ORDER BY MIN(discount_pct);

-- 6. Sales channel and customer segment
SELECT channel, customer_segment,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 2) AS revenue,
       ROUND(SUM(profit), 2) AS profit
FROM sales
GROUP BY channel, customer_segment
ORDER BY revenue DESC;
