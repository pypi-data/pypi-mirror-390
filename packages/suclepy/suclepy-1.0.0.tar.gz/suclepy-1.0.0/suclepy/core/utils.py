# suclepy/core/utils.py

"""
Utility functions for SUCLEPY
---------------------------------
These functions are helper methods for data cleaning and preprocessing.
"""

import pandas as pd
import numpy as np
from email.utils import parseaddr
from dateutil.parser import parse

# ---------------------------
# Missing values handling
# ---------------------------
def fill_missing(df: pd.DataFrame, strategy="mean") -> pd.DataFrame:
    """
    Fill missing values in a DataFrame based on strategy.
    """
    df_copy = df.copy()
    
    for col in df_copy.columns:
        if df_copy[col].isna().sum() == 0:
            continue
        
        if strategy == "mean" and pd.api.types.is_numeric_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].fillna(df_copy[col].mean())
        elif strategy == "median" and pd.api.types.is_numeric_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].fillna(df_copy[col].median())
        elif strategy == "mode":
            df_copy[col] = df_copy[col].fillna(df_copy[col].mode()[0])
        elif strategy == "drop":
            df_copy = df_copy.dropna(subset=[col])
    
    return df_copy

# ---------------------------
# Duplicates handling
# ---------------------------
def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from a DataFrame.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame
    
    Returns:
        pd.DataFrame: DataFrame without duplicates
    """
    return df.drop_duplicates()



# palceholder
# suclepy/core/utils.py

def infer_column_role(df):
    """
    Dummy placeholder for column role inference.
    Returns a dictionary with column names as keys and roles as values.
    """
    roles = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            roles[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            roles[col] = "date"
        elif df[col].dtype == object:
            # Simple heuristic
            if "@" in df[col].dropna().astype(str).iloc[0]:
                roles[col] = "email"
            else:
                roles[col] = "text"
        else:
            roles[col] = "unknown"
    return roles


# ---------------------------
# Email validation
# ---------------------------
def validate_email(email: str) -> bool:
    """
    Simple email validation using parseaddr.
    
    Parameters:
        email (str): Email string
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(email, str) or "@" not in email:
        return False
    name, addr = parseaddr(email)
    return "@" in addr and "." in addr.split("@")[-1]

# ---------------------------
# Date parsing
# ---------------------------
def parse_date(date_str: str):
    """
    Parse a date string to standardized YYYY-MM-DD format.
    
    Parameters:
        date_str (str): Input date string
    
    Returns:
        str: Standardized date string or None if invalid
    """
    try:
        return parse(date_str).strftime("%Y-%m-%d")
    except Exception:
        return None

# ---------------------------
# Text normalization
# ---------------------------
def normalize_text(text: str) -> str:
    """
    Capitalize first letter of each word and strip spaces.
    
    Parameters:
        text (str): Input text string
    
    Returns:
        str: Normalized text
    """
    if not isinstance(text, str):
        return text
    return " ".join(word.capitalize() for word in text.strip().split())

