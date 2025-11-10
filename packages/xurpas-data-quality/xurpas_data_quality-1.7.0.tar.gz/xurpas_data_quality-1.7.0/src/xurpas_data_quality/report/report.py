from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.render import render_report
from xurpas_data_quality.render.renderer import HTMLContainer, HTMLBase

from dataclasses import fields


def get_report(data: TableDescription,config:dict):
    """
    Generates a report
    """

    body = HTMLContainer(
        type="sections",
        container_items = render_report(data=data, config=config)
    )

    return HTMLBase(body=body, name=config.report_name)
