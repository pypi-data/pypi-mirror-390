from typing import List

import pandas as pd

def get_compare(df: pd.DataFrame, shared_values:list):
    # for every df, get, number of unique values, number of values per table, what values exist in other tables
    def handle_error(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error occurred: {e}")
            return "#N/A"
        
    if df.empty:
        unshared_df = pd.DataFrame()
        value_counts = "#N/A"
        unique_counts = "#N/A"
        unique_counts_perc = "#N/A"
        unshared_values = "#N/A"
    
    else:

        try:
            volume_columns = df.columns[df.columns.str.contains('volume', case=False)]
        except:
            volume_columns = "#N/A"
        
        try:
            value_counts = len(df[volume_columns].index)
        except:
            value_counts = "#N/A"

        try:
            unique_counts = df[volume_columns].nunique(dropna=True).iloc[0]
        except:
            unique_counts = "#N/A"
        
        try:
            unique_counts_perc = (unique_counts/value_counts)*100
        except:
            unique_counts_perc = "#N/A"
        
        try:
            unshared_values_series = unshared_df[volume_columns].dropna()
        except:
            unshared_values_series = "#N/A"

        try:
            unshared_values = unshared_values_series.squeeze().to_list()  if isinstance(unshared_values_series.squeeze(), pd.Series) else unshared_values_series.squeeze()
        except:
            unshared_values = "#N/A"
        
        try:
            unshared_values_rows = unshared_df.dropna(subset=['volume']).index
        except:
            unshared_values_rows = "#N/A"

        try:
            unshared_df = df.loc[unshared_values_rows]
        except:
            unshared_df = pd.DataFrame()

    
    return {
        'df': df,
        'unshared_df':unshared_df,
        'value_count':value_counts,
        'distinct_count':unique_counts,
        'distinct_perc': unique_counts_perc,
        'unshared_values': unshared_values
    }