import pandas as pd
from pathlib import Path

# 1. DEFINE FILE LOCATIONS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


sales_file = DATA_DIR / "sales_data.csv"
inventory_file = DATA_DIR / "inventory_data.csv"
suppliers_file = DATA_DIR / "suppliers_data.csv"
purchase_orders_file = DATA_DIR / "purchase_orders_data.csv"


# 2. LOAD THE CSV FILES

sales = pd.read_csv(sales_file)
inventory = pd.read_csv(inventory_file)
suppliers = pd.read_csv(suppliers_file)
purchase_orders = pd.read_csv(purchase_orders_file)

# 3. DISPLAY BASIC INFORMATION

print("\n" + "=" * 70)
print("SUPPLY CHAIN AND INVENTORY MANAGEMENT - DATA EXPLORATION")
print("=" * 70)


print("\n--- DATASET SIZES ---")

print(f"Sales records: {sales.shape[0]}")
print(f"Inventory records: {inventory.shape[0]}")
print(f"Supplier records: {suppliers.shape[0]}")
print(f"Purchase order records: {purchase_orders.shape[0]}")


# 4. DISPLAY COLUMN NAMES

print("\n--- COLUMN NAMES ---")

print("\nSales:")
print(list(sales.columns))

print("\nInventory:")
print(list(inventory.columns))

print("\nSuppliers:")
print(list(suppliers.columns))

print("\nPurchase Orders:")
print(list(purchase_orders.columns))



# 5. DISPLAY FIRST FIVE ROWS

print("\n--- FIRST FIVE SALES RECORDS ---")
print(sales.head())

print("\n--- FIRST FIVE INVENTORY RECORDS ---")
print(inventory.head())

print("\n--- FIRST FIVE SUPPLIER RECORDS ---")
print(suppliers.head())

print("\n--- FIRST FIVE PURCHASE ORDER RECORDS ---")
print(purchase_orders.head())


# 6. CHECK DATA TYPES

print("\n--- DATA TYPES ---")

print("\nSales:")
print(sales.dtypes)

print("\nInventory:")
print(inventory.dtypes)

print("\nSuppliers:")
print(suppliers.dtypes)

print("\nPurchase Orders:")
print(purchase_orders.dtypes)


# 7. CHECK MISSING VALUES

print("\n--- MISSING VALUES ---")

print("\nSales:")
print(sales.isnull().sum())

print("\nInventory:")
print(inventory.isnull().sum())

print("\nSuppliers:")
print(suppliers.isnull().sum())

print("\nPurchase Orders:")
print(purchase_orders.isnull().sum())


# 8. CHECK DUPLICATES

print("\n--- DUPLICATE RECORDS ---")

print(f"Sales duplicates: {sales.duplicated().sum()}")
print(f"Inventory duplicates: {inventory.duplicated().sum()}")
print(f"Supplier duplicates: {suppliers.duplicated().sum()}")
print(f"Purchase order duplicates: {purchase_orders.duplicated().sum()}")


# 9. CONVERT DATE COLUMNS

sales["Sale_Date"] = pd.to_datetime(sales["Sale_Date"])
inventory["Last_Updated"] = pd.to_datetime(inventory["Last_Updated"])
purchase_orders["Order_Date"] = pd.to_datetime(purchase_orders["Order_Date"])
purchase_orders["Arrival_Date"] = pd.to_datetime(
    purchase_orders["Arrival_Date"]
)


# 10. DATE RANGE ANALYSIS

print("\n--- DATE RANGES ---")

print(
    "Sales:",
    sales["Sale_Date"].min().date(),
    "to",
    sales["Sale_Date"].max().date()
)

print(
    "Inventory:",
    inventory["Last_Updated"].min().date(),
    "to",
    inventory["Last_Updated"].max().date()
)

print(
    "Purchase Orders:",
    purchase_orders["Order_Date"].min().date(),
    "to",
    purchase_orders["Order_Date"].max().date()
)


# 11. NUMERICAL SUMMARY

print("\n--- SALES NUMERICAL SUMMARY ---")
print(
    sales[
        ["Quantity_Sold", "Revenue"]
    ].describe()
)


print("\n--- INVENTORY NUMERICAL SUMMARY ---")
print(
    inventory[
        ["Stock_Level", "Reorder_Level"]
    ].describe()
)


print("\n--- PURCHASE ORDER NUMERICAL SUMMARY ---")
print(
    purchase_orders[
        ["Quantity"]
    ].describe()
)


# 12. UNIQUE VALUES

print("\n--- UNIQUE COUNTS ---")

print(f"Unique products in sales: {sales['Product_ID'].nunique()}")
print(f"Unique stores in sales: {sales['Store_ID'].nunique()}")

print(
    f"Unique products in inventory: "
    f"{inventory['Product_ID'].nunique()}"
)

print(
    f"Unique suppliers: "
    f"{suppliers['Supplier_ID'].nunique()}"
)

print(
    f"Unique products supplied: "
    f"{suppliers['Product_ID'].nunique()}"
)


# 13. BASIC BUSINESS METRICS

print("\n--- BASIC BUSINESS METRICS ---")

print(
    f"Total quantity sold: "
    f"{sales['Quantity_Sold'].sum():,.0f}"
)

print(
    f"Total revenue: "
    f"{sales['Revenue'].sum():,.2f}"
)

print(
    f"Average quantity per sale: "
    f"{sales['Quantity_Sold'].mean():,.2f}"
)

print(
    f"Average revenue per sale: "
    f"{sales['Revenue'].mean():,.2f}"
)

print(
    f"Average supplier lead time: "
    f"{suppliers['Lead_Time (days)'].mean():,.2f} days"
)


# 14. INVENTORY REORDER CHECK

inventory["Reorder_Status"] = inventory.apply(
    lambda row:
    "REORDER REQUIRED"
    if row["Stock_Level"] <= row["Reorder_Level"]
    else "STOCK SUFFICIENT",
    axis=1
)


print("\n--- INVENTORY REORDER STATUS ---")

print(
    inventory["Reorder_Status"].value_counts()
)


# 15. FINAL MESSAGE

print("\n" + "=" * 70)
print("DATA EXPLORATION COMPLETED")
print("=" * 70)