"""
Command Line Interface for suclepy
"""

import argparse
from suclepy.main import auto_clean
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="SUCLEPY — Smart Universal Cleaner Library CLI")
    parser.add_argument("csv_file", help="Path to input CSV file")
    parser.add_argument("--report", help="Path to save report CSV files", default=None)
    parser.add_argument("--output", help="Path to save cleaned CSV file", default=None)
    args = parser.parse_args()

    df_clean, roles, validation_report = auto_clean(args.csv_file, args.report)

    if args.output:
        df_clean.to_csv(args.output, index=False)
        print(f"Cleaned data saved to {args.output}")

    print("\nColumn Roles:")
    for col, role in roles.items():
        print(f"{col}: {role}")

    print("\nValidation Summary:")
    for key, value in validation_report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
