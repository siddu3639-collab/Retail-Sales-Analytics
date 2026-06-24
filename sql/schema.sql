-- ============================================================
-- schema.sql
-- Creates the Retail Sales database schema
-- Compatible with MySQL 8+ and PostgreSQL 13+
-- ============================================================

-- ── Customers ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Customers (
    customer_id   VARCHAR(20)  PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    segment       VARCHAR(50),
    region        VARCHAR(50),
    state         VARCHAR(50)
);

-- ── Products ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Products (
    product_id   VARCHAR(20)  PRIMARY KEY,
    category     VARCHAR(50),
    sub_category VARCHAR(50),
    product_name VARCHAR(200)
);

-- ── Orders ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Orders (
    order_id      VARCHAR(20) PRIMARY KEY,
    order_date    DATE        NOT NULL,
    customer_id   VARCHAR(20) NOT NULL,
    product_id    VARCHAR(20) NOT NULL,
    sales         DECIMAL(12,2),
    quantity      INT,
    discount      DECIMAL(5,2),
    profit        DECIMAL(12,2),
    shipping_cost DECIMAL(10,2),
    payment_mode  VARCHAR(50),

    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (product_id)  REFERENCES Products(product_id)
);

-- ── Indexes for query performance ─────────────────────────
CREATE INDEX IF NOT EXISTS idx_orders_date        ON Orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer    ON Orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product     ON Orders(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category  ON Products(category);
CREATE INDEX IF NOT EXISTS idx_customers_region   ON Customers(region);
CREATE INDEX IF NOT EXISTS idx_customers_segment  ON Customers(segment);
