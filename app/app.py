import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "Data" / "processed" / "model_data.csv"
PREDICTIONS_PATH = PROJECT_ROOT / "Data" / "processed" / "predictions.csv"
INVENTORY_PATH = PROJECT_ROOT / "Data" / "processed" / "inventory_recommendations.csv"


# ============================================================
# APP MODULES
# ============================================================

APP_DIR = Path(__file__).resolve().parent

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from forecasting import load_model, predict_demand
from inventory import calculate_inventory


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SmartStock AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# THEME STATE
# ============================================================
# This is the one thing that makes the whole rest of the file work.
# Every widget in Streamlit reruns the ENTIRE script top-to-bottom on
# every interaction. session_state is the only thing that survives
# between reruns, so we store the chosen theme there.

if "theme" not in st.session_state:
    st.session_state.theme = "light"

with st.sidebar:
    dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=(st.session_state.theme == "dark"),
        help="Switch between light and dark UI themes"
    )
    st.session_state.theme = "dark" if dark_mode else "light"

theme_name = st.session_state.theme


# ============================================================
# THEME DEFINITIONS
# ============================================================
# Two flat dictionaries of colors. Nothing fancy — just every color
# the CSS below needs, named once, so light/dark always stay in sync
# and you never have to hunt through CSS to fix a contrast bug.

THEMES = {
    "light": {
        "app_bg":         "#f8fafc",
        "text_primary":   "#0f172a",
        "text_secondary": "#334155",
        "text_muted":     "#64748b",
        "sidebar_bg":     "#0f172a",
        "sidebar_text":   "#ffffff",
        "sidebar_muted":  "#cbd5e1",
        "card_bg":        "#ffffff",
        "card_border":    "#e2e8f0",
        "hero_grad_a":    "#0f172a",
        "hero_grad_b":    "#1e3a8a",
        "hero_text":      "#dbeafe",
        "input_bg":       "#ffffff",
        "input_text":     "#0f172a",
        "input_border":   "#cbd5e1",
        "shadow":         "rgba(15, 23, 42, 0.08)",
    },
    "dark": {
        "app_bg":         "#0b1120",
        "text_primary":   "#f8fafc",
        "text_secondary": "#cbd5e1",
        "text_muted":     "#94a3b8",
        "sidebar_bg":     "#000000",
        "sidebar_text":   "#f8fafc",
        "sidebar_muted":  "#94a3b8",
        "card_bg":        "#111827",
        "card_border":    "#293548",
        "hero_grad_a":    "#1e293b",
        "hero_grad_b":    "#1d4ed8",
        "hero_text":      "#dbeafe",
        "input_bg":       "#1e293b",
        "input_text":     "#f8fafc",
        "input_border":   "#334155",
        "shadow":         "rgba(0, 0, 0, 0.4)",
    },
}

t = THEMES[theme_name]


# ============================================================
# CUSTOM CSS (built from the theme dict above)
# ============================================================
# Every color reference below is t["something"] instead of a hardcoded
# hex code. That's the whole trick: flip theme_name, every rule
# repaints, contrast is guaranteed because light/dark pairs were
# chosen together on purpose (e.g. card_bg vs text_primary).

