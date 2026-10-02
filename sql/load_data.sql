
-- SUPPLY CHAIN AND INVENTORY MANAGEMENT
-- LOAD CLEANED DATA INTO MYSQL DATA WAREHOUSE

USE supply_chain_dw;

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;


-- 1. CREATE STAGING TABLES

DROP TABLE IF EXISTS staging_sales;
DROP TABLE IF EXISTS staging_inventory;
DROP TABLE IF EXISTS staging_suppliers;
DROP TABLE IF EXISTS staging_purchase_orders;


CREATE TABLE staging_sales (
    sale_id VARCHAR(50),
    product_id VARCHAR(20),
    store_id VARCHAR(20),
    sale_date DATE,
    quantity_sold INT,
    revenue DECIMAL(15,2),
    sale_year INT,
    sale_month INT,
    sale_month_name VARCHAR(20),
    revenue_per_unit DECIMAL(15,2)
);


CREATE TABLE staging_inventory (
    product_id VARCHAR(20),
    store_id VARCHAR(20),
    warehouse_id VARCHAR(20),
    stock_level INT,
    reorder_level INT,
    last_updated DATE,
    reorder_status VARCHAR(50),
    stock_difference INT
);


CREATE TABLE staging_suppliers (
    supplier_id VARCHAR(20),
    supplier_name VARCHAR(255),
    product_id VARCHAR(20),
    lead_time_days INT,
    order_frequency VARCHAR(50)
);


CREATE TABLE staging_purchase_orders (
    order_id VARCHAR(50),
    product_id VARCHAR(20),
    supplier_id VARCHAR(20),
    order_date DATE,
    quantity INT,
    arrival_date DATE,
    actual_lead_time_days INT
);


-- 2. LOAD CLEANED SALES DATA

LOAD DATA LOCAL INFILE
'C:/Users/astha/OneDrive/Supply_Chain_Inventory_Management/output/cleaned_sales.csv'
INTO TABLE staging_sales
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


-- 3. LOAD CLEANED INVENTORY DATA

LOAD DATA LOCAL INFILE
'C:/Users/astha/OneDrive/Supply_Chain_Inventory_Management/output/cleaned_inventory.csv'
INTO TABLE staging_inventory
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


-- 4. LOAD CLEANED SUPPLIER DATA

LOAD DATA LOCAL INFILE
'C:/Users/astha/OneDrive/Supply_Chain_Inventory_Management/output/cleaned_suppliers.csv'
INTO TABLE staging_suppliers
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


-- 5. LOAD CLEANED PURCHASE ORDER DATA

LOAD DATA LOCAL INFILE
'C:/Users/astha/OneDrive/Supply_Chain_Inventory_Management/output/cleaned_purchase_orders.csv'
INTO TABLE staging_purchase_orders
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;


-- 6. CLEAR EXISTING WAREHOUSE DATA

DELETE FROM fact_purchase_orders;
DELETE FROM fact_inventory;
DELETE FROM fact_sales;

DELETE FROM agg_monthly_sales;
DELETE FROM agg_product_inventory;

DELETE FROM dim_date;
DELETE FROM dim_product;
DELETE FROM dim_store;
DELETE FROM dim_warehouse;
DELETE FROM dim_supplier;


-- 7. LOAD PRODUCT DIMENSION

INSERT INTO dim_product (product_id)
SELECT DISTINCT product_id
FROM (
    SELECT product_id
    FROM staging_sales

    UNION

    SELECT product_id
    FROM staging_inventory

    UNION

    SELECT product_id
    FROM staging_suppliers

    UNION

    SELECT product_id
    FROM staging_purchase_orders
) AS products
WHERE product_id IS NOT NULL;


-- 8. LOAD STORE DIMENSION

INSERT INTO dim_store (store_id)
SELECT DISTINCT store_id
FROM (
    SELECT store_id
    FROM staging_sales

    UNION

    SELECT store_id
    FROM staging_inventory
) AS stores
WHERE store_id IS NOT NULL;


-- 9. LOAD WAREHOUSE DIMENSION

INSERT INTO dim_warehouse (warehouse_id)
SELECT DISTINCT warehouse_id
FROM staging_inventory
WHERE warehouse_id IS NOT NULL;


-- 10. LOAD SUPPLIER DIMENSION

INSERT INTO dim_supplier (
    supplier_id,
    supplier_name,
    lead_time_days,
    order_frequency
)
SELECT
    supplier_id,
    MAX(supplier_name),
    MAX(lead_time_days),
    MAX(order_frequency)
FROM staging_suppliers
GROUP BY supplier_id;


-- 11. LOAD DATE DIMENSION

