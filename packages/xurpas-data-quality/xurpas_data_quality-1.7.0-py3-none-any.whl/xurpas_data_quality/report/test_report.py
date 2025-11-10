import pandas as pd

from xurpas_data_quality.render.renderer import HTMLBase
from xurpas_data_quality.render.render_test import render_test

def get_test_report(df: pd.DataFrame, name:str)-> HTMLBase:
    """
    Generates an empty report
    """

    return render_test(df)