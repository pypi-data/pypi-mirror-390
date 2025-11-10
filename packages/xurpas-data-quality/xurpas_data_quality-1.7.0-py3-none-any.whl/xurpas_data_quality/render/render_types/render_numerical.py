import pandas as pd

from xurpas_data_quality.render.handler import Handler
from xurpas_data_quality.render.render_types.bottom.render_bottom_numerical import render_bottom_numerical
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLCollapse, HTMLToggle
from xurpas_data_quality.visuals import plot_to_base64, create_tiny_histogram, create_histogram, create_distribution_plot, create_heatmap, create_interaction_plot

def render_numerical(data: dict, name: str, config:dict)-> HTMLBase:
    name = name.replace(" ", "-").lower()
    overview_1 = {
        "Distinct": data['distinct'],
        "Distinct (%)": "{:0.2f}%".format(data['distinct_perc']),
        "Missing": data['missing'],
        "Missing (%)": "{:0.2f}%".format(data["missing_perc"]),
        "Infinite": data["infinite"],
        "Infinite (%)":"{:0.2f}%".format(data["infinite_perc"]) ,
        "Mean": "{:0.4f}".format(data["mean"])
    }

    overview_2 = {
        "Minimum": data['minimum'],
        "Maximum": data['maximum'],
        "Zeros": data['zeros'],
        "Zeros (%)": "{:0.2f}%".format(data['zeros_perc']),
        "Negative": data['negative'],
        "Negative (%)": "{:0.2f}%".format(data['negative_perc']),
        "Memory size": "{} bytes".format(data['memory']),
    }

    variable_body = {
        'table_1': HTMLTable(overview_1),
        'table_2': HTMLTable(overview_2),
        'plot': HTMLPlot(plot=create_tiny_histogram(data['histogram'], minimal=config.minimal))
    }

    return HTMLVariable(
        name = name,
        type = data['type'],
        body = variable_body,
        bottom=HTMLCollapse(
            HTMLToggle("More details", name),
            render_bottom_numerical(data, name)
        )
    )