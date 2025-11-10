import pandas as pd

from xurpas_data_quality.render.renderer import HTMLBase, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse
from xurpas_data_quality.visuals import plot_to_base64, create_horizontal_histogram
from xurpas_data_quality.render.render_types.bottom.render_bottom_categorical import render_bottom_categorical


def render_categorical(data: dict, name:str, config:dict)->HTMLBase:
    name = name.replace(" ", "-").lower()
    table = {
        "Distinct": data['distinct'],
        "Distinct (%)": "{:0.2f}%".format(data['distinct_perc']),
        "Missing": data['missing'],
        "Missing (%)": "{:0.2f}%".format(data["missing_perc"]),
        "Memory size": "{} bytes".format(data['memory'])
    }
    variable_body = {
        'table': HTMLTable(table),
        'plot': HTMLPlot(plot=create_horizontal_histogram(data['histogram_counts'], minimal=config.minimal),
                         type="categorical")
    }

    return HTMLVariable(
        name = name,
        type = data['type'],
        body = variable_body,
        bottom = HTMLCollapse(
            HTMLToggle("More details", name),
            render_bottom_categorical(data,name)
        )
    )