INSERT INTO dim_date (
    date_key,
    full_date,
    year,
    month,
    month_name,
    quarter
)
SELECT
    DATE_FORMAT(all_dates.full_date, '%Y%m%d') + 0 AS date_key,
    all_dates.full_date,
    YEAR(all_dates.full_date),
    MONTH(all_dates.full_date),
    MONTHNAME(all_dates.full_date),
    QUARTER(all_dates.full_date)
FROM (
    SELECT DISTINCT sale_date AS full_date
    FROM staging_sales
    WHERE sale_date IS NOT NULL

    UNION

    SELECT DISTINCT last_updated AS full_date
    FROM staging_inventory
    WHERE last_updated IS NOT NULL

    UNION

    SELECT DISTINCT order_date AS full_date
    FROM staging_purchase_orders
    WHERE order_date IS NOT NULL

    UNION

    SELECT DISTINCT arrival_date AS full_date
    FROM staging_purchase_orders
    WHERE arrival_date IS NOT NULL
) AS all_dates;


-- 12. LOAD SALES FACT TABLE

INSERT INTO fact_sales (
    sale_id,
    product_key,
    store_key,
    date_key,
    quantity_sold,
    revenue,
    revenue_per_unit
)
SELECT
    s.sale_id,
    p.product_key,
    st.store_key,
    d.date_key,
    s.quantity_sold,
    s.revenue,
    s.revenue_per_unit
FROM staging_sales s

INNER JOIN dim_product p
    ON s.product_id = p.product_id

INNER JOIN dim_store st
    ON s.store_id = st.store_id

INNER JOIN dim_date d
    ON s.sale_date = d.full_date;


-- 13. LOAD INVENTORY FACT TABLE

INSERT INTO fact_inventory (
    product_key,
    store_key,
    warehouse_key,
    date_key,
    stock_level,
    reorder_level,
    stock_difference,
    reorder_status
)
SELECT
    p.product_key,
    st.store_key,
    w.warehouse_key,
    d.date_key,
    i.stock_level,
    i.reorder_level,
    i.stock_difference,
    i.reorder_status
FROM staging_inventory i

INNER JOIN dim_product p
    ON i.product_id = p.product_id

INNER JOIN dim_store st
    ON i.store_id = st.store_id

INNER JOIN dim_warehouse w
    ON i.warehouse_id = w.warehouse_id

INNER JOIN dim_date d
    ON i.last_updated = d.full_date;


-- 14. LOAD PURCHASE ORDER FACT TABLE

INSERT INTO fact_purchase_orders (
    order_id,
    product_key,
    supplier_key,
    order_date_key,
    arrival_date_key,
    quantity,
    actual_lead_time_days
)
SELECT
    po.order_id,
    p.product_key,
    s.supplier_key,
    od.date_key,
    ad.date_key,
    po.quantity,
    po.actual_lead_time_days
FROM staging_purchase_orders po

INNER JOIN dim_product p
    ON po.product_id = p.product_id

INNER JOIN dim_supplier s
    ON po.supplier_id = s.supplier_id

INNER JOIN dim_date od
    ON po.order_date = od.full_date

INNER JOIN dim_date ad
    ON po.arrival_date = ad.full_date;


-- 15. VERIFY DIMENSION TABLES

SELECT 'dim_product' AS table_name, COUNT(*) AS row_count
FROM dim_product

UNION ALL

SELECT 'dim_store', COUNT(*)
FROM dim_store

UNION ALL

SELECT 'dim_warehouse', COUNT(*)
FROM dim_warehouse

UNION ALL

SELECT 'dim_supplier', COUNT(*)
FROM dim_supplier

UNION ALL

SELECT 'dim_date', COUNT(*)
FROM dim_date;


-- 16. VERIFY FACT TABLES

SELECT 'fact_sales' AS table_name, COUNT(*) AS row_count
FROM fact_sales

UNION ALL

SELECT 'fact_inventory', COUNT(*)
FROM fact_inventory

UNION ALL

SELECT 'fact_purchase_orders', COUNT(*)
FROM fact_purchase_orders;


-- 17. VERIFY STAGING TABLES

SELECT 'staging_sales' AS table_name, COUNT(*) AS row_count
FROM staging_sales

UNION ALL

SELECT 'staging_inventory', COUNT(*)
FROM staging_inventory

UNION ALL

SELECT 'staging_suppliers', COUNT(*)
FROM staging_suppliers

UNION ALL

SELECT 'staging_purchase_orders', COUNT(*)
FROM staging_purchase_orders;


-- 18. CLEAN UP STAGING TABLES

DROP TABLE staging_sales;
DROP TABLE staging_inventory;
DROP TABLE staging_suppliers;
DROP TABLE staging_purchase_orders;


-- 19. FINAL STATUS

SET FOREIGN_KEY_CHECKS = 1;

SELECT 'DATA LOADING COMPLETED SUCCESSFULLY' AS status;