
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import json
import yaml

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_csv_data(filepath: str, required_columns: list):
    """
    Loads data from a CSV file, validates its structure, and performs cleaning.

    Parameters
    ----------
    filepath : str
        Path to the CSV file.
    required_columns : list
        A list of column names that must be present in the CSV file.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with cleaned and validated data.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        logging.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        logging.error(f"Failed to read CSV file: {e}")
        raise

    if df.empty:
        logging.error("CSV file is empty.")
        raise ValueError("CSV file is empty.")

    # Ensure 'Time' column is present and convert to datetime
    if 'Time' not in df.columns:
        raise ValueError("Missing 'Time' column in CSV file.")
    df['Time'] = pd.to_datetime(df['Time'])
    df = df.set_index('Time')

    # Resample only the required columns (excluding 'Time' if present)
    data_columns = [col for col in required_columns if col != 'Time']
    df_resampled = df[data_columns].resample('1min').mean()
    
    initial_rows = len(df_resampled)
    
    # Interpolate missing values
    interpolated_before = df_resampled.isnull().sum().sum()
    df_resampled.interpolate(method='linear', inplace=True)
    interpolated_after = df_resampled.isnull().sum().sum()
    interpolated_count = interpolated_before - interpolated_after
    if interpolated_count > 0:
        logging.info(f"Interpolated {interpolated_count} missing values.")

    # Validate physical ranges dynamically based on required_columns
    # This assumes normal_ranges are defined in equipment_config for these columns
    # For now, we'll use a generic validation if specific ranges aren't available
    valid_rows_before = len(df_resampled)
    for col in required_columns:
        if col in df_resampled.columns:
            # Placeholder for dynamic range validation from config
            # For now, a very broad range to avoid errors, actual ranges should come from config
            min_val, max_val = -1000000, 1000000 # Very broad range
            
            original_len = len(df_resampled)
            df_resampled = df_resampled[(df_resampled[col] >= min_val) & (df_resampled[col] <= max_val)]
            rejected_count = original_len - len(df_resampled)
            if rejected_count > 0:
                logging.warning(f"Rejected {rejected_count} rows due to out-of-range values in '{col}'.")

    final_rows = len(df_resampled)
    logging.info(f"Loaded {final_rows} rows of data. Rejected {initial_rows - final_rows} rows.")
    
    return df_resampled

def load_metadata(filepath: str) -> dict:
    """
    Loads equipment metadata from a JSON or YAML file.

    Parameters
    ----------
    filepath : str
        Path to the metadata file.

    Returns
    -------
    dict
        A dictionary containing equipment metadata.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        logging.error(f"Metadata file not found: {filepath}")
        raise FileNotFoundError(f"Metadata file not found: {filepath}")

    try:
        with open(filepath, 'r') as f:
            if filepath.suffix in ['.json']:
                return json.load(f)
            elif filepath.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                raise ValueError("Unsupported metadata file format. Use JSON or YAML.")
    except Exception as e:
        logging.error(f"Failed to load metadata: {e}")
        raise

def validate_data_quality(df: pd.DataFrame) -> dict:
    """
    Validates the quality of the data in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to validate.

    Returns
    -------
    dict
        A dictionary with data quality metrics.
    """
    if df.empty:
        return {'missing_%': 100, 'outliers_%': 0, 'valid_rows': 0}

    # Missing data percentage
    missing_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100
    
    # Outlier detection using IQR
    outliers_percentage = 0
    for col in df.select_dtypes(include=np.number).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
        outliers_percentage += len(outliers) / len(df)
        
    outliers_percentage = (outliers_percentage / len(df.select_dtypes(include=np.number).columns)) * 100 if len(df.select_dtypes(include=np.number).columns) > 0 else 0

    quality_metrics = {
        'missing_%': round(missing_percentage, 2),
        'outliers_%': round(outliers_percentage, 2),
        'valid_rows': len(df)
    }

    if missing_percentage > 20:
        logging.warning(f"High percentage of missing data: {quality_metrics['missing_%']}%")

    logging.info(f"Data quality validation complete: {quality_metrics}")
    return quality_metrics
