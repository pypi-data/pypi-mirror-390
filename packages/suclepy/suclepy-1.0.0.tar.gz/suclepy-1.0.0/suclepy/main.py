# suclepy/main.py

import pandas as pd
from suclepy.core.cleaner import Cleaner
from suclepy.core.reporter import CleaningReport



def auto_clean(data):
    """
    Auto clean data from file path or pandas DataFrame.
    Returns a CleaningReport object.
    
    Parameters:
        data (str | pd.DataFrame): Path to CSV file or pandas DataFrame
    
    Returns:
        CleaningReport: Object containing cleaned DataFrame and summary
    """
    # Load data if a file path is given
    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("Input must be a file path or pandas DataFrame")

    # Initialize Cleaner
    cleaner = Cleaner(df)
    cleaned_df, report_dict = cleaner.clean()

    # Return CleaningReport object
    return CleaningReport(cleaned_df, report_dict)