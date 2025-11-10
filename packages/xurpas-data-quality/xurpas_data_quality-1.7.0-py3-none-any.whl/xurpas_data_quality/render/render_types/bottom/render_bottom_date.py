from visions import Date

from xurpas_data_quality.render.handler import Handler
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse, HTMLDropdown
from xurpas_data_quality.visuals import plot_to_base64, create_tiny_histogram, create_histogram, create_distribution_plot, create_heatmap, create_interaction_plot

@Handler.register(Date)
def render_bottom_categorical(data, *args, **kwargs):
    return HTMLContainer(type="default")