st.markdown(
    f"""
    <style>

    /* ---------- GLOBAL APP ---------- */
    .stApp {{
        background-color: {t['app_bg']};
        color: {t['text_primary']};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    h1 {{ color: {t['text_primary']} !important; font-weight: 800 !important; }}
    h2 {{ color: {t['text_primary']} !important; font-weight: 750 !important; }}
    h3 {{ color: {t['text_secondary']} !important; font-weight: 700 !important; }}
    p, .stMarkdown {{ color: {t['text_secondary']} !important; }}
    label {{ color: {t['text_secondary']} !important; font-weight: 600 !important; }}
    .stCaption {{ color: {t['text_muted']} !important; }}

    /* ---------- SIDEBAR ---------- */
    section[data-testid="stSidebar"] {{
        background-color: {t['sidebar_bg']} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {t['sidebar_text']} !important;
    }}
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stCaption {{
        color: {t['sidebar_muted']} !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: #334155 !important;
    }}

    /* ---------- HERO SECTION ---------- */
    .hero {{
        background: linear-gradient(135deg, {t['hero_grad_a']}, {t['hero_grad_b']});
        padding: 32px;
        border-radius: 18px;
        color: #ffffff !important;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px {t['shadow']};
    }}
    .hero h1 {{
        color: #ffffff !important;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 8px;
    }}
    .hero p {{
        color: {t['hero_text']} !important;
        font-size: 17px;
        line-height: 1.6;
    }}

    /* ---------- SECTION TITLES ---------- */
    .section-title {{
        font-size: 24px;
        font-weight: 800;
        margin-top: 25px;
        margin-bottom: 15px;
        color: {t['text_primary']} !important;
    }}

    /* ---------- KPI CARDS ---------- */
    .metric-card {{
        background: {t['card_bg']};
        padding: 20px;
        border-radius: 14px;
        border: 1px solid {t['card_border']};
        box-shadow: 0 2px 8px {t['shadow']};
        text-align: center;
    }}
    .metric-title {{
        font-size: 14px;
        color: {t['text_muted']} !important;
        margin-bottom: 8px;
        font-weight: 600;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 800;
        color: {t['text_primary']} !important;
    }}

    /* ---------- STATUS BOXES ---------- */
    .urgent-box {{
        background-color: #fee2e2; color: #991b1b !important;
        padding: 18px; border-radius: 12px; border-left: 5px solid #dc2626;
    }}
    .warning-box {{
        background-color: #fef3c7; color: #92400e !important;
        padding: 18px; border-radius: 12px; border-left: 5px solid #d97706;
    }}
    .success-box {{
        background-color: #dcfce7; color: #166534 !important;
        padding: 18px; border-radius: 12px; border-left: 5px solid #16a34a;
    }}

    /* ---------- STREAMLIT METRICS ---------- */
    [data-testid="stMetricLabel"] {{ color: {t['text_muted']} !important; font-weight: 600 !important; }}
    [data-testid="stMetricValue"] {{ color: {t['text_primary']} !important; font-weight: 800 !important; }}
    [data-testid="stMetricDelta"] {{ color: {t['text_secondary']} !important; }}

    /* ---------- INPUTS (selectbox, slider, date, toggle) ---------- */
    [data-testid="stSelectbox"] label,
    [data-testid="stSlider"] label {{
        color: {t['text_secondary']} !important;
        font-weight: 650 !important;
    }}
    [data-baseweb="select"] {{
        background-color: {t['input_bg']} !important;
        border-color: {t['input_border']} !important;
    }}
    [data-baseweb="select"] * {{
        color: {t['input_text']} !important;
    }}
    [data-testid="stDateInput"] input {{
        background-color: {t['input_bg']} !important;
        color: {t['input_text']} !important;
    }}

    /* ---------- BUTTONS ---------- */
    .stButton button {{
        border-radius: 10px;
        font-weight: 700;
        padding: 0.55rem 1.2rem;
    }}
    .stDownloadButton button {{
        border-radius: 10px;
        font-weight: 700;
        border: 1px solid {t['input_border']};
    }}

    /* ---------- DATAFRAME / TABLE ---------- */
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
    }}

    /* ---------- DIVIDER ---------- */
    hr {{ border-color: {t['card_border']} !important; }}

    /* ---------- FOOTER ---------- */
    .footer {{
        text-align: center;
        color: {t['text_muted']} !important;
        padding: 30px;
        font-size: 13px;
        line-height: 1.7;
    }}
    .footer strong {{ color: {t['text_secondary']} !important; }}

    /* ---------- ALERTS ---------- */
    [data-testid="stAlert"] {{ border-radius: 10px; }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


df = load_data()


# ============================================================
# SIDEBAR (branding + navigation)
# ============================================================

with st.sidebar:

    st.markdown(
        f"""
        <h1 style="color:{t['sidebar_text']};">📦 SmartStock AI</h1>
        <p style="color:{t['sidebar_muted']};">
        Demand Forecasting & Inventory Intelligence
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "🔮 Demand Forecast",
            "📦 Inventory Optimization"
        ]
    )

    st.divider()

    st.caption("AI-powered inventory decision support")
    st.caption("Machine Learning • Python • SQL • Streamlit")


# ============================================================
# DATA VALIDATION
# ============================================================

