import pandas as pd
from suclepy.core.analyzer import Analyzer
from suclepy.core.cleaner import Cleaner
from suclepy.core.reporter import Reporter

def test_reporter_generate():
    # Sample data
    df = pd.DataFrame({
        "A": [1, 2, None],
        "B": [3, 4, 5]
    })

    # Analyze and clean
    analyzer = Analyzer(df)
    analysis_report = analyzer.run()

    cleaner = Cleaner(df)
    df_clean, clean_report = cleaner.run()

    # Generate report
    reporter = Reporter(df_clean)
    reporter.generate(analysis_report, clean_report)

    # Since Reporter prints, we just ensure no exception occurs
    assert True
