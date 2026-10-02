
# SUPPLY CHAIN AND INVENTORY MANAGEMENT
# DEMAND FORECASTING

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 1. FILE PATHS

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

input_file = os.path.join(
    base_path,
    "output",
    "cleaned_sales.csv"
)

output_file = os.path.join(
    base_path,
    "output",
    "forecasts.csv"
)

chart_file = os.path.join(
    base_path,
    "output",
    "demand_forecast.png"
)


# 2. LOAD SALES DATA

df = pd.read_csv(input_file)

df["sale_date"] = pd.to_datetime(df["sale_date"])

print("Sales data loaded successfully.")
print("Rows:", len(df))


# 3. PREPARE MONTHLY DEMAND

monthly_sales = (
    df.groupby(
        [
            pd.Grouper(key="sale_date", freq="MS"),
            "product_id"
        ]
    )["quantity_sold"]
    .sum()
    .reset_index()
)

monthly_sales = monthly_sales.sort_values(
    ["product_id", "sale_date"]
)

print("\nMonthly sales data:")
print(monthly_sales.head(10))

# 4. FORECAST NEXT MONTH DEMAND

forecast_results = []

for product in monthly_sales["product_id"].unique():

    product_data = monthly_sales[
        monthly_sales["product_id"] == product
    ].copy()

    product_data = product_data.sort_values("sale_date")

    # Create numerical time index
    product_data["month_number"] = np.arange(
        len(product_data)
    )

    # Need at least 2 months for regression
    if len(product_data) < 2:
        continue

    X = product_data[["month_number"]]

    y = product_data["quantity_sold"]

    # Create model
    model = LinearRegression()

    model.fit(X, y)

    # Predict next month
    next_month_number = pd.DataFrame({
      "month_number": [
        product_data["month_number"].max() + 1
      ]
    })

    predicted_demand = model.predict(
      next_month_number
    )[0]

    # Demand cannot be negative
    predicted_demand = max(
        0,
        predicted_demand
    )

    next_month = (
        product_data["sale_date"].max()
        + pd.DateOffset(months=1)
    )

    forecast_results.append({
        "product_id": product,
        "forecast_month": next_month.strftime("%Y-%m"),
        "predicted_demand": round(
            predicted_demand,
            2
        )
    })

# 5. CREATE FORECAST DATAFRAME

forecast_df = pd.DataFrame(
    forecast_results
)

# 6. SAVE FORECAST RESULTS

forecast_df.to_csv(
    output_file,
    index=False
)

# 7. DISPLAY RESULTS

print("\n========================================")
print("NEXT MONTH DEMAND FORECAST")
print("========================================")

print(forecast_df)


# 8. VISUALIZE DEMAND

plt.figure(figsize=(10, 6))

for product in monthly_sales["product_id"].unique():

    product_data = monthly_sales[
        monthly_sales["product_id"] == product
    ]

    plt.plot(
        product_data["sale_date"],
        product_data["quantity_sold"],
        marker="o",
        label=product
    )


plt.title("Monthly Product Demand")
plt.xlabel("Date")
plt.ylabel("Quantity Sold")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    chart_file,
    dpi=300
)

plt.show()


# 9. FINAL MESSAGE

print("\nForecast file saved to:")
print(output_file)

print("\nDemand chart saved to:")
print(chart_file)

print("\nDemand forecasting completed successfully!")