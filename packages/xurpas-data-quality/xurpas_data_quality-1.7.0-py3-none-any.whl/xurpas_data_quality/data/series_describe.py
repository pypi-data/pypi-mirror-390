import pandas as pd

from typing import Tuple

from xurpas_data_quality.data import Describer, XTypeSet


def describe_series(col_name: str, series: pd.Series, data_types:dict=None)->Tuple[str, dict]:
    describer = Describer()
    if data_types is not None and col_name in data_types:
        series_type = data_types[col_name]

    else:
        typeset = XTypeSet()
        series_type = typeset.infer_type(series)

    series_description = describer.summarize(dtype=series_type, series=series)
    series_description.update({'type': series_type})

    return col_name, series_description

def get_series_descriptions(df: pd.DataFrame, data_types: dict=None)-> dict:
    """
    Provides a statistical description of each series in a DataFrame

    Args
        df: the dataframe to be described

    Returns
        A dict containing the descriptions of each series, and another dict
        containing the datatypes of each series
    """
    descriptions = {}
    for name, series in df.items():

        col_name, series_description = describe_series(name, series, data_types)
        descriptions.update({col_name: series_description})

        
    return descriptions
