import pandas as pd

from dataclasses import dataclass
from visions import VisionsTypeset, Generic, Date, DateTime
from typing import Dict, List, Callable, Optional

from xurpas_data_quality.data.type_descriptions import describe_numeric, describe_categorical, describe_generic, describe_date, describe_string
from xurpas_data_quality.data.typeset import Numeric, Categorical, Text


class Describer():
    """Describer of series. Contains mapping per type"""

    def __init__(self, 
                type_mapping: Dict[str, List[Callable]] = {
                     Generic : [
                         describe_generic,
                     ],
                     Numeric : [
                         describe_generic,
                         describe_numeric
                     ],
                     Categorical : [
                         describe_generic,
                         describe_categorical
                     ],
                     Date: [
                        describe_generic,
                        describe_date
                     ],
                     DateTime: [
                        describe_generic,
                        describe_date
                     ],
                     Text: [
                         describe_generic,
                         describe_string
                     ]}):
        self.mapping = type_mapping
    
    def summarize(self, dtype, series, **kwargs)-> dict:
        # give the series and typeset
        # for every applicable type apply the function to the series
        # update the summary dict with the new
        summary = {}
        if dtype in self.mapping:
            for func in self.mapping[dtype]:
                summary.update(func(series,summary))
        else:
            for func in self.mapping[Generic]:
                summary.update(func(series,summary))

        return summary
