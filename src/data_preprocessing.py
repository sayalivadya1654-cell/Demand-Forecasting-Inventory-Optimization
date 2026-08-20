"""
Data preprocessing module for Demand Forecasting
and Inventory Optimization.
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(r"E:\SmartStock-AI")


# ============================================================
# DATA PATHS
# ============================================================

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "Data"
    / "Raw"
    / "demand_forecasting_inventory_data.csv"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "Data"
    / "processed"
)

CLEANED_DATA_PATH = (
    PROCESSED_DIR
    / "cleaned_sales_data.csv"
)


# ============================================================
# EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS = [
    "Date",
    "Product_ID",
    "Product",
    "Category",
    "Store",
    "City",
    "Price",
    "Discount",
    "Promotion",
    "Inventory",
    "Sales",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data(file_path=RAW_DATA_PATH):
    """
    Load raw sales data from CSV.
    """

    file_path = Path(file_path)

    print(f"Reading dataset from:")
    print(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"\nDataset not found:\n{file_path}"
        )

    df = pd.read_csv(file_path)

    return df


# ============================================================
# VALIDATE COLUMNS
# ============================================================

def validate_columns(df):
    """
    Check whether all required columns exist.
    """

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in dataset: {missing_columns}"
        )

    print("All required columns are present.")

    return True


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):
    """
    Clean and prepare the raw sales dataset.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = df.columns.str.strip()

    # --------------------------------------------------------
    # Validate columns
    # --------------------------------------------------------

    validate_columns(df)

    # --------------------------------------------------------
    # Convert Date
    # --------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "Price",
        "Discount",
        "Promotion",
        "Inventory",
        "Sales",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Remove duplicate rows
    # --------------------------------------------------------

    before_duplicates = len(df)

    df = df.drop_duplicates()

    after_duplicates = len(df)

    print(
        f"Duplicate rows removed: "
        f"{before_duplicates - after_duplicates}"
    )

    # --------------------------------------------------------
    # Remove rows with missing important values
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
            "Date",
            "Product_ID",
            "Store",
        ]
    )

    # --------------------------------------------------------
    # Fill missing numeric values
    # --------------------------------------------------------

    for column in numeric_columns:

        if df[column].isna().any():

            median_value = df[column].median()

            df[column] = df[column].fillna(
                median_value
            )

    # --------------------------------------------------------
    # Fill missing categorical values
    # --------------------------------------------------------

    categorical_columns = [
        "Product",
        "Category",
        "City",
    ]

    for column in categorical_columns:

        df[column] = df[column].fillna(
            "Unknown"
        )

    # --------------------------------------------------------
    # Remove invalid values
    # --------------------------------------------------------

    df = df[df["Price"] >= 0]

    df = df[df["Inventory"] >= 0]

    df = df[df["Sales"] >= 0]

    # --------------------------------------------------------
    # Keep Discount between 0 and 100
    # --------------------------------------------------------

    df["Discount"] = df["Discount"].clip(
        lower=0,
        upper=100
    )

    # --------------------------------------------------------
    # Keep Promotion as 0 or 1
    # --------------------------------------------------------

    df["Promotion"] = df["Promotion"].clip(
        lower=0,
        upper=1
    )

    # --------------------------------------------------------
    # Sort data
    # --------------------------------------------------------

    df = df.sort_values(
        by=[
            "Product_ID",
            "Store",
            "Date"
        ]
    ).reset_index(drop=True)

    return df


# ============================================================
# SAVE CLEANED DATA
# ============================================================

def save_cleaned_data(
    df,
    output_path=CLEANED_DATA_PATH
):
    """
    Save cleaned dataset.
    """

    output_path = Path(output_path)

    # Create processed folder if it doesn't exist
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nCleaned dataset saved to:"
    )

    print(output_path)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("DEMAND FORECASTING - DATA PREPROCESSING")
    print("=" * 60)

    # --------------------------------------------------------
    # Load raw dataset
    # --------------------------------------------------------

    print("\n1. Loading raw dataset...")

    df = load_data()

    print(
        f"Raw dataset shape: {df.shape}"
    )

    # --------------------------------------------------------
    # Clean dataset
    # --------------------------------------------------------

    print("\n2. Cleaning dataset...")

    cleaned_df = clean_data(df)

    print(
        f"Cleaned dataset shape: "
        f"{cleaned_df.shape}"
    )

    # --------------------------------------------------------
    # Save dataset
    # --------------------------------------------------------

    print("\n3. Saving cleaned dataset...")

    save_cleaned_data(
        cleaned_df
    )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DATA PREPROCESSING COMPLETED SUCCESSFULLY")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()