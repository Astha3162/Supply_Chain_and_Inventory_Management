
-- SUPPLY CHAIN AND INVENTORY MANAGEMENT
-- MYSQL DATA WAREHOUSE

-- Create database
CREATE DATABASE IF NOT EXISTS supply_chain_dw;

USE supply_chain_dw;


-- 1. DIMENSION: PRODUCT

DROP TABLE IF EXISTS dim_product;

CREATE TABLE dim_product (
    product_key INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL UNIQUE
);


-- 2. DIMENSION: STORE

DROP TABLE IF EXISTS dim_store;

CREATE TABLE dim_store (
    store_key INT AUTO_INCREMENT PRIMARY KEY,
    store_id VARCHAR(20) NOT NULL UNIQUE
);


-- 3. DIMENSION: WAREHOUSE

DROP TABLE IF EXISTS dim_warehouse;

CREATE TABLE dim_warehouse (
    warehouse_key INT AUTO_INCREMENT PRIMARY KEY,
    warehouse_id VARCHAR(20) NOT NULL UNIQUE
);


-- 4. DIMENSION: SUPPLIER

DROP TABLE IF EXISTS dim_supplier;

CREATE TABLE dim_supplier (
    supplier_key INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL UNIQUE,
    supplier_name VARCHAR(255),
    lead_time_days INT,
    order_frequency VARCHAR(50)
);


-- 5. DIMENSION: DATE

DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INT,
    month INT,
    month_name VARCHAR(20),
    quarter INT
);


-- 6. FACT TABLE: SALES

DROP TABLE IF EXISTS fact_sales;

CREATE TABLE fact_sales (
    sales_key BIGINT AUTO_INCREMENT PRIMARY KEY,
    sale_id VARCHAR(50) NOT NULL UNIQUE,

    product_key INT NOT NULL,
    store_key INT NOT NULL,
    date_key INT NOT NULL,

    quantity_sold INT,
    revenue DECIMAL(15,2),
    revenue_per_unit DECIMAL(15,2),

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    FOREIGN KEY (store_key)
        REFERENCES dim_store(store_key),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);


-- 7. FACT TABLE: INVENTORY

DROP TABLE IF EXISTS fact_inventory;

CREATE TABLE fact_inventory (
    inventory_key BIGINT AUTO_INCREMENT PRIMARY KEY,

    product_key INT NOT NULL,
    store_key INT NOT NULL,
    warehouse_key INT NOT NULL,
    date_key INT NOT NULL,

    stock_level INT,
    reorder_level INT,
    stock_difference INT,
    reorder_status VARCHAR(50),

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    FOREIGN KEY (store_key)
        REFERENCES dim_store(store_key),

    FOREIGN KEY (warehouse_key)
        REFERENCES dim_warehouse(warehouse_key),

    FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);


-- 8. FACT TABLE: PURCHASE ORDERS

DROP TABLE IF EXISTS fact_purchase_orders;

CREATE TABLE fact_purchase_orders (
    purchase_order_key BIGINT AUTO_INCREMENT PRIMARY KEY,

    order_id VARCHAR(50) NOT NULL UNIQUE,

    product_key INT NOT NULL,
    supplier_key INT NOT NULL,
    order_date_key INT NOT NULL,
    arrival_date_key INT NOT NULL,

    quantity INT,
    actual_lead_time_days INT,

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key),

    FOREIGN KEY (supplier_key)
        REFERENCES dim_supplier(supplier_key),

    FOREIGN KEY (order_date_key)
        REFERENCES dim_date(date_key),

    FOREIGN KEY (arrival_date_key)
        REFERENCES dim_date(date_key)
);


-- 9. AGGREGATED TABLE: MONTHLY SALES

DROP TABLE IF EXISTS agg_monthly_sales;

CREATE TABLE agg_monthly_sales (
    aggregation_key BIGINT AUTO_INCREMENT PRIMARY KEY,

    product_key INT NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,

    total_quantity_sold BIGINT,
    total_revenue DECIMAL(18,2),

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key)
);


-- 10. AGGREGATED TABLE: PRODUCT INVENTORY

DROP TABLE IF EXISTS agg_product_inventory;

CREATE TABLE agg_product_inventory (
    aggregation_key BIGINT AUTO_INCREMENT PRIMARY KEY,

    product_key INT NOT NULL,

    total_stock INT,
    average_reorder_level DECIMAL(15,2),
    reorder_required_count INT,

    FOREIGN KEY (product_key)
        REFERENCES dim_product(product_key)
);


-- VERIFY CREATED TABLES

SHOW TABLES;