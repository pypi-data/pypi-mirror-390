import warnings
from typing import Callable, Sequence, Set

from visions import create_type, VisionsBaseType
from visions import DateTime, Date, Generic
from visions.relations import IdentityRelation, InferenceRelation,TypeRelation
from visions.typesets import StandardSet, VisionsTypeset

import pandas as pd
from pandas.api import types as pdt

warnings.filterwarnings("ignore", category=UserWarning, module='visions.typesets.typeset')

class Numeric(VisionsBaseType):

    @staticmethod
    def get_relations() -> Sequence[TypeRelation]:
        return [IdentityRelation(Generic)]
    
    @classmethod
    def contains_op(cls, series: pd.Series, state:dict)->bool:
        return pdt.is_numeric_dtype(series)
    
class Text(VisionsBaseType):
    @staticmethod
    def get_relations() -> Sequence[TypeRelation]:
        return [IdentityRelation(Generic)]
    
    @classmethod
    def contains_op(cls, series: pd.Series, state:dict) ->bool:
        series = series.dropna()
        return pdt.is_object_dtype(series)

def numeric_is_category(series: pd.Series, state: dict) -> bool:
    n_unique = series.nunique()
    threshold = 5
    return 1 <= n_unique <= threshold

def string_is_category(series: pd.Series, state: dict) -> bool:
    n_unique = series.nunique()
    unique_threshold = 0.5
    threshold = 50
    return (
        1 <= n_unique <= threshold and (n_unique / series.size) < unique_threshold
    )

def to_category(series: pd.Series, state: dict) -> pd.Series:
    return series.astype("category")

class Categorical(VisionsBaseType):

    @staticmethod
    def get_relations() -> Sequence[TypeRelation]:
        return [
            IdentityRelation(Generic),
            InferenceRelation(
                Numeric,
                relationship=lambda x, y: numeric_is_category(x,y),
                transformer=to_category,
            ),
            InferenceRelation(
                Text,
                relationship=lambda x, y: string_is_category(x,y),
                transformer=to_category,
            ),
        ]

    @staticmethod
    def contains_op(series: pd.Series, state: dict) -> bool:
        series = series.dropna()
        is_valid_dtype = pdt.is_categorical_dtype(series)
        if is_valid_dtype:
            return True
        return False

class XTypeSet(VisionsTypeset):
    def __init__(self):
        types = {
            Generic,
            Numeric,
            Categorical,
            Text,
            DateTime,
            }
        super().__init__(types)




