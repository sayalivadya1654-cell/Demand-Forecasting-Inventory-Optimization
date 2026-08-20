"""
Prediction module for demand forecasting.
"""

from pathlib import Path

import joblib
import pandas as pd


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "demand_forecasting_model.pkl"
)

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "model_data.csv"
)


# ---------------------------------------------------------
# FEATURES
# ---------------------------------------------------------

FEATURES = [
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

    "Inventory_to_Sales",
]


# ---------------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------------

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}. "
            "Run train_model.py first."
        )

    return joblib.load(
        MODEL_PATH
    )


# ---------------------------------------------------------
# PREDICT
# ---------------------------------------------------------

def predict_demand(df):

    model = load_model()

    missing_columns = [
        column
        for column in FEATURES
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing feature columns: {missing_columns}"
        )

    X = df[FEATURES].copy()

    X = X.fillna(0)

    predictions = model.predict(X)

    result = df[
        [
            "Date",
            "Product_ID",
            "Product",
            "Store",
            "City",
            "Inventory",
        ]
    ].copy()

    result["Predicted_Demand"] = predictions

    result["Predicted_Demand"] = (
        result["Predicted_Demand"]
        .clip(lower=0)
    )

    return result


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

    print("Generating predictions...")

    predictions = predict_demand(df)

    print("\nPrediction Sample")
    print("-----------------------------")

    print(
        predictions.head(20).to_string(
            index=False
        )
    )

    output_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "predictions.csv"
    )

    predictions.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nPredictions saved to: {output_path}"
    )


if __name__ == "__main__":
    main()