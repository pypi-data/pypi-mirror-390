"""
Analyzer module for suclepy
Detects missing values, duplicates, and basic stats
"""

import pandas as pd

class Analyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.report = {}

    def check_missing(self):
        """Check missing values"""
        missing = self.df.isnull().sum().to_dict()
        self.report["missing_values"] = missing
        return missing

    def check_duplicates(self):
        """Check duplicate rows"""
        duplicates = self.df.duplicated().sum()
        self.report["duplicate_rows"] = duplicates
        return duplicates

    def summary_stats(self):
        """Return basic summary statistics"""
        stats = self.df.describe(include='all').to_dict()
        self.report["summary_stats"] = stats
        return stats

    def run(self):
        """Run full analysis"""
        self.check_missing()
        self.check_duplicates()
        self.summary_stats()
        return self.report
