from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "demand_forecasting_model.pkl"
)

DATA_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "model_data.csv"
)


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    if not MODEL_PATH.exists():

        st.error(
            f"Model not found:\n{MODEL_PATH}"
        )

        return None

    return joblib.load(
        MODEL_PATH
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    if not DATA_PATH.exists():

        st.error(
            f"Model data not found:\n{DATA_PATH}"
        )

        return pd.DataFrame()

    return pd.read_csv(
        DATA_PATH
    )


# ============================================================
# GET EXACT MODEL FEATURES
# ============================================================

def get_model_features(model):

    if hasattr(
        model,
        "feature_names_in_"
    ):

        return list(
            model.feature_names_in_
        )

    # Fallback
    return [
        "Price",
        "Discount",
        "Promotion",
        "Inventory",
        "Year",
        "Month",
        "Day",
        "DayOfWeek",
        "WeekOfYear",
        "Quarter",
        "IsWeekend",
        "DiscountAmount",
        "PriceAfterDiscount",
        "Sales_Lag_1",
        "Sales_Lag_7",
        "Sales_Lag_14",
        "Sales_Lag_30",
        "Sales_Rolling_7",
        "Sales_Rolling_14",
        "Sales_Rolling_30",
        "Inventory_to_Sales"
    ]


# ============================================================
# PREDICT DEMAND
# ============================================================

def predict_demand(
    data,
    model
):

    if model is None:

        return None

    # --------------------------------------------------------
    # Get EXACT features used during model training
    # --------------------------------------------------------

    feature_columns = get_model_features(
        model
    )

    # --------------------------------------------------------
    # Check missing features
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in feature_columns
        if column not in data.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing model features: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # Select features in EXACT order
    # --------------------------------------------------------

    X = data[
        feature_columns
    ].copy()

    # --------------------------------------------------------
    # Handle missing values
    # --------------------------------------------------------

    X = X.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    X = X.fillna(
        0
    )

    # --------------------------------------------------------
    # Generate predictions
    # --------------------------------------------------------

    predictions = model.predict(
        X
    )

    return predictions 