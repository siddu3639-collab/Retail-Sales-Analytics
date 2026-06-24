-- ============================================================
-- business_queries.sql
-- Answers key business questions for the retail dashboard
-- ============================================================


-- ── 1. EXECUTIVE OVERVIEW ─────────────────────────────────
-- Total sales, profit, orders, margin
SELECT
    ROUND(SUM(o.sales), 2)                               AS total_sales,
    ROUND(SUM(o.profit), 2)                              AS total_profit,
    COUNT(DISTINCT o.order_id)                           AS total_orders,
    ROUND(SUM(o.profit) / NULLIF(SUM(o.sales), 0) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(o.sales), 2)                               AS avg_order_value
FROM Orders o;


-- ── 2. MONTHLY SALES TREND ────────────────────────────────
SELECT
    YEAR(order_date)                  AS year,
    MONTH(order_date)                 AS month,
    ROUND(SUM(sales), 2)              AS total_sales,
    ROUND(SUM(profit), 2)             AS total_profit,
    COUNT(DISTINCT order_id)          AS order_count
FROM Orders
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY year, month;

-- PostgreSQL version (comment above, uncomment below):
-- SELECT
--     EXTRACT(YEAR  FROM order_date)::INT AS year,
--     EXTRACT(MONTH FROM order_date)::INT AS month,
--     ROUND(SUM(sales)::NUMERIC, 2)       AS total_sales,
--     ROUND(SUM(profit)::NUMERIC, 2)      AS total_profit,
--     COUNT(DISTINCT order_id)            AS order_count
-- FROM Orders
-- GROUP BY 1, 2 ORDER BY 1, 2;


-- ── 3. REGIONAL PERFORMANCE ───────────────────────────────
SELECT
    c.region,
    ROUND(SUM(o.sales), 2)                               AS total_sales,
    ROUND(SUM(o.profit), 2)                              AS total_profit,
    COUNT(DISTINCT o.order_id)                           AS total_orders,
    ROUND(SUM(o.profit) / NULLIF(SUM(o.sales), 0) * 100, 2) AS profit_margin_pct
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_sales DESC;


-- ── 4. TOP 10 CUSTOMERS BY REVENUE ───────────────────────
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    c.region,
    ROUND(SUM(o.sales), 2)   AS total_spent,
    ROUND(SUM(o.profit), 2)  AS total_profit_generated,
    COUNT(DISTINCT o.order_id) AS order_count
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment, c.region
ORDER BY total_spent DESC
LIMIT 10;


-- ── 5. TOP 10 MOST PROFITABLE PRODUCTS ───────────────────
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    ROUND(SUM(o.profit), 2)  AS total_profit,
    ROUND(SUM(o.sales), 2)   AS total_sales,
    SUM(o.quantity)          AS units_sold
FROM Orders o
JOIN Products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY total_profit DESC
LIMIT 10;


-- ── 6. CATEGORY vs SUB-CATEGORY BREAKDOWN ────────────────
SELECT
    p.category,
    p.sub_category,
    ROUND(SUM(o.sales), 2)                               AS total_sales,
    ROUND(SUM(o.profit), 2)                              AS total_profit,
    ROUND(SUM(o.profit) / NULLIF(SUM(o.sales), 0) * 100, 2) AS profit_margin_pct,
    SUM(o.quantity)                                      AS units_sold
FROM Orders o
JOIN Products p ON o.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY total_sales DESC;


-- ── 7. CUSTOMER SEGMENT ANALYSIS ─────────────────────────
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id)  AS customer_count,
    ROUND(SUM(o.sales), 2)         AS total_sales,
    ROUND(AVG(o.sales), 2)         AS avg_order_value,
    ROUND(SUM(o.profit), 2)        AS total_profit
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY total_sales DESC;


-- ── 8. DISCOUNT IMPACT ON PROFIT ─────────────────────────
SELECT
    CASE
        WHEN discount = 0            THEN 'No Discount'
        WHEN discount <= 0.15        THEN 'Low (≤15%)'
        WHEN discount <= 0.35        THEN 'Medium (16-35%)'
        ELSE                              'High (>35%)'
    END                                         AS discount_bucket,
    COUNT(*)                                    AS order_count,
    ROUND(AVG(sales), 2)                        AS avg_sales,
    ROUND(AVG(profit), 2)                       AS avg_profit,
    ROUND(AVG(profit / NULLIF(sales,0)) * 100, 2) AS avg_margin_pct
FROM Orders
GROUP BY discount_bucket
ORDER BY avg_margin_pct DESC;


-- ── 9. TOP 5 STATES BY SALES ──────────────────────────────
SELECT
    c.state,
    c.region,
    ROUND(SUM(o.sales), 2)   AS total_sales,
    ROUND(SUM(o.profit), 2)  AS total_profit,
    COUNT(DISTINCT o.order_id) AS orders
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.state, c.region
ORDER BY total_sales DESC
LIMIT 5;


-- ── 10. REPEAT CUSTOMERS ──────────────────────────────────
SELECT
    total_customers,
    repeat_customers,
    ROUND(repeat_customers * 100.0 / total_customers, 2) AS repeat_rate_pct
FROM (
    SELECT
        COUNT(DISTINCT customer_id)                                AS total_customers,
        COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) AS repeat_customers
    FROM (
        SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
        FROM Orders
        GROUP BY customer_id
    ) sub
) summary;


-- ── 11. PAYMENT MODE ANALYSIS ─────────────────────────────
SELECT
    payment_mode,
    COUNT(*)                  AS transactions,
    ROUND(SUM(sales), 2)      AS total_sales,
    ROUND(AVG(sales), 2)      AS avg_transaction_value
FROM Orders
GROUP BY payment_mode
ORDER BY transactions DESC;


-- ── 12. YoY SALES GROWTH (MySQL) ─────────────────────────
SELECT
    curr.year,
    curr.total_sales,
    prev.total_sales                                              AS prev_year_sales,
    ROUND((curr.total_sales - prev.total_sales)
          / NULLIF(prev.total_sales, 0) * 100, 2)               AS yoy_growth_pct
FROM (
    SELECT YEAR(order_date) AS year, ROUND(SUM(sales),2) AS total_sales
    FROM Orders GROUP BY YEAR(order_date)
) curr
LEFT JOIN (
    SELECT YEAR(order_date) AS year, ROUND(SUM(sales),2) AS total_sales
    FROM Orders GROUP BY YEAR(order_date)
) prev ON curr.year = prev.year + 1
ORDER BY curr.year;
