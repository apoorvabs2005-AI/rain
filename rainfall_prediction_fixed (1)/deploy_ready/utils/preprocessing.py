import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform initial cleaning: drop duplicates and handle basic sanity checks.
    """
    df = df.copy()
    initial_shape = df.shape
    
    # Drop duplicates
    df = df.drop_duplicates()
    if df.shape != initial_shape:
        logger.info(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows.")
        
    # Drop rows where target variable (ANNUAL) is null during training
    if "ANNUAL" in df.columns:
        df = df.dropna(subset=["ANNUAL"])
        
    return df

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fills missing values in monthly rainfall columns using subdivision-specific medians.
    If subdivision median is missing, uses the overall column median.
    """
    df = df.copy()
    
    # For monthly rainfall columns
    for col in MONTHS:
        if col in df.columns:
            # First, check if subdivision column exists to group by
            if "SUBDIVISION" in df.columns:
                df[col] = df.groupby("SUBDIVISION")[col].transform(lambda x: x.fillna(x.median()))
            # Fallback to overall median if still any NaN
            df[col] = df[col].fillna(df[col].median())
            
    # Handle ANNUAL if missing
    if "ANNUAL" in df.columns:
        df["ANNUAL"] = df["ANNUAL"].fillna(df[MONTHS].sum(axis=1))
        
    return df

def detect_outliers_iqr(df: pd.DataFrame, columns: list, factor: float = 3.0) -> pd.DataFrame:
    """
    Detects and handles outliers by capping them rather than deleting them,
    to preserve historical weather records but limit extreme ML model skew.
    """
    df = df.copy()
    for col in columns:
        if col in df.columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - factor * iqr
            upper_bound = q3 + factor * iqr
            
            # Cap outliers
            df[col] = np.clip(df[col], lower_bound, upper_bound)
    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates additional relevant features based on seasonal patterns.
    - Winter: Jan, Feb
    - Summer: Mar, Apr, May
    - Monsoon: Jun, Jul, Aug, Sep
    - Post-Monsoon: Oct, Nov, Dec
    - Statistics: Mean, Max, Min, Std of monthly rainfall
    """
    df = df.copy()
    
    # Seasons
    df["WINTER"] = df["JAN"] + df["FEB"]
    df["SUMMER"] = df["MAR"] + df["APR"] + df["MAY"]
    df["MONSOON"] = df["JUN"] + df["JUL"] + df["AUG"] + df["SEP"]
    df["POST_MONSOON"] = df["OCT"] + df["NOV"] + df["DEC"]
    
    # Stats
    df["MEAN_RAIN"] = df[MONTHS].mean(axis=1)
    df["MAX_RAIN"] = df[MONTHS].max(axis=1)
    df["MIN_RAIN"] = df[MONTHS].min(axis=1)
    df["STD_RAIN"] = df[MONTHS].std(axis=1)
    
    return df

def preprocess_data(
    df: pd.DataFrame, 
    is_training: bool = True, 
    label_encoder: LabelEncoder = None, 
    scaler: StandardScaler = None
):
    """
    Main preprocessing pipeline.
    Returns:
    - X: feature matrix (pandas DataFrame)
    - y: target array (only if is_training=True)
    - label_encoder: fitted LabelEncoder
    - scaler: fitted StandardScaler
    """
    df = clean_dataset(df)
    df = handle_missing_values(df)
    
    # Cap extreme outliers in monthly columns during training to stabilize models
    if is_training:
        df = detect_outliers_iqr(df, MONTHS, factor=3.0)
        
    df = engineer_features(df)
    
    # Encode SUBDIVISION
    if "SUBDIVISION" in df.columns:
        if is_training:
            label_encoder = LabelEncoder()
            df["SUBDIVISION_ENC"] = label_encoder.fit_transform(df["SUBDIVISION"].astype(str))
        else:
            if label_encoder is None:
                raise ValueError("Label encoder must be provided for inference.")
            
            # Map unseen subdivisions to a special placeholder if they appear
            sub_classes = set(label_encoder.classes_)
            df["SUBDIVISION"] = df["SUBDIVISION"].apply(lambda s: s if s in sub_classes else list(sub_classes)[0])
            df["SUBDIVISION_ENC"] = label_encoder.transform(df["SUBDIVISION"].astype(str))
    
    # Feature columns (ordered)
    feature_cols = ["SUBDIVISION_ENC", "YEAR"] + MONTHS + [
        "WINTER", "SUMMER", "MONSOON", "POST_MONSOON",
        "MEAN_RAIN", "MAX_RAIN", "MIN_RAIN", "STD_RAIN"
    ]
    
    X = df[feature_cols].copy()
    
    # Scaling
    numeric_cols = ["YEAR"] + MONTHS + [
        "WINTER", "SUMMER", "MONSOON", "POST_MONSOON",
        "MEAN_RAIN", "MAX_RAIN", "MIN_RAIN", "STD_RAIN"
    ]
    
    if is_training:
        scaler = StandardScaler()
        # Fit scaler on features
        X_scaled_vals = scaler.fit_transform(X[numeric_cols])
        X[numeric_cols] = X_scaled_vals
    else:
        if scaler is None:
            raise ValueError("Scaler must be provided for inference.")
        X_scaled_vals = scaler.transform(X[numeric_cols])
        X[numeric_cols] = X_scaled_vals
        
    if is_training and "ANNUAL" in df.columns:
        y = df["ANNUAL"].values
        return X, y, label_encoder, scaler
        
    return X, label_encoder, scaler
