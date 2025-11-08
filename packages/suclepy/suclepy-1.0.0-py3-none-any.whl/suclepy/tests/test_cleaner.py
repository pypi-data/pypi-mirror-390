import pandas as pd
from suclepy.core.cleaner import Cleaner

def test_cleaner_fill_missing():
    # Sample data
    df = pd.DataFrame({
        "A": [1, 2, None, 4],
        "B": [None, 2, 3, 4]
    })
    
    cleaner = Cleaner(df)
    df_clean, report = cleaner.run()

    # Check missing values filled
    assert df_clean.isnull().sum().sum() == 0
    assert "missing_handled" in report

def test_cleaner_drop_duplicates():
    # Sample data with duplicates
    df = pd.DataFrame({
        "A": [1, 2, 2],
        "B": [5, 6, 6]
    })
    
    cleaner = Cleaner(df)
    df_clean, report = cleaner.run()

    # Check duplicates removed
    assert df_clean.duplicated().sum() == 0
    assert "duplicates_removed" in report
