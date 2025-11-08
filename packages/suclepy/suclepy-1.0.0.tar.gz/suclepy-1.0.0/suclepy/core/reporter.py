# suclepy/core/reporter.py

import pandas as pd

class CleaningReport:
    """
    CleaningReport stores the result of a cleaning operation
    and generates a summary in the documented format.
    """

    def __init__(self, cleaned_df, report_dict=None):
        """
        cleaned_df: pandas DataFrame after cleaning
        report_dict: Optional dictionary with stats about cleaning
        """
        self.cleaned_df = cleaned_df
        self.report = report_dict or {}
        self._generate_summary()

    def _generate_summary(self):
        # Default keys in case report_dict is empty
        self.summary_dict = {
            "Total Rows (before)": self.report.get("total_rows", len(self.cleaned_df)),
            "Rows After Cleaning": self.report.get("rows_after", len(self.cleaned_df)),
            "Duplicates Removed": self.report.get("duplicates_removed", 0),
            "Missing Values Filled": self.report.get("missing_filled", 0),
            "Invalid Emails Found": self.report.get("invalid_emails", 0),
            "Standardized Columns": self.report.get("standardized_cols", len(self.cleaned_df.columns)),
            "Status": self.report.get("status", "SUCCESS ✅")
        }

    def summary(self):
        # Nicely formatted summary string
        lines = ["SUCLEPY CLEANING REPORT", "-"*30]
        for key, value in self.summary_dict.items():
            lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def to_csv(self, filepath="cleaned_data.csv"):
        """Export cleaned DataFrame to CSV"""
        self.cleaned_df.to_csv(filepath, index=False)
        print(f"Cleaned data saved to {filepath}")

    def head(self, n=5):
        """Return top n rows of cleaned DataFrame"""
        return self.cleaned_df.head(n)
