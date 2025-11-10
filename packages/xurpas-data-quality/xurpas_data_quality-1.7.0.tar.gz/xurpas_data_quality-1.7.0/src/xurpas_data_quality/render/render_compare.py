import pandas as pd

from typing import List
from pydantic_settings import BaseSettings

from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable
from xurpas_data_quality.config import Settings

def render_compare(data: List[TableDescription], table_names:List[str],name:str, config:BaseSettings):
    

    headers = [f"Table {i+1}" for i in range(len(data))] if table_names is None else table_names

    distinct_count_list = []
    distinct_perc_list = []
    value_count_list = []
    shared_values_list = []
    shared_values_count_list = []
    shared_values_perc_list = []
    variable_types_list = []
    num_variables_list = []
    missing_cells_list = []
    missing_cells_perc_list = []
    duplicate_rows_list = []
    duplicate_rows_perc_list = []
    unshared_values_list = []
    dataframe_comparison = []

    for datum in data:
        distinct_count_list.append(datum.comparison['distinct_count'])
        value_count_list.append(datum.comparison['value_count'])
        distinct_perc_list.append(datum.comparison['distinct_perc'])
        shared_values_list.append(datum.shared_values['shared_values'])
        shared_values_count_list.append(datum.shared_values['shared_values_count'])
        try:
            shared_values_perc_list.append((datum.shared_values['shared_values_count']/datum.comparison['value_count'])*100)
        except:
            shared_values_perc_list.append("#N/A")

        unshared_values_list.append((datum.comparison['unshared_values']))

        variable_types_list.append(datum.variable_types)
        num_variables_list.append(datum.dataset_statistics['num_variables'])
        missing_cells_list.append(datum.dataset_statistics['missing_cells'])
        
        try:
            missing_cells_perc_list.append("{:0.2f}%".format(datum.dataset_statistics['missing_cells_perc']))
        except:
            missing_cells_perc_list.append("#N/A")
        
        duplicate_rows_list.append(datum.dataset_statistics['duplicate_rows'])

        try:
            duplicate_rows_perc_list.append("{:0.2f}%".format(datum.dataset_statistics['duplicate_rows_perc']))
        except:
            duplicate_rows_perc_list.append("#N/A")
        

        dataframe_comparison.append(datum.comparison['unshared_df'])
    
    combined_data = {
        'Count of Values': value_count_list,
        'Distinct Values (Count)': distinct_count_list,
        'Distinct Values (Percentage)': [f"{x:.2f}%" if isinstance(x, (int, float)) else x for x in distinct_perc_list],
        'Values Existing in All Tables (Count)': shared_values_count_list,
        'Values Existing in All Tables (Percentage)': [f"{x:.2f}%" if isinstance(x, (int, float)) else x for x in shared_values_perc_list],
        'Values NOT Shared between the tables': unshared_values_list
    }  

    dataset_statistics = {
        'Number of Variables': num_variables_list,
        'Missing Cells': missing_cells_list,
        'Missing Cells (%)': missing_cells_perc_list,
        'Duplicate Rows': duplicate_rows_list,
        'Duplicate Rows (%)': duplicate_rows_perc_list 
    }

    variable_types_statistics = {}
    for key in set().union(*variable_types_list):
        variable_types_statistics[key] = [0] * len(variable_types_list)

    for i, d in enumerate(variable_types_list):
        for key, value in d.items():
            variable_types_statistics[key][i] = value

    dataframe_unshared_sample = []

    for i, dataframe in enumerate(dataframe_comparison):
        dataframe_unshared_sample.append(
            HTMLContainer(
                type="default",
                name = headers[i],
                id = f"unshared_{headers[i]}_container",
                container_items=[
                    HTMLTable(
                    id = f"unshared_{headers[i]}",
                    name = f"Rows in {headers[i]} that are not shared with the other tables",
                    data= dataframe.to_html(classes="table table-sm", border=0, index=True, justify='left')
                    )
                ]
            ) 
        )    

    unshared_samples_tabs = HTMLContainer(
        type="tabs",
        container_items= dataframe_unshared_sample
    )

    comparison_section = HTMLContainer(
        type="tabs",
        container_items=[
            HTMLContainer(
                type="default",
                name="Comparison",
                id="comparison-column-compare",
                container_items=[HTMLTable(
                    id = "comparison",
                    name = '"Volume Column" Comparison',
                    data = combined_data,
                    headers = headers,
                    config = config
                )]
            ),
            HTMLContainer(
                type="default",
                name="Samples",
                id="samples-column-compare",
                container_items=[
                    unshared_samples_tabs
                ]
            )
        ]
    )

    column_comparison = HTMLContainer(
            type="box",
            name = "Comparison",
            container_items=[
                comparison_section
            ]
        )
    
    overview_section = HTMLContainer(
        type="box",
        name="Overview",
        container_items = [
            HTMLContainer(
                type="tabs",
                container_items=[HTMLContainer(
                    type="default",
                    name="Data",
                    id="comparison-data",
                    container_items = [HTMLTable(
                        id = "comparison",
                        name = "Overview of Data",
                        data = dataset_statistics,
                        headers = headers,
                        config = config
                        )]
                    ),
                    HTMLContainer(
                        type="default",
                        name="Variables",
                        id = "comparison-variables",
                        container_items = [HTMLTable(
                            id = "comparison",
                            name = "Overview of Variables",
                            data = variable_types_statistics,
                            headers = headers,
                            config = config
                        )]
                    )
                ]
            ),
        ]
    )

    content = [
        column_comparison,
        overview_section
    ]
    body = HTMLContainer(type="sections",
                         container_items = content)

    if name is not None:
        return HTMLBase(
            body=body,
            name=name
        )
    
    else:
        return HTMLBase(
            body=body
        )