import pandas as pd
import streamlit as st

from inventory import calculate_inventory


# ============================================================
# DASHBOARD
# ============================================================
# NOTE: app.py currently builds its Dashboard page inline instead of
# calling this function, so this file is a standalone reusable version
# — useful if you want to embed the same dashboard elsewhere, or reuse
# it as a component. Kept in sync with the same inventory logic used
# by app.py's Inventory Optimization page.

def show_dashboard(df, lead_time=7, safety_stock_days=2):
    """
    Render the summary dashboard for a given dataframe.

    lead_time / safety_stock_days are passed straight through to
    calculate_inventory() so this dashboard's inventory table matches
    whatever the user configured elsewhere in the app, instead of
    silently falling back to defaults.
    """

    st.title("📊 Demand Forecasting & Inventory Dashboard")
    st.markdown("Monitor sales, demand and inventory performance.")

    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    total_sales = int(df["Sales"].sum()) if "Sales" in df.columns else 0
    average_daily_demand = round(df["Sales"].mean(), 2) if "Sales" in df.columns else 0
    total_inventory = int(df["Inventory"].sum()) if "Inventory" in df.columns else 0

    # Product_ID isn't guaranteed to exist (app.py's model_data.csv
    # only guarantees "Product"), so fall back gracefully.
    if "Product_ID" in df.columns:
        total_products = df["Product_ID"].nunique()
    elif "Product" in df.columns:
        total_products = df["Product"].nunique()
    else:
        total_products = 0

    # ========================================================
    # KPI DISPLAY
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Sales", f"{total_sales:,}")

    with col2:
        st.metric("Avg Daily Demand", f"{average_daily_demand:.2f}")

    with col3:
        st.metric("Total Inventory", f"{total_inventory:,}")

    with col4:
        st.metric("Products", total_products)

    st.divider()

    # ========================================================
    # PRODUCT FILTER
    # ========================================================

    products = sorted(df["Product"].dropna().unique()) if "Product" in df.columns else []

    selected_product = st.selectbox(
        "Select Product",
        ["All Products"] + products
    )

    if selected_product != "All Products":
        filtered_df = df[df["Product"] == selected_product]
    else:
        filtered_df = df

    # ========================================================
    # SALES TREND
    # ========================================================

    st.subheader("Sales Trend")

    if "Date" in filtered_df.columns and "Sales" in filtered_df.columns:
        sales_trend = filtered_df.groupby("Date")["Sales"].sum()
        st.line_chart(sales_trend)
    else:
        st.info("Sales trend needs 'Date' and 'Sales' columns.")

    # ========================================================
    # INVENTORY STATUS
    # ========================================================

    st.subheader("Inventory Status")

    inventory_df = calculate_inventory(
        filtered_df,
        lead_time=lead_time,
        safety_stock_days=safety_stock_days
    )

    st.dataframe(
        inventory_df,
        use_container_width=True,
        hide_index=True
    )