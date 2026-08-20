"""
Inventory optimization module.

Calculates safety stock, reorder point,
and recommended reorder quantity.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "model_data.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "inventory_recommendations.csv"
)


# ---------------------------------------------------------
# INVENTORY PARAMETERS
# ---------------------------------------------------------

LEAD_TIME_DAYS = 7

SERVICE_LEVEL_Z = 1.65

REVIEW_PERIOD_DAYS = 7


# ---------------------------------------------------------
# OPTIMIZATION
# ---------------------------------------------------------

def calculate_inventory_metrics(df):

    df = df.copy()

    # -----------------------------------------------------
    # PRODUCT LEVEL DEMAND
    # -----------------------------------------------------

    product_metrics = (
        df.groupby(
            [
                "Product_ID",
                "Product",
                "Category",
            ]
        )
        .agg(
            Average_Daily_Demand=(
                "Sales",
                "mean"
            ),

            Demand_Std=(
                "Sales",
                "std"
            ),

            Current_Inventory=(
                "Inventory",
                "last"
            ),

            Average_Inventory=(
                "Inventory",
                "mean"
            )
        )
        .reset_index()
    )

    # -----------------------------------------------------
    # HANDLE MISSING STANDARD DEVIATION
    # -----------------------------------------------------

    product_metrics["Demand_Std"] = (
        product_metrics["Demand_Std"]
        .fillna(0)
    )

    # -----------------------------------------------------
    # SAFETY STOCK
    # -----------------------------------------------------

    product_metrics["Safety_Stock"] = (
        SERVICE_LEVEL_Z
        * product_metrics["Demand_Std"]
        * (LEAD_TIME_DAYS ** 0.5)
    )

    # -----------------------------------------------------
    # REORDER POINT
    # -----------------------------------------------------

    product_metrics["Reorder_Point"] = (
        product_metrics["Average_Daily_Demand"]
        * LEAD_TIME_DAYS
        + product_metrics["Safety_Stock"]
    )

    # -----------------------------------------------------
    # TARGET STOCK
    # -----------------------------------------------------

    product_metrics["Target_Stock"] = (
        product_metrics["Average_Daily_Demand"]
        * (
            LEAD_TIME_DAYS
            + REVIEW_PERIOD_DAYS
        )
        + product_metrics["Safety_Stock"]
    )

    # -----------------------------------------------------
    # REORDER QUANTITY
    # -----------------------------------------------------

    product_metrics["Recommended_Reorder_Qty"] = (
        product_metrics["Target_Stock"]
        - product_metrics["Current_Inventory"]
    ).clip(lower=0)

    # -----------------------------------------------------
    # INVENTORY COVERAGE
    # -----------------------------------------------------

    product_metrics["Inventory_Coverage_Days"] = (
        product_metrics["Current_Inventory"]
        /
        product_metrics[
            "Average_Daily_Demand"
        ].replace(0, pd.NA)
    )

    # -----------------------------------------------------
    # REORDER STATUS
    # -----------------------------------------------------

    product_metrics["Reorder_Status"] = (
        product_metrics.apply(
            determine_reorder_status,
            axis=1
        )
    )

    # -----------------------------------------------------
    # ROUND VALUES
    # -----------------------------------------------------

    numeric_columns = [
        "Average_Daily_Demand",
        "Demand_Std",
        "Current_Inventory",
        "Average_Inventory",
        "Safety_Stock",
        "Reorder_Point",
        "Target_Stock",
        "Recommended_Reorder_Qty",
        "Inventory_Coverage_Days",
    ]

    product_metrics[numeric_columns] = (
        product_metrics[numeric_columns]
        .round(2)
    )

    return product_metrics


# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

def determine_reorder_status(row):

    inventory = row["Current_Inventory"]

    reorder_point = row["Reorder_Point"]

    if inventory <= reorder_point * 0.5:
        return "URGENT REORDER"

    if inventory <= reorder_point:
        return "REORDER"

    if inventory <= reorder_point * 1.5:
        return "MONITOR"

    return "HEALTHY"


# ---------------------------------------------------------
# SAVE RESULTS
# ---------------------------------------------------------

def save_recommendations(
    df,
    output_path=OUTPUT_PATH
):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Inventory recommendations saved to: "
        f"{output_path}"
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Model data not found: {DATA_PATH}"
        )

    print("Loading model data...")

    df = pd.read_csv(DATA_PATH)

    print(
        f"Input shape: {df.shape}"
    )

    print(
        "Calculating inventory recommendations..."
    )

    recommendations = calculate_inventory_metrics(
        df
    )

    print("\nInventory Optimization Results")
    print("-------------------------------")

    print(
        recommendations[
            [
                "Product_ID",
                "Product",
                "Average_Daily_Demand",
                "Current_Inventory",
                "Reorder_Point",
                "Recommended_Reorder_Qty",
                "Reorder_Status",
            ]
        ]
        .sort_values(
            "Recommended_Reorder_Qty",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )

    save_recommendations(
        recommendations
    )

    print(
        "\nInventory optimization completed successfully."
    )


if __name__ == "__main__":
    main()