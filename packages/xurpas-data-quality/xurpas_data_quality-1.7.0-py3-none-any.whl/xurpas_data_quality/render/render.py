import logging
logger = logging.getLogger(__name__)
from typing import Any, List

from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import BaseRenderer, HTMLContainer, HTMLTable, HTMLPlot, HTMLText
from xurpas_data_quality.render.render_sections import (render_variables_section, 
                                                    render_missing_section,
                                                    render_correlation_section, 
                                                    render_interactions_section, 
                                                    render_dropdown_section)

def  create_overview_section(data: TableDescription, dataset_statistics: dict) -> HTMLContainer:
    

    overview = HTMLContainer(
            type="default",
            name="Overview",
            id="overview-tab",
            container_items=[
                HTMLContainer(
                    type="column",
                    container_items=HTMLTable(
                        data=dataset_statistics,
                        name="Dataset Statistics"
                    )),
                HTMLContainer(
                    type="column",
                    container_items=HTMLTable(
                        data=data.variable_types,
                        name="Variable Types"
                    )
                )
            ]
        )
    
    overview_contents = [overview]

    if data.description is not None:
        description = HTMLContainer(
            type="default",
            name="Description",
            id="description-tab",
            container_items=[
                HTMLText(
                    text = data.description
                )
            ]
        )

        overview_contents.append(description)

    '''if data.alerts is not None and "shipment_no_alerts" in data.alerts:
        alerts = HTMLContainer(
            type="default",
            name="Alerts",
            id="alerts-tab",
            flex=True,
            container_items=[
                HTMLTable(
                    id="alerts",
                    data=[f"There are {data.alerts['shipment_no_alerts']['alerts']} rows with no Shipment Numbers"]
                ),
                HTMLTable(
                    id="alert_sample",
                    data=data.alerts["shipment_no_alerts"]["df"].to_html(classes="table table-sm", border=0, justify='left')
                )
            ]
        )
        overview_contents.append(alerts)'''

    return HTMLContainer(
        type="box",
        name="Overview",
        id="overview_section",
        container_items=[
            HTMLContainer(
                type="tabs",
                container_items=overview_contents
            )
        ]
    )

def render_report(data: TableDescription, config: dict) -> List[BaseRenderer]:
    """
    Creates the content of a normal report
    """
    content = []

    dataset_statistics = {
        'Length of Dataset': data.dataset_statistics['dataset_length'],
        'Number of Variables': data.dataset_statistics['num_variables'],
        'Missing Cells': data.dataset_statistics['missing_cells'],
        'Missing Cells (%)': "{:0.2f}%".format(data.dataset_statistics['missing_cells_perc']),
        'Duplicate Rows': data.dataset_statistics['duplicate_rows'],
        'Duplicate Rows (%)': "{:0.2f}%".format(data.dataset_statistics['duplicate_rows_perc'])
    }

    overview_section = create_overview_section(data, dataset_statistics)
    content.extend([overview_section])

    samples_section = HTMLContainer(
        type="box",
        name="Sample",
        container_items=[
            HTMLTable(
                id="sample",
                data=data.df.head(10).to_html(classes="table table-sm", border=0, index=False, justify='left')
            )
        ]
    )
    content.extend([samples_section])

    variables_section = HTMLContainer(
        type="box",
        name="Variables",
        container_items=render_dropdown_section(items=render_variables_section(data, config=config), names=list(data.df), config=config)
    )
    content.extend([variables_section])

    if config.visualizations.missing:
        missing_section = render_missing_section(data, config)
        content.extend([missing_section])

    if config.visualizations.correlation:
        correlation_section = render_correlation_section(data.correlation, config)
        content.extend([correlation_section])

    if not config.minimal:
        if config.visualizations.interactions:
            interactions_section = HTMLContainer(
                type="box",
                name="Interactions",
                container_items=[
                    HTMLContainer(
                        type="tabs",
                        container_items=render_interactions_section(data.df, config)
                    )
                ]
            )
            content.extend([interactions_section])
    
    return content