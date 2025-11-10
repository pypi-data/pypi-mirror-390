import pandas as pd
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLPlot
from xurpas_data_quality.data.descriptions import TableDescription

def render_error(data:TableDescription, data_invalid:TableDescription, errors:list, is_empty:bool):
    
    dataset_length = 0 if is_empty else data.dataset_statistics['dataset_length']

    total_rows = dataset_length + data_invalid.dataset_statistics['dataset_length']
    errors_stats = {
        'Valid Data Ingested (# of Rows)': dataset_length,
        'Valid Data Ingested (% Percentage)': "{:0.2f}%".format(((dataset_length / total_rows) * 100) if total_rows != 0 else 0),
        'Invalid Data Ingested (# of Rows)': data_invalid.dataset_statistics['dataset_length'],
        'Invalid Data Ingested (% Percentage)': "{:0.2f}%".format(((data_invalid.dataset_statistics['dataset_length'] / total_rows) * 100) if total_rows != 0 else 0),
        'Total Rows for Dataset': total_rows
    }
    
    sample_errors_section = HTMLContainer(
        type="default",
        name="Invalid Rows",
        id ="sample-errors",
        flex = True,
        container_items=[
            HTMLTable(
                id = "sample",
                data=data_invalid.df.to_html(classes="table table-sm", border=0, index=True, justify='left')
            )
        ]
    )

    errors_list = HTMLContainer(
            type="default",
            name="Erroneous Values",
            id = "list-errors",
            flex = True,
            container_items=[
                HTMLTable(
                    headers = ["Error Value", "Count"],
                    data = data_invalid.dataset_statistics['error_counts'],
                    hoverable = True,
                )
            ]
        )
    
    errors_info = HTMLContainer(
        type="default",
        id = "info-errors",
        name="Error Overview",
        flex = True,
        container_items=[
            HTMLContainer(type="default",
                          container_items=[]),
            HTMLTable(
                name="Errors Overview",
                data = errors_stats
            )
        ]
    )

    errors_section = HTMLContainer(
        type="box",
        name="Errors during Ingestion",
        id = "errors_section",
        container_items=[
            HTMLContainer(
                type="tabs",
                container_items=[errors_info,errors_list, sample_errors_section]
            )
        ]
    )

 
    return errors_section
