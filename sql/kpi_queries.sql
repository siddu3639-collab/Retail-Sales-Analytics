CREATE OR REPLACE VIEW vw_monthly_kpi AS
SELECT
    YEAR(o.order_date)        AS year,
    MONTH(o.order_date)       AS month,
    ROUND(SUM(o.sales), 2)    AS monthly_sales,
    ROUND(SUM(o.profit), 2)   AS monthly_profit,
    COUNT(DISTINCT o.order_id) AS monthly_orders,
    ROUND(SUM(o.profit) / NULLIF(SUM(o.sales),0) * 100, 2) AS profit_margin_pct,
    ROUND(AVG(o.sales), 2)    AS avg_order_value
FROM Orders o
GROUP BY YEAR(o.order_date), MONTH(o.order_date);


-- ── VIEW 2: Product Performance
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    ROUND(SUM(o.sales), 2)    AS total_sales,
    ROUND(SUM(o.profit), 2)   AS total_profit,
    SUM(o.quantity)           AS units_sold,
    ROUND(AVG(o.discount), 2) AS avg_discount,
    ROUND(SUM(o.profit) / NULLIF(SUM(o.sales),0) * 100, 2) AS profit_margin_pct
FROM Orders o
JOIN Products p ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category;


-- ── VIEW 3: Customer 360 
CREATE OR REPLACE VIEW vw_customer_360 AS
SELECT
    c.customer_id,
    c.customer_name,
    c.segment,
    c.region,
    c.state,
    COUNT(DISTINCT o.order_id)  AS total_orders,
    ROUND(SUM(o.sales), 2)      AS lifetime_value,
    ROUND(SUM(o.profit), 2)     AS total_profit_contributed,
    ROUND(AVG(o.sales), 2)      AS avg_order_value,
    MIN(o.order_date)           AS first_order_date,
    MAX(o.order_date)           AS last_order_date,
    CASE WHEN COUNT(DISTINCT o.order_id) > 1 THEN 'Repeat' ELSE 'One-Time' END AS customer_type
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment, c.region, c.state;


-- ── VIEW 4: Regional KPI 
CREATE OR REPLACE VIEW vw_regional_kpi AS
SELECT
    c.region,
    c.state,
    ROUND(SUM(o.sales), 2)    AS total_sales,
    ROUND(SUM(o.profit), 2)   AS total_profit,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    ROUND(SUM(o.profit) / NULLIF(SUM(o.sales),0) * 100, 2) AS profit_margin_pct
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.region, c.state;


-- ── SCALAR KPIs (use in Power BI measures or reports) ────

-- KPI: Total Sales
SELECT ROUND(SUM(sales), 2) AS kpi_total_sales FROM Orders;

-- KPI: Total Profit
SELECT ROUND(SUM(profit), 2) AS kpi_total_profit FROM Orders;

-- KPI: Overall Profit Margin %
SELECT ROUND(SUM(profit) / NULLIF(SUM(sales), 0) * 100, 2) AS kpi_profit_margin FROM Orders;

-- KPI: Total Unique Customers
SELECT COUNT(DISTINCT customer_id) AS kpi_total_customers FROM Orders;

-- KPI: Average Order Value
SELECT ROUND(AVG(sales), 2) AS kpi_avg_order_value FROM Orders;

-- KPI: Best Performing Region
SELECT region
FROM (
    SELECT c.region, SUM(o.sales) AS s
    FROM Orders o JOIN Customers c ON o.customer_id = c.customer_id
    GROUP BY c.region ORDER BY s DESC LIMIT 1
) best;

-- KPI: Most Profitable Category
SELECT category
FROM (
    SELECT p.category, SUM(o.profit) AS p_val
    FROM Orders o JOIN Products p ON o.product_id = p.product_id
    GROUP BY p.category ORDER BY p_val DESC LIMIT 1
) best;
