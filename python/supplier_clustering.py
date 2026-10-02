import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# 1. LOAD SUPPLIER DATA

input_file = "../output/cleaned_suppliers.csv"

df = pd.read_csv(input_file)

print("Supplier data loaded:", len(df))


# 2. DISPLAY BASIC INFORMATION

print("\nSupplier Data:")
print(df.head())

print("\nColumns:")
print(df.columns.tolist())


# 3. CONVERT ORDER FREQUENCY INTO NUMERIC VALUES
# Approximate orders per week:
# Daily     = 7
# Weekly    = 1
# Biweekly  = 0.5
# Monthly   = 0.25

frequency_mapping = {
    "Daily": 7,
    "Weekly": 1,
    "Biweekly": 0.5,
    "Monthly": 0.25
}

df["order_frequency_per_week"] = (
    df["order_frequency"]
    .astype(str)
    .str.strip()
    .map(frequency_mapping)
)

# Check for values that could not be converted
if df["order_frequency_per_week"].isna().any():
    print("\nWarning: Some order frequency values could not be mapped.")
    print(
        df.loc[
            df["order_frequency_per_week"].isna(),
            "order_frequency"
        ].unique()
    )

# Remove rows with missing clustering values
df = df.dropna(
    subset=[
        "lead_time_days",
        "order_frequency_per_week"
    ]
)


# 4. SELECT FEATURES FOR CLUSTERING

features = df[
    [
        "lead_time_days",
        "order_frequency_per_week"
    ]
]

print("\nFeatures used for clustering:")
print(features.head())


# 5. STANDARDIZE THE FEATURES

scaler = StandardScaler()

scaled_features = scaler.fit_transform(features)


# 6. APPLY K-MEANS CLUSTERING

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

df["cluster"] = kmeans.fit_predict(scaled_features)


# 7. CREATE CLUSTER SUMMARY

cluster_summary = (
    df.groupby("cluster")
    .agg(
        supplier_count=("supplier_id", "count"),
        average_lead_time_days=("lead_time_days", "mean"),
        average_order_frequency_per_week=(
            "order_frequency_per_week",
            "mean"
        )
    )
    .reset_index()
)

print("\nSUPPLIER CLUSTER SUMMARY")
print(cluster_summary)


# 8. ADD CLUSTER PROFILE

def classify_cluster(row):
    if (
        row["average_lead_time_days"] <=
        cluster_summary["average_lead_time_days"].median()
        and
        row["average_order_frequency_per_week"] >=
        cluster_summary[
            "average_order_frequency_per_week"
        ].median()
    ):
        return "Short Lead Time / Frequent Orders"

    elif (
        row["average_lead_time_days"] >
        cluster_summary["average_lead_time_days"].median()
        and
        row["average_order_frequency_per_week"] <
        cluster_summary[
            "average_order_frequency_per_week"
        ].median()
    ):
        return "Long Lead Time / Less Frequent Orders"

    else:
        return "Moderate Supplier Pattern"


cluster_profiles = {}

for _, row in cluster_summary.iterrows():
    cluster_profiles[row["cluster"]] = classify_cluster(row)

df["cluster_profile"] = df["cluster"].map(cluster_profiles)


# 9. DISPLAY SUPPLIER CLUSTERS

print("\nSUPPLIER CLUSTERING RESULTS")

print(
    df[
        [
            "supplier_id",
            "supplier_name",
            "product_id",
            "lead_time_days",
            "order_frequency",
            "order_frequency_per_week",
            "cluster",
            "cluster_profile"
        ]
    ].head(20)
)


# 10. SAVE CLUSTER RESULTS

output_file = "../output/supplier_clusters.csv"

df[
    [
        "supplier_id",
        "supplier_name",
        "product_id",
        "lead_time_days",
        "order_frequency",
        "order_frequency_per_week",
        "cluster",
        "cluster_profile"
    ]
].to_csv(
    output_file,
    index=False
)

print("\nSupplier clustering results saved to:")
print(output_file)


# 11. CREATE VISUALIZATION

plt.figure(figsize=(10, 6))

plt.scatter(
    df["lead_time_days"],
    df["order_frequency_per_week"],
    c=df["cluster"],
    s=80
)

plt.xlabel("Lead Time (Days)")
plt.ylabel("Order Frequency (Orders per Week)")
plt.title("Supplier Clustering Based on Lead Time and Order Frequency")
plt.grid(True)

plt.tight_layout()

chart_file = "../output/supplier_clusters.png"

plt.savefig(chart_file, dpi=300)

plt.show()

print("\nSupplier clustering chart saved to:")
print(chart_file)

print("\nSupplier clustering completed successfully.")