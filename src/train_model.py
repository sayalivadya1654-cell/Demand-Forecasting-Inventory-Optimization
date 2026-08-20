"""
Model training module for demand forecasting.
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


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

MODEL_DIR = PROJECT_ROOT / "models"

MODEL_PATH = (
    MODEL_DIR
    / "demand_forecasting_model.pkl"
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


TARGET = "Sales"


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_model_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Model data not found: {DATA_PATH}"
        )

    return pd.read_csv(DATA_PATH)


# ---------------------------------------------------------
# PREPARE DATA
# ---------------------------------------------------------

def prepare_data(df):

    required_columns = FEATURES + [TARGET]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    df = df.sort_values("Date").reset_index(
        drop=True
    )

    X = df[FEATURES].copy()

    y = df[TARGET].copy()

    X = X.fillna(0)

    y = y.fillna(0)

    return X, y


# ---------------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------------

def train_model(X_train, y_train):

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    return model


# ---------------------------------------------------------
# EVALUATE MODEL
# ---------------------------------------------------------

def evaluate_model(
    model,
    X_test,
    y_test
):

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\nModel Performance")
    print("-----------------------------")
    print(f"MAE  : {mae:.2f}")
    print(f"RMSE : {rmse:.2f}")
    print(f"R²   : {r2:.4f}")

    return predictions


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print("Loading model data...")

    df = load_model_data()

    print(
        f"Dataset shape: {df.shape}"
    )

    X, y = prepare_data(df)

    # -----------------------------------------------------
    # CHRONOLOGICAL SPLIT
    # -----------------------------------------------------

    split_index = int(
        len(X) * 0.80
    )

    X_train = X.iloc[:split_index]

    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]

    y_test = y.iloc[split_index:]

    print(
        f"Training samples: {len(X_train)}"
    )

    print(
        f"Testing samples: {len(X_test)}"
    )

    # -----------------------------------------------------
    # TRAIN
    # -----------------------------------------------------

    print("\nTraining model...")

    model = train_model(
        X_train,
        y_train
    )

    # -----------------------------------------------------
    # EVALUATE
    # -----------------------------------------------------

    evaluate_model(
        model,
        X_test,
        y_test
    )

    # -----------------------------------------------------
    # SAVE MODEL
    # -----------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )

    print(
        "\nModel training completed successfully."
    )


if __name__ == "__main__":
    main() 