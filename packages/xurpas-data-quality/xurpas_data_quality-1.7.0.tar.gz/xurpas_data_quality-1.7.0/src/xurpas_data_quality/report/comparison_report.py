from typing import List
from pydantic_settings import BaseSettings

from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import HTMLBase
from xurpas_data_quality.render.render_compare import render_compare

def get_comparison_report(data:List[TableDescription], table_names: List[str],name:str, config:BaseSettings)-> HTMLBase:
    """
    Generates a comparison report
    """

    return render_compare(data, table_names,name, config)