if df.empty:
    st.error("❌ Model data not found.")
    st.info("Run data_preprocessing.py and feature_engineering.py first.")
    st.stop()


# ============================================================
# COMMON METRICS
# ============================================================

total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
total_inventory = df["Inventory"].sum() if "Inventory" in df.columns else 0
total_products = df["Product"].nunique() if "Product" in df.columns else 0
total_stores = df["Store"].nunique() if "Store" in df.columns else 0


# ============================================================
# 1) DASHBOARD
# ============================================================

if page == "📊 Dashboard":

    st.markdown(
        """
        <div class="hero">
        <h1>📦 SmartStock AI</h1>
        <p>Intelligent Demand Forecasting & Inventory Optimization Platform</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-title">Business Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""<div class="metric-card">
            <div class="metric-title">Total Sales</div>
            <div class="metric-value">{total_sales:,.0f}</div>
            </div>""",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""<div class="metric-card">
            <div class="metric-title">Current Inventory</div>
            <div class="metric-value">{total_inventory:,.0f}</div>
            </div>""",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""<div class="metric-card">
            <div class="metric-title">Products</div>
            <div class="metric-value">{total_products}</div>
            </div>""",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""<div class="metric-card">
            <div class="metric-title">Stores</div>
            <div class="metric-value">{total_stores}</div>
            </div>""",
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown('<div class="section-title">Sales Analytics</div>', unsafe_allow_html=True)

    if "Date" in df.columns:
        min_date = df["Date"].min()
        max_date = df["Date"].max()

        selected_dates = st.date_input(
            "Select Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )

        if len(selected_dates) == 2:
            start_date = pd.Timestamp(selected_dates[0])
            end_date = pd.Timestamp(selected_dates[1])
            filtered_data = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()
        else:
            filtered_data = df.copy()
    else:
        filtered_data = df.copy()

    if not filtered_data.empty:
        daily_sales = filtered_data.groupby("Date")["Sales"].sum()
        st.subheader("📈 Daily Sales Trend")
        st.line_chart(daily_sales)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top Products")
        product_sales = (
            filtered_data.groupby("Product")["Sales"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        st.bar_chart(product_sales)

    with col2:
        st.subheader("🏪 Store Performance")
        store_sales = (
            filtered_data.groupby("Store")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(store_sales)


# ============================================================
# 2) DEMAND FORECASTING
# ============================================================

elif page == "🔮 Demand Forecast":

    st.markdown(
        """
        <div class="hero">
        <h1>🔮 Demand Forecasting</h1>
        <p>Predict future product demand using the trained Machine Learning model.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    model = load_model()

    if model is None:
        st.error("Demand forecasting model could not be loaded.")
        st.stop()

    st.success("✅ Demand forecasting model loaded successfully.")

    products = sorted(df["Product"].dropna().unique())
    selected_product = st.selectbox("🛍️ Select Product", products)

    stores = sorted(df[df["Product"] == selected_product]["Store"].dropna().unique())
    selected_store = st.selectbox("🏪 Select Store", stores)

    filtered_df = df[
        (df["Product"] == selected_product) & (df["Store"] == selected_store)
    ].copy()

    if filtered_df.empty:
        st.warning("No data available for this product and store.")
        st.stop()

    if st.button("🔮 Generate Demand Forecast", type="primary"):

        try:
            predictions = predict_demand(filtered_df, model)

            if predictions is not None:
                filtered_df["Predicted_Demand"] = predictions

                avg_prediction = predictions.mean()
                max_prediction = predictions.max()
                min_prediction = predictions.min()

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Average Predicted Demand", f"{avg_prediction:.2f}")
                with col2:
                    st.metric("Peak Predicted Demand", f"{max_prediction:.2f}")
                with col3:
                    st.metric("Minimum Predicted Demand", f"{min_prediction:.2f}")

                # ------------------------------------------------
                # ACCURACY METRICS
                # ------------------------------------------------
                # These compare the model's Predicted_Demand against the
                # actual historical Sales for the SAME rows. This is a
                # backtest, not a forward-looking accuracy score — it
                # tells you how well the model fits this product/store's
                # known history, not how it will do on unseen future dates.

                if "Sales" in filtered_df.columns:

                    actual = filtered_df["Sales"].values
                    predicted = filtered_df["Predicted_Demand"].values

                    mae = mean_absolute_error(actual, predicted)
                    rmse = np.sqrt(mean_squared_error(actual, predicted))

                    nonzero_mask = actual != 0
                    if nonzero_mask.any():
                        mape = np.mean(
                            np.abs(
                                (actual[nonzero_mask] - predicted[nonzero_mask])
                                / actual[nonzero_mask]
                            )
                        ) * 100
                    else:
                        mape = None

                    st.divider()
                    st.subheader("🎯 Model Accuracy (this Product/Store)")

                    acc_col1, acc_col2, acc_col3 = st.columns(3)

                    with acc_col1:
                        st.metric("MAE", f"{mae:.2f}", help="Average absolute error in units sold")
                    with acc_col2:
                        st.metric("RMSE", f"{rmse:.2f}", help="Penalizes large misses more than MAE")
                    with acc_col3:
                        if mape is not None:
                            st.metric("MAPE", f"{mape:.1f}%", help="Average percentage error")
                        else:
                            st.metric("MAPE", "N/A", help="Undefined when actual sales are 0")

                else:
                    st.divider()
                    st.warning(
                        "⚠️ Model Accuracy section skipped: no 'Sales' column found "
                        f"in the filtered data. Columns available: {list(filtered_df.columns)}"
                    )

                st.divider()

                st.subheader("📈 Actual vs Predicted Demand")
                chart_df = filtered_df.set_index("Date")[["Sales", "Predicted_Demand"]]
                st.line_chart(chart_df)

                st.subheader("📋 Forecast Results")

                display_columns = ["Date", "Product", "Store", "Inventory", "Sales", "Predicted_Demand"]
                available_columns = [c for c in display_columns if c in filtered_df.columns]

                st.dataframe(
                    filtered_df[available_columns].tail(30),
                    width="stretch",
                    hide_index=True
                )

                csv_data = filtered_df.to_csv(index=False)

                st.download_button(
                    "⬇️ Download Forecast",
                    data=csv_data,
                    file_name="demand_forecast.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error("Prediction failed.")
            st.exception(e)


# ============================================================
# 3) INVENTORY OPTIMIZATION
# ============================================================

elif page == "📦 Inventory Optimization":

    st.markdown(
        """
        <div class="hero">
        <h1>📦 Inventory Optimization</h1>
        <p>Identify products that require replenishment and optimize stock levels.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        lead_time = st.slider("🚚 Lead Time (days)", min_value=1, max_value=30, value=7)

    with col2:
        safety_stock_days = st.slider("🛡️ Safety Stock (days)", min_value=1, max_value=15, value=2)

    recommendations = calculate_inventory(df, lead_time=lead_time, safety_stock_days=safety_stock_days)

    urgent = (recommendations["Reorder_Status"] == "URGENT REORDER").sum()
    reorder = (recommendations["Reorder_Status"] == "REORDER").sum()
    healthy = (recommendations["Reorder_Status"] == "HEALTHY").sum()

    st.markdown('<div class="section-title">Inventory Health</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.error(f"🚨 Urgent Reorder: {urgent}")
    with col2:
        st.warning(f"⚠️ Reorder Required: {reorder}")
    with col3:
        st.success(f"✅ Healthy Stock: {healthy}")

    st.divider()

    status_filter = st.selectbox(
        "Filter Inventory Status",
        ["ALL", "URGENT REORDER", "REORDER", "HEALTHY"]
    )

    if status_filter == "ALL":
        display_df = recommendations.copy()
    else:
        display_df = recommendations[recommendations["Reorder_Status"] == status_filter].copy()

    st.subheader("📋 Inventory Recommendations")

    st.dataframe(display_df, width="stretch", hide_index=True)

    csv_data = display_df.to_csv(index=False)

    st.download_button(
        "⬇️ Download Inventory Recommendations",
        data=csv_data,
        file_name="inventory_recommendations.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
    SmartStock AI • Demand Forecasting & Inventory Optimization
    <br>
    Built with Python • Pandas • Scikit-Learn • Streamlit • SQL
    </div>
    """,
    unsafe_allow_html=True
)