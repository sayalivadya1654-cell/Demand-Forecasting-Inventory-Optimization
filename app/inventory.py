import pandas as pd
import streamlit as st


# ============================================================
# INVENTORY CALCULATION
# ============================================================

def calculate_inventory(
    df,
    lead_time=7,
    safety_stock_days=2
):

    required_columns = [
        "Product_ID",
        "Product",
        "Inventory",
        "Sales"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )

    inventory_df = (
        df.groupby(
            [
                "Product_ID",
                "Product"
            ],
            as_index=False
        )
        .agg(
            Average_Daily_Demand=(
                "Sales",
                "mean"
            ),
            Current_Inventory=(
                "Inventory",
                "last"
            )
        )
    )

    # --------------------------------------------------------
    # Safety stock
    # --------------------------------------------------------

    inventory_df[
        "Safety_Stock"
    ] = (
        inventory_df[
            "Average_Daily_Demand"
        ]
        * safety_stock_days
    )

    # --------------------------------------------------------
    # Reorder point
    # --------------------------------------------------------

    inventory_df[
        "Reorder_Point"
    ] = (
        inventory_df[
            "Average_Daily_Demand"
        ]
        * lead_time
        +
        inventory_df[
            "Safety_Stock"
        ]
    )

    # --------------------------------------------------------
    # Recommended quantity
    # --------------------------------------------------------

    inventory_df[
        "Recommended_Reorder_Qty"
    ] = (
        inventory_df[
            "Reorder_Point"
        ]
        -
        inventory_df[
            "Current_Inventory"
        ]
    )

    inventory_df[
        "Recommended_Reorder_Qty"
    ] = (
        inventory_df[
            "Recommended_Reorder_Qty"
        ]
        .clip(lower=0)
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    def get_status(row):

        inventory = row[
            "Current_Inventory"
        ]

        reorder_point = row[
            "Reorder_Point"
        ]

        if inventory <= reorder_point * 0.5:

            return "URGENT REORDER"

        elif inventory <= reorder_point:

            return "REORDER"

        else:

            return "HEALTHY"

    inventory_df[
        "Reorder_Status"
    ] = inventory_df.apply(
        get_status,
        axis=1
    )

    # --------------------------------------------------------
    # Round values
    # --------------------------------------------------------

    numeric_columns = [
        "Average_Daily_Demand",
        "Safety_Stock",
        "Reorder_Point",
        "Recommended_Reorder_Qty"
    ]

    inventory_df[
        numeric_columns
    ] = inventory_df[
        numeric_columns
    ].round(2)

    return inventory_df