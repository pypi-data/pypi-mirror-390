import pandas as pd
from suclepy.core.utils import fill_missing, drop_duplicates, validate_email

class Cleaner:
    def __init__(self, df):
        self.df = df.copy()
    
    def clean(self):
        total_rows = len(self.df)
        
        # Drop duplicates
        self.df = drop_duplicates(self.df)
        duplicates_removed = total_rows - len(self.df)
        
        # Fill missing values using correct argument name
        missing_before = self.df.isnull().sum().sum()
        self.df = fill_missing(self.df, strategy="mean")
        missing_filled = missing_before - self.df.isnull().sum().sum()
        
        # Simple email validation
        if 'Email' in self.df.columns:
            invalid_emails = ~self.df['Email'].astype(str).apply(validate_email)
            invalid_emails_count = invalid_emails.sum()
        else:
            invalid_emails_count = 0
        
        # Standardized columns count (dummy example)
        standardized_cols = len(self.df.columns)
        
        # Report dictionary
        report_dict = {
            "total_rows": total_rows,
            "rows_after": len(self.df),
            "duplicates_removed": duplicates_removed,
            "missing_filled": missing_filled,
            "invalid_emails": invalid_emails_count,
            "standardized_cols": standardized_cols,
            "status": "SUCCESS ✅"
        }
        
        return self.df, report_dict
