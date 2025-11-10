import pandas as pd

from xurpas_data_quality.data.typeset import XTypeSet

def check_dtypes(dtypes: dict) -> dict:
    dtypes_mapping = {value.__name__: value for value in XTypeSet.types}

    for key, value in dtypes.items():
        if value in dtypes_mapping:
            dtypes[key] = dtypes_mapping[value]

    return dtypes

def check_col_names(dtypes: dict, cols: pd.Index) -> dict:
    for key in dtypes.keys():
        if key not in cols:
            raise ValueError(f'{key} is not a column in the given dataset!')
        
    return dtypes