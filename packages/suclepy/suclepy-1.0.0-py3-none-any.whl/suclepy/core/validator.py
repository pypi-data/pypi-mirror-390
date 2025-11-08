"""
Validator module for suclepy
Performs basic validation on cleaned dataset
"""

import pandas as pd

class Validator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.report = {}

    def validate_types(self):
        """Validate column types"""
        types = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        self.report["column_types"] = types
        return types

    def validate_missing(self):
        """Check if any missing values remain"""
        missing = self.df.isnull().sum().sum()
        self.report["missing_remaining"] = missing
        return missing

    def validate_duplicates(self):
        """Check if any duplicates remain"""
        duplicates = self.df.duplicated().sum()
        self.report["duplicates_remaining"] = duplicates
        return duplicates

    def run(self):
        """Run full validation"""
        self.validate_types()
        self.validate_missing()
        self.validate_duplicates()
        return self.report
