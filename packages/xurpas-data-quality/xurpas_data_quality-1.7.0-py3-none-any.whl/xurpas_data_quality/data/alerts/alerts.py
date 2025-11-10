from enum import Enum, auto, unique
from typing import Optional, List
from xurpas_data_quality.data.typeset import Numeric

@unique
class AlertType(Enum):
    CONSTANT = auto()

    ZEROS = auto()

    HIGH_CORRELATION = auto()

    HIGH_CARDINALITY = auto()

    IMBALANCE = auto()

    SKEWNESS = auto()

    MISSING_VALUES = auto()

    INFINITE_VALUES = auto()

    DATE = auto()

    UNIFORM = auto()

    UNIQUE = auto()

    CONSTANT_LENGTH = auto()

    REJECTED = auto()
    
    UNSUPPORTED = auto()

    DUPLICATES = auto()

    EMPTY = auto()

class Alert:
    def __init__(
            self,
            alert_type: AlertType,
            values: Optional[dict] = None,
            column_name: Optional[str] = None,
            fields: Optional[set] = None
    ):
        self.alert_type = alert_type
        self.column_name = column_name

    @property
    def alert_name(self) -> str:
        return self.alert_type.name
    
    
    def _get_description(self) -> str:
        return "{} on column: {}".format(self.alert_name, self.column_name)
    
    def __repr__(self):
        return self._get_description()
    
class ConstantAlert(Alert):
    def __init__(self, values: Optional[dict] = None, column_name: Optional[str] = None ):
        super().__init__(
            alert_type= AlertType.CONSTANT,
            values=values,
            column_name=column_name,
            fields={'distinct', 'distinct_perc'},
        )
    
    def _get_description(self) -> str:
        return f"[{self.column_name}] has a constant value"
    
class DuplicatesAlert(Alert):
    def __init__(self, values: Optional[dict] = None, column_name: Optional[str] = None ):
        super().__init__(
            alert_type= AlertType.DUPLICATES,
            values=values,
            column_name=column_name,
            fields={'duplicate_rows', 'duplicate_rows_perc'},
        )
    
    def _get_description(self) -> str:
        return f"[{self.column_name}] has a constant value"
    
class InfiniteAlert(Alert):
    def __init__(self, values: Optional[dict] = None, column_name: Optional[str] = None ):
        super().__init__(
            alert_type= AlertType.INFINITE_VALUES,
            values=values,
            column_name=column_name,
            fields={'infinite', 'infinite_perc'},
        )
    
    def _get_description(self) -> str:
        return f"[{self.column_name}] has a constant value"
    
class MissingAlert(Alert):
    def __init__(self, values: Optional[dict] = None, column_name: Optional[str] = None ):
        super().__init__(
            alert_type= AlertType.MISSING_VALUES,
            values=values,
            column_name=column_name,
            fields={'zeros', 'zeros_perc'},
        )
    
    def _get_description(self) -> str:
        return f"[{self.column_name}] contains missing values"
    
class UniqueAlert(Alert):
    def __init__(self, values: Optional[dict] = None, column_name: Optional[str] = None ):
        super().__init__(
            alert_type= AlertType.UNIQUE,
            values=values,
            column_name=column_name,
            fields={'zeros', 'zeros_perc'},
        )
    
    def _get_description(self) -> str:
        return f"[{self.column_name}] values are all unique"
    
class ZerosAlert(Alert):
    def __init__(self, values: Optional[dict] = None, column_name: Optional[str] = None ):
        super().__init__(
            alert_type= AlertType.ZEROS,
            values=values,
            column_name=column_name,
            fields={'zeros', 'zeros_perc'},
        )

    def _get_description(self) -> str:
        return f"[{self.column_name}] contains zeros"
    

def get_overview_alerts(dataset_stats: dict) -> List[Alert]:
    alerts = []
    
    if dataset_stats['duplicate_rows'] > 0:
        alerts.append(DuplicatesAlert)

    return alerts

def get_general_alerts(series_description: dict) -> List[Alert]:
    alerts = []

    if series_description['distinct'] > 0:
        alerts.append(ConstantAlert)

    if series_description['distinct_perc'] == 100:
        alerts.append(UniqueAlert)

    if series_description['missing'] > 0:
        alerts.append(MissingAlert)
    
    return alerts

def get_numerical_alerts(series_description: dict) -> List[Alert]:
    alerts = []

    if series_description['infinite'] > 0:
        alerts.append(InfiniteAlert)
    if series_description['zeros'] > 0:
        alerts.append(ZerosAlert)

    return alerts

def get_variable_alerts(col_name, series_description):
    alerts = []
    
    alerts.extend(get_general_alerts(series_description))

    if series_description['type'] == Numeric:
        alerts.extend(get_numerical_alerts(series_description))

    for i, alert in enumerate(alerts):
        alerts[i].column_name = col_name
        alerts[i].values = series_description

    return alerts

def get_alerts(dataset_stats, series_descriptions):

    alerts = []

    alerts.extend(get_overview_alerts(dataset_stats))

    for column_name, values in series_descriptions.items():
        alerts.extend(get_variable_alerts(column_name, values))

    return alerts