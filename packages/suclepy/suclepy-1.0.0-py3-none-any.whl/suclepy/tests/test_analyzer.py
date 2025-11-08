import pandas as pd
from suclepy.core.analyzer import Analyzer

def test_analyzer_missing():
    df = pd.DataFrame({
        "A": [1, None, 3],
        "B": [4, 5, None]
    })
    analyzer = Analyzer(df)
    report = analyzer.run()
    
    # Missing values should be detected
    assert report["missing_values"]["A"] == 1
    assert report["missing_values"]["B"] == 1

def test_analyzer_duplicates():
    df = pd.DataFrame({
        "A": [1, 2, 2],
        "B": [5, 6, 6]
    })
    analyzer = Analyzer(df)
    report = analyzer.run()
    
    # Duplicates should be detected
    assert report["duplicate_rows"] == 1
