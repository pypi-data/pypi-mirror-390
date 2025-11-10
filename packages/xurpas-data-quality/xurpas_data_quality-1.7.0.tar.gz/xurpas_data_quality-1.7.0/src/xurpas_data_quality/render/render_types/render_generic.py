from xurpas_data_quality.render.renderer import HTMLBase, HTMLVariable, HTMLTable

def render_generic(data, name, config:dict):
    name = name.replace(" ", "-").lower()
    table = {
        "Distinct": data['distinct'],
        "Distinct (%)": "{:0.2f}%".format(data['distinct_perc']),
        "Missing": data['missing'],
        "Missing (%)": "{:0.2f}%".format(data["missing_perc"]),
        "Memory size": "{} bytes".format(data['memory'])
    }

    variable_body = {
        'table': HTMLTable(table)
    }
    return HTMLVariable(
        name = name,
        type = data['type'],
        body = variable_body
    )