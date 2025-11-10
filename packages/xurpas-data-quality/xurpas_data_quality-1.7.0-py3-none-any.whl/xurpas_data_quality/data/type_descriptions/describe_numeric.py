import pandas as pd
import numpy as np

from typing import  Dict, Tuple

from xurpas_data_quality.data.algorithms import compute_histogram

def get_variable_statistics(series: pd.Series) ->dict:
    def get_MAD(df):
        med = df.median()
        med_list = [abs(item-med) for item in df]

        return pd.Series(med_list).median()

    def get_monotonicity(df):
        if df.is_monotonic_increasing:
            return "Is increasing"
        elif df.is_monotonic_decreasing:
            return "Is decreasing"
        else:
            return "Not Monotonic"
     
    minimum = series.min()
    fifth_percentile = series.quantile(0.05)
    q1 = series.quantile(0.25)
    median = series.quantile(0.5)
    q3 = series.quantile(0.75)
    ninety_fifth_percentile = series.quantile(0.95)
    maximum = series.max()
    stat_range = maximum - minimum
    interquartile_range = q3-q1
    standard_dev = series.std()
    mean = series.mean()

    if mean == 0:
        cv = "N/A"
    else:
        cv = (standard_dev/mean)

    kurtosis= series.kurtosis()
    mad = get_MAD(series)
    skew = series.skew()
    total_sum = series.sum()
    variance = series.var()
    monotonicity = get_monotonicity(series)
    return {
        'quantile_stats':
            {
                'minimum': minimum,
                '5th_percentile': fifth_percentile,
                'Q1': q1,
                'median': median,
                'Q3': q3,
                '95th_percentile': ninety_fifth_percentile,
                'maximum': maximum,
                'range': stat_range,
                'IQR': interquartile_range,
            }, 
        'descriptive_stats':
            { 
            'std_dev': standard_dev,
            'mean': mean,
            'CV': cv,
            'kurtosis': kurtosis,
            'MAD': mad,
            'skew': skew,
            'sum': total_sum,
            'variance': variance,
            'monotonicity': monotonicity
            }
        }


def describe_numeric(series: pd.Series, summary: Dict) ->  Tuple[pd.Series, Dict]:
    """
    Describes a numeric series.

    Args
        series: a pandas Series with a Numeric dtype to be described
        summary: dict containing the series descriptions so far

    Returns
        The series and the updated summary

    """
    """ensure that series is numeric"""
    series = pd.to_numeric(series, errors='coerce')
    series = series.dropna()


    series_len = len(series)

    def _get_percentage(divisor: int, dividend=series_len):
        if dividend != 0:
            return (divisor / dividend) * 100
        else:
            return 0

    infinite = series.isin([np.inf,-np.inf]).sum().sum()
    negative = (pd.to_numeric(series, errors='coerce') < 0).sum()


    if 'value_counts' in summary:
        zeros = summary['value_counts'].get(0, 0)
    else:
        zeros = series.value_counts().get(0, 0)

    summary.update({
        "infinite": infinite,
        "infinite_perc": _get_percentage(infinite),
        "mean": series.mean(),
        "minimum": series.min(),
        "maximum": series.max(),
        "zeros": zeros,
        "zeros_perc": _get_percentage(zeros),
        "negative": negative,
        "negative_perc": _get_percentage(negative)
    })

    summary.update(compute_histogram(series.dropna()))
    summary.update(get_variable_statistics(series))

    return summary