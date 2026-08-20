import pandas as pd
import streamlit as st

from inventory import calculate_inventory


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard(df):

    st.title(
        "📊 Demand Forecasting & Inventory Dashboard"
    )

    st.markdown(
        "Monitor sales, demand and inventory performance."
    )

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_sales = int(
        df["Sales"].sum()
    )

    average_daily_demand = round(
        df["Sales"].mean(),
        2
    )

    total_inventory = int(
        df["Inventory"].sum()
    )

    total_products = (
        df["Product_ID"]
        .nunique()
    )

    # ========================================================
    # KPI DISPLAY
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Sales",
            f"{total_sales:,}"
        )

    with col2:

        st.metric(
            "Avg Daily Demand",
            f"{average_daily_demand:.2f}"
        )

    with col3:

        st.metric(
            "Total Inventory",
            f"{total_inventory:,}"
        )

    with col4:

        st.metric(
            "Products",
            total_products
        )

    st.divider()

    # ========================================================
    # PRODUCT FILTER
    # ========================================================

    products = sorted(
        df["Product"].unique()
    )

    selected_product = st.selectbox(
        "Select Product",
        ["All Products"] + products
    )

    if selected_product != "All Products":

        filtered_df = df[
            df["Product"] == selected_product
        ]

    else:

        filtered_df = df

    # ========================================================
    # SALES TREND
    # ========================================================

    st.subheader(
        "Sales Trend"
    )

    sales_trend = (
        filtered_df
        .groupby("Date")["Sales"]
        .sum()
    )

    st.line_chart(
        sales_trend
    )

    # ========================================================
    # INVENTORY STATUS
    # ========================================================

    st.subheader(
        "Inventory Status"
    )

    inventory_df = calculate_inventory(
        filtered_df
    )

    st.dataframe(
        inventory_df,
        use_container_width=True,
        hide_index=True
    )