import warnings
from typing import Any

import jinja2
from jinja2 import Environment, PackageLoader, select_autoescape

# initialize jinja environment
env = Environment(loader=PackageLoader("xurpas_data_quality", "render/templates"))

def template(template_name:str)-> jinja2.Template:
    if not template_name.endswith('.html'):
        warnings.warn(f"Template {template_name} does not have the correct file extension '.html'! adding '.html' to template name", stacklevel=2)
        template_name += ".html"

    return env.get_template(template_name)
