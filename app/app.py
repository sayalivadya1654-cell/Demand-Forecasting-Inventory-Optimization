import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

DATA_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "model_data.csv"
)

PREDICTIONS_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "predictions.csv"
)

INVENTORY_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "inventory_recommendations.csv"
)


# ============================================================
# IMPORT APP MODULES
# ============================================================

sys.path.append(
    str(Path(__file__).resolve().parent)
)

from dashboard import show_dashboard
from forecasting import (
    load_model,
    predict_demand
)
from inventory import calculate_inventory


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SmartStock AI",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if not DATA_PATH.exists():

        return pd.DataFrame()

    return pd.read_csv(
        DATA_PATH
    )


df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "📦 SmartStock AI"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Demand Forecast",
        "Inventory Optimization"
    ]
)


# ============================================================
# DATA CHECK
# ============================================================

if df.empty:

    st.error(
        "Model data not found."
    )

    st.info(
        "Run the preprocessing and feature engineering scripts first."
    )

    st.stop()


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    show_dashboard(
        df
    )


# ============================================================
# DEMAND FORECAST
# ============================================================

elif page == "Demand Forecast":

    st.title(
        "🔮 Demand Forecasting"
    )

    st.write(
        "Generate demand predictions using the trained ML model."
    )

    model = load_model()

    if model is not None:

        products = sorted(
            df["Product"].unique()
        )

        selected_product = st.selectbox(
            "Select Product",
            products
        )

        stores = sorted(
            df[
                df["Product"] ==
                selected_product
            ]["Store"]
            .unique()
        )

        selected_store = st.selectbox(
            "Select Store",
            stores
        )

        filtered_df = df[
            (
                df["Product"]
                == selected_product
            )
            &
            (
                df["Store"]
                == selected_store
            )
        ].copy()

        if st.button(
            "Generate Forecast"
        ):

            predictions = predict_demand(
                filtered_df,
                model
            )

            if predictions is not None:

                filtered_df[
                    "Predicted_Demand"
                ] = predictions

                st.success(
                    "Demand prediction generated successfully."
                )

                st.metric(
                    "Average Predicted Demand",
                    f"{predictions.mean():.2f}"
                )

                st.dataframe(
                    filtered_df[
                        [
                            "Date",
                            "Product",
                            "Store",
                            "Inventory",
                            "Sales",
                            "Predicted_Demand"
                        ]
                    ].tail(30),
                    use_container_width=True,
                    hide_index=True
                )

                chart_df = (
                    filtered_df
                    .set_index("Date")
                    [
                        [
                            "Sales",
                            "Predicted_Demand"
                        ]
                    ]
                )

                st.subheader(
                    "Actual vs Predicted Demand"
                )

                st.line_chart(
                    chart_df
                )


# ============================================================
# INVENTORY OPTIMIZATION
# ============================================================

elif page == "Inventory Optimization":

    st.title(
        "📦 Inventory Optimization"
    )

    st.write(
        "Identify products that require inventory replenishment."
    )

    lead_time = st.slider(
        "Lead Time (days)",
        min_value=1,
        max_value=30,
        value=7
    )

    safety_stock_days = st.slider(
        "Safety Stock (days)",
        min_value=1,
        max_value=15,
        value=2
    )

    recommendations = calculate_inventory(
        df,
        lead_time=lead_time,
        safety_stock_days=safety_stock_days
    )

    # --------------------------------------------------------
    # STATUS COUNTS
    # --------------------------------------------------------

    urgent = (
        recommendations[
            "Reorder_Status"
        ]
        == "URGENT REORDER"
    ).sum()

    reorder = (
        recommendations[
            "Reorder_Status"
        ]
        == "REORDER"
    ).sum()

    healthy = (
        recommendations[
            "Reorder_Status"
        ]
        == "HEALTHY"
    ).sum()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🚨 Urgent Reorder",
            urgent
        )

    with col2:

        st.metric(
            "⚠️ Reorder",
            reorder
        )

    with col3:

        st.metric(
            "✅ Healthy",
            healthy
        )

    st.divider()

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    status_filter = st.selectbox(
        "Filter Status",
        [
            "ALL",
            "URGENT REORDER",
            "REORDER",
            "HEALTHY"
        ]
    )

    display_df = recommendations

    if status_filter != "ALL":

        display_df = recommendations[
            recommendations[
                "Reorder_Status"
            ]
            == status_filter
        ]

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    csv = display_df.to_csv(
        index=False
    )

    st.download_button(
        "Download Inventory Recommendations",
        data=csv,
        file_name="inventory_recommendations.csv",
        mime="text/csv"
    )