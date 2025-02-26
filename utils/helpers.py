import pandas as pd

# Required columns
REQUIRED_COLUMNS = [
    "Person_Id", "Age", "Sleep_Duration", "Quality_of_Sleep", "Physical_Activity_Level", 
    "Blood_Pressure", "Heart_Rate", "Daily_Steps"
]

def validate_csv_columns(df: pd.DataFrame):
    """Check if CSV contains all required columns."""
    return all(col in df.columns for col in REQUIRED_COLUMNS)

def clean_csv_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess CSV: Extract BP, convert datatypes, and clean missing values."""
    if not validate_csv_columns(df):
        raise ValueError(f"CSV must contain all required columns: {', '.join(REQUIRED_COLUMNS)}")

    # Extract Systolic & Diastolic BP
    df[['Systolic_BP', 'Diastolic_BP']] = df['Blood_Pressure'].str.split('/', expand=True).astype(int)

    # Drop unnecessary columns
    df.drop(columns=["Person_Id", "Blood_Pressure"], inplace=True)

    # Convert to numeric
    numeric_cols = ["Age", "Sleep_Duration", "Quality_of_Sleep", "Physical_Activity_Level",
                    "Systolic_BP", "Diastolic_BP", "Heart_Rate", "Daily_Steps"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    return df.dropna()  # Drop rows with missing values
