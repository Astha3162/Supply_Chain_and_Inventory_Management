
-- SUPPLY CHAIN AND INVENTORY MANAGEMENT
-- SQL ANALYSIS

USE supply_chain_dw;


-- 1. FAST-MOVING PRODUCTS
-- Highest sales in the latest 3 months

SELECT
    p.product_id,
    SUM(f.quantity_sold) AS total_quantity_sold,
    SUM(f.revenue) AS total_revenue
FROM fact_sales f
INNER JOIN dim_product p
    ON f.product_key = p.product_key
INNER JOIN dim_date d
    ON f.date_key = d.date_key
WHERE d.full_date >= (
    SELECT DATE_SUB(MAX(full_date), INTERVAL 3 MONTH)
    FROM dim_date
)
GROUP BY p.product_id
ORDER BY total_quantity_sold DESC;

-- 2. SLOW-MOVING PRODUCTS
-- Lowest sales in the latest 3 months

SELECT
    p.product_id,
    SUM(f.quantity_sold) AS total_quantity_sold,
    SUM(f.revenue) AS total_revenue
FROM fact_sales f
INNER JOIN dim_product p
    ON f.product_key = p.product_key
INNER JOIN dim_date d
    ON f.date_key = d.date_key
WHERE d.full_date >= (
    SELECT DATE_SUB(MAX(full_date), INTERVAL 3 MONTH)
    FROM dim_date
)
GROUP BY p.product_id
ORDER BY total_quantity_sold ASC;


-- 3. PRODUCTS BELOW REORDER LEVEL

SELECT
    p.product_id,
    st.store_id,
    w.warehouse_id,
    f.stock_level,
    f.reorder_level,
    f.stock_difference,
    f.reorder_status,
    d.full_date AS last_updated
FROM fact_inventory f
INNER JOIN dim_product p
    ON f.product_key = p.product_key
INNER JOIN dim_store st
    ON f.store_key = st.store_key
INNER JOIN dim_warehouse w
    ON f.warehouse_key = w.warehouse_key
INNER JOIN dim_date d
    ON f.date_key = d.date_key
WHERE f.stock_level <= f.reorder_level
ORDER BY f.stock_difference ASC;


-- 4. INVENTORY STATUS SUMMARY

SELECT
    reorder_status,
    COUNT(*) AS inventory_records
FROM fact_inventory
GROUP BY reorder_status
ORDER BY inventory_records DESC;


-- 5. PRODUCT-WISE INVENTORY SUMMARY

SELECT
    p.product_id,
    SUM(f.stock_level) AS total_stock,
    AVG(f.reorder_level) AS average_reorder_level,
    SUM(
        CASE
            WHEN f.stock_level <= f.reorder_level THEN 1
            ELSE 0
        END
    ) AS reorder_required_count
FROM fact_inventory f
INNER JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_id
ORDER BY reorder_required_count DESC;


-- 6. SUPPLIER LEAD TIME ANALYSIS

SELECT
    s.supplier_id,
    s.supplier_name,
    s.lead_time_days,
    s.order_frequency,
    COUNT(po.purchase_order_key) AS total_orders,
    AVG(po.actual_lead_time_days) AS average_actual_lead_time
FROM dim_supplier s
LEFT JOIN fact_purchase_orders po
    ON s.supplier_key = po.supplier_key
GROUP BY
    s.supplier_id,
    s.supplier_name,
    s.lead_time_days,
    s.order_frequency
ORDER BY s.lead_time_days ASC;


-- 7. SUPPLIERS WITH LONG LEAD TIMES

SELECT
    supplier_id,
    supplier_name,
    lead_time_days,
    order_frequency
FROM dim_supplier
ORDER BY lead_time_days DESC;


-- 8. PRODUCT-WISE SUPPLIER ANALYSIS

SELECT
    p.product_id,
    s.supplier_id,
    s.supplier_name,
    s.lead_time_days,
    s.order_frequency
FROM bridge_supplier_product bsp
INNER JOIN dim_product p
    ON bsp.product_key = p.product_key
INNER JOIN dim_supplier s
    ON bsp.supplier_key = s.supplier_key
