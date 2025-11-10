import warnings
import logging
import pandas as pd

from typing import List
from visions import Date, DateTime

from xurpas_data_quality.config import Settings
from xurpas_data_quality.data import get_series_descriptions, get_correlations, XTypeSet
from xurpas_data_quality.data.compare import get_compare
from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.data.alerts import get_alerts

warnings.filterwarnings('ignore', category=UserWarning)
logger = logging.getLogger(__name__)

def get_variable_type_counts(variable_types: dict)-> dict:
    value_counts = {}
    for _, value in variable_types.items():

        if value == Date or value == DateTime:
            value = 'Date'
        if value in value_counts:
            value_counts[value] += 1
        else:
            value_counts[value] = 1

    return value_counts
    

def get_overview(df: pd.DataFrame, data_types:dict=None) -> dict:
    """
    Get the overview statistics of the DataFrame.

    Args:
        df: the DataFrame object
    
    Retunr:
        dictionary object containing the table statistics
    """
    num_variables = len(df.columns)
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()

    if data_types is not None:
        v_types = data_types

        for column in df.columns: # updates the v_types dict with the columns that are not user given data types
            if column not in v_types:
                v_types[column] = XTypeSet.infer_type(df[column])

    else:
        v_types = XTypeSet().infer_type(df)

    dataset_stats = {
        "dataset_statistics": {
            'num_variables': num_variables,
            'missing_cells': missing_cells,
            'missing_cells_perc' : (missing_cells/df.count().sum())*100,
            'duplicate_rows': duplicate_rows,
            'duplicate_rows_perc': (duplicate_rows/len(df))*100,
            'total_memory': df.memory_usage().sum(),
            'ave_memory': df.memory_usage().sum()/len(df),
            'dataset_length': len(df.index)
            },
        'variable_types': get_variable_type_counts(v_types)
    }

    return dataset_stats

def describe(df: pd.DataFrame, config:Settings,data_types: dict=None)-> TableDescription:
    """Gets Description of DataFrame which includes
    an overview, its correlations, and variable descriptions
    
    Args
        df: dataframe to be described

    Returns
        a class containing all the descriptions
    """
    logger.debug("in describe.py")
    def get_description(df, data_types, config=config):
        if config.visualizations.correlation:
            correlation = get_correlations(df)
        else:
            correlation = None
        if data_types is None:
            overview = get_overview(df)
            variables = get_series_descriptions(df)
        else:
            overview = get_overview(df, data_types)
            variables = get_series_descriptions(df, data_types)
        alerts = get_alerts(overview['dataset_statistics'], variables)
        data = TableDescription(df=df, variables=variables, correlation=correlation, alerts=alerts, **overview)

        return data

    if isinstance(df, list):
        descriptions = []
        shared_columns = [dataframe[col] for dataframe in df for col in dataframe.columns if 'volume' in col]
        shared_values = list(pd.Series(list(set(shared_columns[0]).intersection(*map(set, shared_columns[1:])))).values)
        shared_values_count = len(shared_values)
        for dataframe in df:
            data = get_description(dataframe,data_types)
            comparison_data = get_compare(dataframe, shared_values)
            data.shared_values = {'shared_values': shared_values,
                                  'shared_values_count': shared_values_count}
            data.comparison = comparison_data
            descriptions.append(data)

        return descriptions

    elif isinstance(df, pd.DataFrame):
        return get_description(df,data_types)
    

def describe_invalid(df: pd.DataFrame, errors: list, config: Settings) -> TableDescription:
    """
    Gets descriptions for the invalid dataframes/ dataframes that were ingested with error
    Args
        df: dataframe to be described

    Returns
        a class containing all the descriptions
    """
    try:
        dataset_length =   len(df.shape[0])
    except:
        dataset_length = 0
        
    dataset_stats = {
        "dataset_statistics": {
            "dataset_length": dataset_length,
            "error_counts": pd.Series(errors).value_counts().to_dict()
        }
    }


    
    return TableDescription(df=df, **dataset_stats)


def check_data(df: pd.DataFrame) -> list:
    try:
        df_empty = df[df['cbs_shipment_distribution.shipment_no'].isnull()]
        alerts = len(df_empty.index)

        if alerts <= 0:
            return

        else:
            return {"shipment_no_alerts": {"df": df_empty,
                                    "alerts": alerts}}

    except:
        return
    
