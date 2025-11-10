import pandas as pd
import numpy as np
import string

from typing import  Dict, Tuple

def _get_variable_frequencies(series: pd.Series, num_rows: int = 10) -> pd.DataFrame:
    series_value_counts = series.value_counts()

    # Create a DataFrame from the value counts
    df_value_counts = pd.DataFrame({'Count': series_value_counts.values}, index=series_value_counts.index)

    # Calculate the frequency and add it to the DataFrame
    df_value_counts['Frequency (%)'] = (df_value_counts['Count'] / series_value_counts.sum()) * 100

    # Add a row for "Other values"
    if len(series_value_counts) > num_rows:
        other_values_count = sum(series_value_counts.values[num_rows:])
        other_values_freq = (other_values_count / series_value_counts.sum()) * 100
        other_values_df = pd.DataFrame({'Count': [other_values_count], 'Frequency (%)': [other_values_freq]}, index=['Other values (' + str(len(series_value_counts) - num_rows) + ')'])
        df_variable_frequencies = pd.concat([df_value_counts.head(num_rows), other_values_df])
    else:
        df_variable_frequencies = df_value_counts.head(num_rows)

    # Set the name of the index
    df_variable_frequencies.index.name='Value'
    df_value_counts.index.name='Value'

    # Round the 'Frequency (%)' column to two decimal places and add a percentage sign
    df_variable_frequencies['Frequency (%)'] = df_variable_frequencies['Frequency (%)'].apply(lambda x: f'{x:.2f}%')

    return df_variable_frequencies

def _get_word_count(series: pd.Series) -> pd.Series:
    word_lists = series.str.lower().str.split()
    words = word_lists.explode().str.strip(string.punctuation+string.whitespace)
    word_counts = pd.Series(words.index, index=words)
    word_counts = word_counts[word_counts.index.notnull()]
    word_counts = word_counts.groupby(level=0, sort=False).sum()
    word_counts = word_counts.sort_values(ascending=False)

    return word_counts

def _get_samples(series: pd.Series):
    first_five = series.head(5)

    series_samples = {f"row_{value}": value for value in first_five }

    return series_samples

def describe_string(series: pd.Series, summary: Dict) ->  Tuple[pd.Series, Dict]:
    """
    Describes a string series.

    Args
        series: a pandas Series with a Numeric dtype to be described
        summary: dict containing the series descriptions so far

    Returns
        The series and the updated summary

    """
        # make sure that the series has no numbers

    def _get_percentage(divisor: int, dividend=summary['value_counts']):
        try:
            return (divisor / dividend) * 100
        except:
            return 0
    
    series = series.astype('string')
    
    max_length = series.str.len().max()
    min_length = series.str.len().min()
    median_length = series.str.len().median()
    mean_length = series.str.len().mean()
    unique = sum(summary['value_counts']==1)
    unique_perc = _get_percentage(unique)
    sample = _get_samples(series)
    word_counts = _get_word_count(series)

    summary.update({
        "max_length": max_length,
        "min_length": min_length,
        "median_length": median_length,
        "mean_length": mean_length,
        "unique": unique,
        "unique_perc": unique_perc,
        "histogram_counts": series.value_counts().to_dict(),
        "samples": sample,
        "word_counts": word_counts,
        "variable_frequencies": _get_variable_frequencies(series)
    })

    return summary
