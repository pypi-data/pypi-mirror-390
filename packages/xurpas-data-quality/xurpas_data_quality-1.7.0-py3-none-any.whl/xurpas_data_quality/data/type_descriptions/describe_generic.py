import pandas as pd

from typing import Tuple

def describe_generic(series: pd.Series, summary: dict)-> Tuple[pd.Series, dict]:
    """
    Describes a series with information for any data type.

    Args:
        series: series to describe
        summary: dict containing the descriptions of the series so far

    Return:
        The series and the updated summary dict

    """
    value_counts = series.value_counts()

    series_len = len(series)
    distinct = series.nunique()
    missing = series.isnull().sum().sum()
    memory = series.memory_usage()

    def _get_percentage(divisor: int, dividend=series_len):
        if dividend != 0:
            return (divisor / dividend) * 100
        else:
            return 0

    series_stats ={
        "distinct": distinct,
        "distinct_perc": _get_percentage(distinct),
        "missing": missing,
        "missing_perc": _get_percentage(missing),
        "memory": memory,
        "value_counts": value_counts
    }

    summary.update(series_stats)

    return summary
