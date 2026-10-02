import pandas as pd
from pathlib import Path


# 1. PROJECT PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# 2. INPUT FILE PATHS

sales_file = DATA_DIR / "sales_data.csv"
inventory_file = DATA_DIR / "inventory_data.csv"
suppliers_file = DATA_DIR / "suppliers_data.csv"
purchase_orders_file = DATA_DIR / "purchase_orders_data.csv"


# 3. LOAD RAW DATA

print("\n" + "=" * 70)
print("SUPPLY CHAIN AND INVENTORY MANAGEMENT - ETL PROCESS")
print("=" * 70)

print("\n--- LOADING RAW DATA ---")

sales = pd.read_csv(sales_file)
inventory = pd.read_csv(inventory_file)
suppliers = pd.read_csv(suppliers_file)
purchase_orders = pd.read_csv(purchase_orders_file)

print(f"Sales records loaded: {len(sales)}")
print(f"Inventory records loaded: {len(inventory)}")
print(f"Supplier records loaded: {len(suppliers)}")
print(f"Purchase order records loaded: {len(purchase_orders)}")


# 4. STANDARDIZE COLUMN NAMES

print("\n--- STANDARDIZING COLUMN NAMES ---")

sales = sales.rename(columns={
    "Sale_ID": "sale_id",
    "Product_ID": "product_id",
    "Store_ID": "store_id",
    "Sale_Date": "sale_date",
    "Quantity_Sold": "quantity_sold",
    "Revenue": "revenue"
})

inventory = inventory.rename(columns={
    "Product_ID": "product_id",
    "Store_ID": "store_id",
    "Warehouse_ID": "warehouse_id",
    "Stock_Level": "stock_level",
    "Reorder_Level": "reorder_level",
    "Last_Updated": "last_updated"
})

suppliers = suppliers.rename(columns={
    "Supplier_ID": "supplier_id",
    "Supplier_Name": "supplier_name",
    "Product_ID": "product_id",
    "Lead_Time (days)": "lead_time_days",
    "Order_Frequency": "order_frequency"
})

purchase_orders = purchase_orders.rename(columns={
    "Order_ID": "order_id",
    "Product_ID": "product_id",
    "Supplier_ID": "supplier_id",
    "Order_Date": "order_date",
    "Quantity": "quantity",
    "Arrival_Date": "arrival_date"
})


# 5. CONVERT DATE COLUMNS

print("\n--- CONVERTING DATE COLUMNS ---")

sales["sale_date"] = pd.to_datetime(
    sales["sale_date"],
    errors="coerce"
)

inventory["last_updated"] = pd.to_datetime(
    inventory["last_updated"],
    errors="coerce"
)

purchase_orders["order_date"] = pd.to_datetime(
    purchase_orders["order_date"],
    errors="coerce"
)

purchase_orders["arrival_date"] = pd.to_datetime(
    purchase_orders["arrival_date"],
    errors="coerce"
)

print("Date conversion completed.")


# 6. CONVERT NUMERIC COLUMNS

print("\n--- CONVERTING NUMERIC COLUMNS ---")

sales["quantity_sold"] = pd.to_numeric(
    sales["quantity_sold"],
    errors="coerce"
)

sales["revenue"] = pd.to_numeric(
    sales["revenue"],
    errors="coerce"
)

inventory["stock_level"] = pd.to_numeric(
    inventory["stock_level"],
    errors="coerce"
)

inventory["reorder_level"] = pd.to_numeric(
    inventory["reorder_level"],
    errors="coerce"
)

suppliers["lead_time_days"] = pd.to_numeric(
    suppliers["lead_time_days"],
    errors="coerce"
)

purchase_orders["quantity"] = pd.to_numeric(
    purchase_orders["quantity"],
    errors="coerce"
)

print("Numeric conversion completed.")


# 7. REMOVE EXACT DUPLICATES

print("\n--- CHECKING DUPLICATES ---")

sales_duplicates = sales.duplicated().sum()
inventory_duplicates = inventory.duplicated().sum()
supplier_duplicates = suppliers.duplicated().sum()
purchase_order_duplicates = purchase_orders.duplicated().sum()

print(f"Sales duplicates: {sales_duplicates}")
print(f"Inventory duplicates: {inventory_duplicates}")
print(f"Supplier duplicates: {supplier_duplicates}")
print(f"Purchase order duplicates: {purchase_order_duplicates}")

sales = sales.drop_duplicates()
inventory = inventory.drop_duplicates()
suppliers = suppliers.drop_duplicates()
purchase_orders = purchase_orders.drop_duplicates()


# 8. CHECK MISSING VALUES AFTER CONVERSION

print("\n--- CHECKING MISSING VALUES ---")

sales_missing = sales.isnull().sum().sum()
inventory_missing = inventory.isnull().sum().sum()
supplier_missing = suppliers.isnull().sum().sum()
purchase_order_missing = purchase_orders.isnull().sum().sum()

print(f"Sales missing values: {sales_missing}")
print(f"Inventory missing values: {inventory_missing}")
print(f"Supplier missing values: {supplier_missing}")
print(f"Purchase order missing values: {purchase_order_missing}")

# 9. CREATE SALES DERIVED COLUMNS

print("\n--- CREATING SALES DERIVED COLUMNS ---")