ORDER BY
    p.product_id,
    s.lead_time_days ASC;


-- 9. ALTERNATIVE SUPPLIERS
-- Products supplied by multiple suppliers

SELECT
    p.product_id,
    COUNT(DISTINCT s.supplier_id) AS supplier_count,
    GROUP_CONCAT(
        CONCAT(
            s.supplier_id,
            ' - ',
            s.supplier_name
        )
        ORDER BY s.lead_time_days ASC
        SEPARATOR ', '
    ) AS available_suppliers
FROM bridge_supplier_product bsp
INNER JOIN dim_product p
    ON bsp.product_key = p.product_key
INNER JOIN dim_supplier s
    ON bsp.supplier_key = s.supplier_key
GROUP BY p.product_id
HAVING COUNT(DISTINCT s.supplier_id) > 1
ORDER BY supplier_count DESC;


-- 10. SUPPLIER WITH LOWEST LEAD TIME FOR EACH PRODUCT

SELECT
    p.product_id,
    s.supplier_id,
    s.supplier_name,
    s.lead_time_days,
    s.order_frequency
FROM bridge_supplier_product bsp
INNER JOIN dim_product p
    ON bsp.product_key = p.product_key
INNER JOIN dim_supplier s
    ON bsp.supplier_key = s.supplier_key
INNER JOIN (
    SELECT
        bsp2.product_key,
        MIN(s2.lead_time_days) AS minimum_lead_time
    FROM bridge_supplier_product bsp2
    INNER JOIN dim_supplier s2
        ON bsp2.supplier_key = s2.supplier_key
    GROUP BY bsp2.product_key
) x
    ON bsp.product_key = x.product_key
    AND s.lead_time_days = x.minimum_lead_time
ORDER BY p.product_id;


-- 11. PURCHASE ORDER PERFORMANCE

SELECT
    s.supplier_id,
    s.supplier_name,
    COUNT(po.purchase_order_key) AS total_purchase_orders,
    SUM(po.quantity) AS total_quantity_ordered,
    AVG(po.actual_lead_time_days) AS average_actual_lead_time,
    MIN(po.actual_lead_time_days) AS minimum_actual_lead_time,
    MAX(po.actual_lead_time_days) AS maximum_actual_lead_time
FROM fact_purchase_orders po
INNER JOIN dim_supplier s
    ON po.supplier_key = s.supplier_key
GROUP BY
    s.supplier_id,
    s.supplier_name
ORDER BY average_actual_lead_time ASC;


-- 12. MONTHLY SALES SUMMARY

SELECT
    d.year,
    d.month,
    d.month_name,
    SUM(f.quantity_sold) AS total_quantity_sold,
    SUM(f.revenue) AS total_revenue
FROM fact_sales f
INNER JOIN dim_date d
    ON f.date_key = d.date_key
GROUP BY
    d.year,
    d.month,
    d.month_name
ORDER BY
    d.year,
    d.month;


-- 13. PRODUCT SALES SUMMARY

SELECT
    p.product_id,
    SUM(f.quantity_sold) AS total_quantity_sold,
    SUM(f.revenue) AS total_revenue,
    AVG(f.revenue_per_unit) AS average_revenue_per_unit
FROM fact_sales f
INNER JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_id
ORDER BY total_revenue DESC;


-- 14. STORE-WISE SALES PERFORMANCE

SELECT
    st.store_id,
    SUM(f.quantity_sold) AS total_quantity_sold,
    SUM(f.revenue) AS total_revenue
FROM fact_sales f
INNER JOIN dim_store st
    ON f.store_key = st.store_key
GROUP BY st.store_id
ORDER BY total_revenue DESC;


-- 15. OVERALL BUSINESS SUMMARY

SELECT
    COUNT(DISTINCT f.sale_id) AS total_sales_transactions,
    SUM(f.quantity_sold) AS total_quantity_sold,
    SUM(f.revenue) AS total_revenue,
    AVG(f.quantity_sold) AS average_quantity_per_sale,
    AVG(f.revenue) AS average_revenue_per_sale
FROM fact_sales f;

-- END OF SQL ANALYSIS