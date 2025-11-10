import pandas as pd

from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer
from xurpas_data_quality.render.render_empty import render_empty

def get_empty_report(df: pd.DataFrame, config:dict)-> HTMLBase:
    """
    Generates an empty report
    """

    body = HTMLContainer(type="sections",
                         container_items = render_empty(df, config.report_name))


    return HTMLBase(body=body, name=config.report_name)