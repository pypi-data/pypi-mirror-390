import pandas as pd
import numpy as np

from typing import  Dict, Tuple

def get_samples(series: pd.Series):
    first_five = series.head(5)

    series_samples = {f"row_{value}": value for value in first_five }

    return series_samples

def get_cat_counts(series:pd.Series):
    counts = series.value_counts()
    percent = series.value_counts(normalize=True)*100
    percent = percent.map("{:.2f}%".format)

    return pd.DataFrame({'Counts': counts, 'Percentages': percent})

def describe_categorical(series: pd.Series, summary: Dict) ->  Tuple[pd.Series, Dict]:
    """
    Describes a categorical series.

    Args
        series: a pandas Series with a Numeric dtype to be described
        summary: dict containing the series descriptions so far

    Returns
        The series and the updated summary

    """
    # make sure that the series has no numbers
    series = series.astype('string')

    max_length = series.str.len().max()
    min_length = series.str.len().min()
    median_length = series.str.len().median()
    mean_length = series.str.len().mean()
    unique = sum(summary['value_counts']==1)
    unique_perc = unique/len(summary['value_counts'])*100
    sample = get_samples(series)
    cat_counts = get_cat_counts(series)

    summary.update({
        "max_length": max_length,
        "min_length": min_length,
        "median_length": median_length,
        "mean_length": mean_length,
        "unique": unique,
        "unique_perc": unique_perc,
        "histogram_counts": series.value_counts().to_dict(),
        "samples": sample,
        "cat_counts": cat_counts
    })


    return summary