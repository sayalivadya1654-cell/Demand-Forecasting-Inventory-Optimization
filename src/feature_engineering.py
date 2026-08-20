from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(r"E:\SmartStock-AI")

INPUT_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "cleaned_sales_data.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "Data"
    / "processed"
    / "model_data.csv"
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(df):

    print("Creating features...")

    df = df.copy()

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # SORT DATA
    # --------------------------------------------------------

    df = df.sort_values(
        by=[
            "Product_ID",
            "Store",
            "Date"
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # TIME FEATURES
    # --------------------------------------------------------

    df["Year"] = df["Date"].dt.year

    df["Month"] = df["Date"].dt.month

    df["Day"] = df["Date"].dt.day

    df["DayOfWeek"] = df["Date"].dt.dayofweek

    df["WeekOfYear"] = (
        df["Date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    df["Quarter"] = df["Date"].dt.quarter

    df["IsWeekend"] = (
        df["DayOfWeek"] >= 5
    ).astype(int)

    # --------------------------------------------------------
    # PRICE / DISCOUNT FEATURES
    # --------------------------------------------------------

    df["DiscountAmount"] = (
        df["Price"]
        * df["Discount"]
        / 100
    )

    df["PriceAfterDiscount"] = (
        df["Price"]
        - df["DiscountAmount"]
    )

    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    df["Revenue"] = (
        df["PriceAfterDiscount"]
        * df["Sales"]
    )

    # --------------------------------------------------------
    # GROUP
    # --------------------------------------------------------

    group = df.groupby(
        [
            "Product_ID",
            "Store"
        ]
    )

    # --------------------------------------------------------
    # LAG FEATURES
    # --------------------------------------------------------

    df["Sales_Lag_1"] = (
        group["Sales"]
        .shift(1)
    )

    df["Sales_Lag_7"] = (
        group["Sales"]
        .shift(7)
    )

    df["Sales_Lag_14"] = (
        group["Sales"]
        .shift(14)
    )

    df["Sales_Lag_30"] = (
        group["Sales"]
        .shift(30)
    )

    # --------------------------------------------------------
    # ROLLING AVERAGE FEATURES
    # --------------------------------------------------------

    df["Sales_Rolling_7"] = (
        df.groupby(
            [
                "Product_ID",
                "Store"
            ]
        )["Sales"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                7,
                min_periods=1
            )
            .mean()
        )
    )

    df["Sales_Rolling_14"] = (
        df.groupby(
            [
                "Product_ID",
                "Store"
            ]
        )["Sales"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                14,
                min_periods=1
            )
            .mean()
        )
    )

    df["Sales_Rolling_30"] = (
        df.groupby(
            [
                "Product_ID",
                "Store"
            ]
        )["Sales"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                30,
                min_periods=1
            )
            .mean()
        )
    )

    # --------------------------------------------------------
    # INVENTORY / SALES
    # --------------------------------------------------------

    df["Inventory_to_Sales"] = (
        df["Inventory"]
        /
        df["Sales"].replace(
            0,
            pd.NA
        )
    )

    # --------------------------------------------------------
    # HANDLE INFINITE VALUES
    # --------------------------------------------------------

    df = df.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    # --------------------------------------------------------
    # FILL MISSING VALUES
    # --------------------------------------------------------

    feature_columns = [
        "Sales_Lag_1",
        "Sales_Lag_7",
        "Sales_Lag_14",
        "Sales_Lag_30",
        "Sales_Rolling_7",
        "Sales_Rolling_14",
        "Sales_Rolling_30",
        "Inventory_to_Sales"
    ]

    for column in feature_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        df[column] = df[column].fillna(0)

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("DEMAND FORECASTING - FEATURE ENGINEERING")
    print("=" * 60)

    # --------------------------------------------------------
    # CHECK INPUT
    # --------------------------------------------------------

    if not INPUT_PATH.exists():

        raise FileNotFoundError(
            f"\nFile not found:\n{INPUT_PATH}"
        )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    print("\nLoading cleaned data...")

    df = pd.read_csv(
        INPUT_PATH
    )

    print(
        f"Input shape: {df.shape}"
    )

    # --------------------------------------------------------
    # CREATE FEATURES
    # --------------------------------------------------------

    model_df = create_features(df)

    print(
        f"Model dataset shape: "
        f"{model_df.shape}"
    )

    # --------------------------------------------------------
    # CHECK REQUIRED FEATURES
    # --------------------------------------------------------

    required_features = [
        "Year",
        "Month",
        "Day",
        "DayOfWeek",
        "WeekOfYear",
        "Quarter",
        "IsWeekend",
        "DiscountAmount",
        "PriceAfterDiscount",
        "Revenue",
        "Sales_Lag_1",
        "Sales_Lag_7",
        "Sales_Lag_14",
        "Sales_Lag_30",
        "Sales_Rolling_7",
        "Sales_Rolling_14",
        "Sales_Rolling_30",
        "Inventory_to_Sales"
    ]

    missing = [
        column
        for column in required_features
        if column not in model_df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing engineered features: {missing}"
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    model_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "\nModel data saved successfully:"
    )

    print(OUTPUT_PATH)

    print(
        f"\nFinal dataset shape: "
        f"{model_df.shape}"
    )

    print("\nFeature engineering completed successfully!")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()