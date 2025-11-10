import pandas as pd

from visions import DateTime, Date

from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse, HTMLDropdown
from xurpas_data_quality.render.render_types import render_numerical, render_categorical, render_date, render_generic, render_string
from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.data.typeset import Numeric, Categorical, Text
from xurpas_data_quality.visuals import plot_to_base64,create_heatmap, create_interaction_plot, create_missing_bar_plot

def render_variable(data: dict, column: str, config:dict):
    if data['type'] == Numeric:
        return render_numerical(data, column, config)
    
    elif data['type'] == Categorical:
        return render_categorical(data, column, config)
    
    elif data['type'] == Date or data['type'] == DateTime:
        return render_date(data, column, config)
    
    elif data['type'] == Text:
        return render_string(data, column, config)
    
    else:
        return render_generic(data, column, config)
    
def render_variables_section(data: TableDescription, config:dict, **kwargs) -> list:
    vars = []
    for key, value in data.variables.items():
        variable = render_variable(value, key, config)
        vars.append(variable)
    return vars

def render_missing_section(data: pd.DataFrame, config:dict):
    if config.visualizations.missing:
        return HTMLContainer(
            type="box",
            name="Missing",
            container_items=[
                HTMLPlot(plot=create_missing_bar_plot(data.df, minimal=config.minimal),
                        type="large",
                        id="missingplot",
                        name="Missing Bar Plot")]
        )

def render_correlation_section(data: pd.DataFrame, config:dict):
    if config.visualizations.correlation:
        return HTMLContainer(
            type="box",
            name="Correlation",
            container_items=[
                HTMLContainer(
                    type="tabs",
                    container_items=[
                        HTMLPlot(plot=create_heatmap(data, minimal=config.minimal),
                                type="large",
                                id="corr",
                                name="Heatmap"),
                        HTMLTable(
                            id='sample',
                            name="Table",
                            data=data.to_html(classes="table table-sm", border=0, justify='left', index=False))
                    ]
                )
            ]
        )

def render_interactions_section(data:pd.DataFrame, config:dict)->HTMLBase:
    if config.visualizations.interactions:
        df = data.select_dtypes(exclude=['object'])
        outer_tabs = []
        for column in df.columns:
            inner_tabs = []
            for inner_col in df.columns:
                inner_tabs.append(
                    HTMLContainer(
                        type="default",
                        name= inner_col,
                        id = f"{column}-{inner_col}-interaction-inner",
                        container_items = [HTMLPlot(
                            plot= create_interaction_plot(df[inner_col],df[column], minimal=config.minimal),
                            type = "large",
                            name = f"{column}-{inner_col} Interaction Plot",
                            id = f"{column}-{inner_col}_interaction_plot"
                        )]
                    )
                )
            outer_tabs.append(
                HTMLContainer(
                    type="tabs",
                    name = column,
                    id = f"{column}-interaction-outer",
                    container_items = inner_tabs
                )
            )
        return outer_tabs

def render_dropdown_section(items: HTMLBase, names:list, config:dict, id="variables-dropdown" )-> list:
    return [
        HTMLDropdown(
        dropdown_items= names,
        dropdown_content= HTMLContainer(
            type="default",
            container_items= items),
        id=id
        )
    ]