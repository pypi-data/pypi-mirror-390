from xurpas_data_quality.data.typeset import Categorical
from xurpas_data_quality.render.handler import Handler
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse, HTMLDropdown
from xurpas_data_quality.visuals import plot_to_base64, create_tiny_histogram, create_histogram, create_distribution_plot, create_heatmap, create_interaction_plot

@Handler.register(Categorical)
def render_bottom_categorical(data, col_name,*args, **kwargs):
    variable_bottom = [
        HTMLContainer(
            type="default",
            name="Overview",
            id = 'overview',
            container_items= [
                HTMLContainer(type="box",
                              container_items=[
                                HTMLContainer(
                                    type = "column",
                                    container_items = HTMLTable(
                                        data = {
                                            "Max Length": data['max_length'],
                                            "Median Length": data['median_length'],
                                            "Mean Length": data['mean_length'],
                                            "Minimum Length": data['min_length']

                                        }
                                    )
                                ),
                                HTMLContainer(
                                    type ="column",
                                    container_items = HTMLTable(
                                        data = {f"{i+1}st Row" if i == 0 else f"{i+1}nd Row" if i == 1 else f"{i+1}rd Row" if i == 2 else f"{i+1}th Row": value for i, (key, value) in enumerate(data['samples'].items())}
                                    )

                                )]
                            )
            ]
        ),
        HTMLContainer(
            type="default",
            name="Categories",
            id="categories",
            container_items=[
                HTMLTable(
                    id=f"{col_name}-cat-samples",
                    name='Table',
                    data = data['cat_counts'].to_html(classes="table table-sm", border=0)
                )
            ]
        )
    ]
    return HTMLContainer(type="tabs",
                         col=col_name,
                         container_items=variable_bottom)