"""
Default configuration and rules for suclepy
"""

# Default configuration dictionary
config = {
    "missing_values": "fill_mean",  # options: drop, fill_mean, fill_median
    "drop_duplicates": True,
    "date_format": "%Y-%m-%d",
    "report_type": "console",  # options: console, csv
}

# Function to override default rules
def set_rules(**kwargs):
    """
    Update configuration rules.
    Example: set_rules(missing_values='drop', report_type='csv')
    """
    global config
    for key, value in kwargs.items():
        if key in config:
            config[key] = value
