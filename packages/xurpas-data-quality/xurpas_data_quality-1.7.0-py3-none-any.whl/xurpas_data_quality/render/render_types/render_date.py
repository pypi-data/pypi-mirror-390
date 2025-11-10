import pandas as pd

from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse, HTMLDropdown
from xurpas_data_quality.visuals import plot_to_base64, create_tiny_histogram, create_histogram, create_distribution_plot, create_heatmap, create_interaction_plot

def render_date(data: dict, name:str, config:dict)->HTMLBase:
    name = name.replace(" ", "-").lower()
    table_1 = {
        "Distinct": data['distinct'],
        "Distinct (%)": "{:0.2f}%".format(data['distinct_perc']),
        "Missing": data['missing'],
        "Missing (%)": "{:0.2f}%".format(data["missing_perc"]),
        "Memory size": "{} bytes".format(data['memory'])
    }

    table_2 = {
        "Minimum": data['min_date'],
        "Maximum": data['max_date'],
        "Time range": f"{data['time_range']} days"
    }

    variable_body = {
        'table_1': HTMLTable(table_1),
        'table_2': HTMLTable(table_2),
        #'plot': HTMLPlot(plot=create_tiny_histogram(data['histogram'], minimal=config.minimal))
    }

    return HTMLVariable(
        name = name,
        type = data['type'],
        body = variable_body
    )