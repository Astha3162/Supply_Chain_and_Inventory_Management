
# SUPPLY CHAIN AND INVENTORY MANAGEMENT
# REORDER POINT CALCULATION

import os
import pandas as pd
import numpy as np


# 1. FILE PATHS

base_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sales_file = os.path.join(
    base_path,
    "output",
    "cleaned_sales.csv"
)

supplier_file = os.path.join(
    base_path,
    "output",
    "cleaned_suppliers.csv"
)

inventory_file = os.path.join(
    base_path,
    "output",
    "cleaned_inventory.csv"
)

output_file = os.path.join(
    base_path,
    "output",
    "reorder_points.csv"
)


# 2. LOAD DATA

sales = pd.read_csv(sales_file)

suppliers = pd.read_csv(supplier_file)

inventory = pd.read_csv(inventory_file)

sales["sale_date"] = pd.to_datetime(
    sales["sale_date"]
)

print("Sales data loaded:", len(sales))
print("Supplier data loaded:", len(suppliers))
print("Inventory data loaded:", len(inventory))


# 3. CALCULATE DAILY DEMAND

daily_demand = (
    sales.groupby(
        ["sale_date", "product_id"]
    )["quantity_sold"]
    .sum()
    .reset_index()
)

average_daily_demand = (
    daily_demand.groupby("product_id")
    ["quantity_sold"]
    .mean()
    .reset_index()
)

average_daily_demand.rename(
    columns={
        "quantity_sold": "average_daily_demand"
    },
    inplace=True
)


# 4. CALCULATE DEMAND VARIABILITY

demand_std = (
    daily_demand.groupby("product_id")
    ["quantity_sold"]
    .std()
    .reset_index()
)

demand_std.rename(
    columns={
        "quantity_sold": "demand_std_dev"
    },
    inplace=True
)

# If standard deviation is missing,
# replace it with zero.
demand_std["demand_std_dev"] = (
    demand_std["demand_std_dev"]
    .fillna(0)
)


# 5. PREPARE SUPPLIER LEAD TIME

supplier_lead_time = (
    suppliers.groupby("product_id")
    ["lead_time_days"]
    .mean()
    .reset_index()
)

supplier_lead_time.rename(
    columns={
        "lead_time_days": "average_lead_time_days"
    },
    inplace=True
)


# 6. COMBINE DEMAND AND LEAD TIME

reorder_data = average_daily_demand.merge(
    demand_std,
    on="product_id",
    how="left"
)

reorder_data = reorder_data.merge(
    supplier_lead_time,
    on="product_id",
    how="left"
)


# 7. CALCULATE SAFETY STOCK

# Safety Stock = Demand Variability × √Lead Time

reorder_data["safety_stock"] = (
    reorder_data["demand_std_dev"]
    * np.sqrt(
        reorder_data["average_lead_time_days"]
    )
)


# 8. CALCULATE REORDER POINT

# Reorder Point =
# Average Daily Demand × Lead Time + Safety Stock

reorder_data["reorder_point"] = (
    reorder_data["average_daily_demand"]
    * reorder_data["average_lead_time_days"]
    + reorder_data["safety_stock"]
)


# 9. ADD CURRENT INVENTORY

current_inventory = (
    inventory.groupby("product_id")
    ["stock_level"]
    .mean()
    .reset_index()
)

current_inventory.rename(
    columns={
        "stock_level": "average_current_stock"
    },
    inplace=True
)

reorder_data = reorder_data.merge(
    current_inventory,
    on="product_id",
    how="left"
)


# 10. DETERMINE REORDER STATUS

reorder_data["reorder_required"] = np.where(
    reorder_data["average_current_stock"]
    <= reorder_data["reorder_point"],
    "REORDER REQUIRED",
    "STOCK SUFFICIENT"
)


# 11. ROUND NUMERICAL VALUES

numeric_columns = [
    "average_daily_demand",
    "demand_std_dev",
    "average_lead_time_days",
    "safety_stock",
    "reorder_point",
    "average_current_stock"
]

reorder_data[numeric_columns] = (
    reorder_data[numeric_columns]
    .round(2)
)


# 12. SAVE RESULTS

reorder_data.to_csv(
    output_file,
    index=False
)


# 13. DISPLAY RESULTS

print("\n========================================")
print("REORDER POINT ANALYSIS")
print("========================================")

print(
    reorder_data.to_string(
        index=False
    )
)


# 14. SUMMARY

print("\n========================================")
print("REORDER SUMMARY")
print("========================================")

print(
    reorder_data[
        "reorder_required"
    ].value_counts()
)


# 15. FINAL MESSAGE

print("\nReorder point file saved to:")
print(output_file)

print("\nReorder point calculation completed successfully!")