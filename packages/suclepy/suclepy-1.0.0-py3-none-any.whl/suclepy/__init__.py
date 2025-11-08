"""
SUCLEPY — Smart Universal Cleaner Library for Python
----------------------------------------------------
Clean Data. Clear Insights.

Developed by: Subodh Kumar Yadav
GitHub: https://github.com/subodhkryadav
LinkedIn: https://www.linkedin.com/in/subodh-kumar-yadav-522828293/
"""

__version__ = "1.0.0"
__author__ = "Subodh Kumar Yadav"

# Core functionality imports
from .main import auto_clean
from .config.settings import set_rules
from .core.cleaner import Cleaner
from .core.reporter import CleaningReport

# Alias for docs alignment: sp.config() → set_rules()
config = set_rules

__all__ = [
    "auto_clean",    # main entry point for cleaning
    "config",        # global config alias
    "set_rules",     # per-column/custom rules
    "Cleaner",       # optional direct cleaner access
    "CleaningReport" # optional report class access
]
