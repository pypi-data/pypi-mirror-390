import pandas as pd

def get_correlations(df: pd.DataFrame)-> dict:
    return df.corr(numeric_only=True).round(3)