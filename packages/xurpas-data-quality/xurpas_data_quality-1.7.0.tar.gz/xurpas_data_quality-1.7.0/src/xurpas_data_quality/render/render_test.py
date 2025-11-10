import pandas as pd
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer
from xurpas_data_quality.render.render_sections import render_variables_section, render_dropdown_section


def render_test(data):
    variables_section = HTMLContainer(
        type = "box",
        name = "Variables",
        container_items = render_dropdown_section(items=render_variables_section(data), names=list(data.df))
    )

    body = HTMLContainer(type="sections",
                        container_items = [variables_section])
    
    return HTMLBase(
        body=body,
        name="report.py"
    )