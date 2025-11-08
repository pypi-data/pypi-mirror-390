"""
Role inference module for suclepy
Infers column roles: ID, numeric, categorical, date
"""

import pandas as pd
from suclepy.core.utils import infer_column_role

class RoleInfer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.roles = {}

    def run(self):
        """Infer roles for all columns"""
        for col in self.df.columns:
            self.roles[col] = infer_column_role(self.df[col])
        return self.roles
