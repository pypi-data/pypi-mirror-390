import pandas as pd

from typing import Tuple

def describe_date(series: pd.Series, summary: dict)-> Tuple[pd.Series, dict]:
    """
    Describes a series with information for date data type.

    Args:
        series: series to describe
        summary: dict containing the descriptions of the series so far

    Return:
        The series and the updated summary dict
        """
    series = series.dropna()
    min_date = pd.to_datetime(series.min())
    max_date = pd.to_datetime(series.max())
    med_date = pd.to_datetime(min_date + (max_date-min_date))
    time_range = (max_date - min_date).days
    histogram_counts = series.value_counts().to_dict()
    summary.update(
            {'min_date': min_date,
             'median_date': med_date,
            'max_date': max_date,
            'time_range': time_range,
            'histogram_counts':histogram_counts})
    
    return summary