sales["sale_year"] = sales["sale_date"].dt.year
sales["sale_month"] = sales["sale_date"].dt.month
sales["sale_month_name"] = sales["sale_date"].dt.month_name()

sales["revenue_per_unit"] = (
    sales["revenue"] / sales["quantity_sold"]
)

print("Sales derived columns created.")


# 10. CREATE INVENTORY DERIVED COLUMNS

print("\n--- CREATING INVENTORY DERIVED COLUMNS ---")

inventory["reorder_status"] = inventory.apply(
    lambda row:
    "REORDER REQUIRED"
    if row["stock_level"] <= row["reorder_level"]
    else "STOCK SUFFICIENT",
    axis=1
)

inventory["stock_difference"] = (
    inventory["stock_level"] - inventory["reorder_level"]
)

print("Inventory derived columns created.")


# 11. CREATE PURCHASE ORDER DERIVED COLUMNS

print("\n--- CREATING PURCHASE ORDER DERIVED COLUMNS ---")

purchase_orders["actual_lead_time_days"] = (
    purchase_orders["arrival_date"]
    - purchase_orders["order_date"]
).dt.days

print("Purchase order lead-time calculation completed.")


# 12. STANDARDIZE TEXT VALUES

print("\n--- STANDARDIZING TEXT VALUES ---")

text_columns = [
    "product_id",
    "store_id"
]

for column in text_columns:
    sales[column] = sales[column].astype(str).str.strip().str.upper()
    inventory[column] = inventory[column].astype(str).str.strip().str.upper()

suppliers["supplier_id"] = (
    suppliers["supplier_id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

suppliers["product_id"] = (
    suppliers["product_id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

purchase_orders["product_id"] = (
    purchase_orders["product_id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

purchase_orders["supplier_id"] = (
    purchase_orders["supplier_id"]
    .astype(str)
    .str.strip()
    .str.upper()
)

print("Text standardization completed.")

# 13. BASIC DATA VALIDATION

print("\n--- DATA VALIDATION ---")

invalid_sales_quantity = (
    sales["quantity_sold"] <= 0
).sum()

invalid_sales_revenue = (
    sales["revenue"] <= 0
).sum()

invalid_inventory_stock = (
    inventory["stock_level"] < 0
).sum()

invalid_inventory_reorder = (
    inventory["reorder_level"] < 0
).sum()

invalid_supplier_lead_time = (
    suppliers["lead_time_days"] <= 0
).sum()

invalid_po_quantity = (
    purchase_orders["quantity"] <= 0
).sum()

print(
    f"Invalid sales quantities: "
    f"{invalid_sales_quantity}"
)

print(
    f"Invalid sales revenues: "
    f"{invalid_sales_revenue}"
)

print(
    f"Invalid inventory stock levels: "
    f"{invalid_inventory_stock}"
)

print(
    f"Invalid inventory reorder levels: "
    f"{invalid_inventory_reorder}"
)

print(
    f"Invalid supplier lead times: "
    f"{invalid_supplier_lead_time}"
)

print(
    f"Invalid purchase order quantities: "
    f"{invalid_po_quantity}"
)


# 14. REFERENTIAL INTEGRITY CHECKS

print("\n--- REFERENTIAL INTEGRITY CHECKS ---")

sales_invalid_products = (
    ~sales["product_id"].isin(
        inventory["product_id"].unique()
    )
).sum()

purchase_invalid_products = (
    ~purchase_orders["product_id"].isin(
        suppliers["product_id"].unique()
    )
).sum()

purchase_invalid_suppliers = (
    ~purchase_orders["supplier_id"].isin(
        suppliers["supplier_id"].unique()
    )
).sum()

print(
    f"Sales products not found in inventory: "
    f"{sales_invalid_products}"
)

print(
    f"Purchase order products not found in suppliers: "
    f"{purchase_invalid_products}"
)

print(
    f"Purchase order suppliers not found in supplier table: "
    f"{purchase_invalid_suppliers}"
)


# 15. SAVE CLEANED DATA

print("\n--- SAVING CLEANED DATA ---")

sales_output = OUTPUT_DIR / "cleaned_sales.csv"
inventory_output = OUTPUT_DIR / "cleaned_inventory.csv"
suppliers_output = OUTPUT_DIR / "cleaned_suppliers.csv"
purchase_orders_output = OUTPUT_DIR / "cleaned_purchase_orders.csv"

sales.to_csv(
    sales_output,
    index=False
)

inventory.to_csv(
    inventory_output,
    index=False
)

suppliers.to_csv(
    suppliers_output,
    index=False
)

purchase_orders.to_csv(
    purchase_orders_output,
    index=False
)

print(f"Saved: {sales_output}")
print(f"Saved: {inventory_output}")
print(f"Saved: {suppliers_output}")
print(f"Saved: {purchase_orders_output}")


# 16. FINAL RECORD COUNT VALIDATION

print("\n--- FINAL CLEANED DATASET SIZES ---")

print(
    f"Cleaned sales records: "
    f"{len(sales)}"
)

print(
    f"Cleaned inventory records: "
    f"{len(inventory)}"
)

print(
    f"Cleaned supplier records: "
    f"{len(suppliers)}"
)

print(
    f"Cleaned purchase order records: "
    f"{len(purchase_orders)}"
)


# 17. ETL COMPLETION

print("\n" + "=" * 70)
print("ETL PROCESS COMPLETED SUCCESSFULLY")
print("=" * 70)