import pandas as pd
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable

def render_empty(df: pd.DataFrame, name:str):
    content = [
        HTMLContainer(
            type="box",
            name="Sample",
            container_items=[
                HTMLTable(
                    id = "sample",
                    data=df.to_html(classes="table table-sm", border=0)
                )
            ]
        )
    ]

    return content
