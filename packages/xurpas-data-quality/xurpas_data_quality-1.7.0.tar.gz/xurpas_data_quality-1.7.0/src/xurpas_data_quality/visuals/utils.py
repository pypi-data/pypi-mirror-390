import io
import base64
import matplotlib.pyplot as plt

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in creating plot: {e}")
            fig, ax = plt.subplots()
            ax.set(frame_on=False)
            ax.set_yticks([])
            ax.set_xticks([])
            return fig  # Replace with your actual empty plot logic

    return wrapper


def plot_to_base64_method(fig: plt.figure, minimal:bool=False):
    buf = io.BytesIO()
    
    if minimal:
        fig.savefig(buf, format="svg", bbox_inches='tight', dpi=80)
    else:    
        fig.savefig(buf, format="svg", bbox_inches='tight')
    
    plt.close(fig)

    data = base64.b64encode(buf.getvalue()).decode("utf8")
    buf.close()
    return "data:image/svg+xml;base64,{}".format(data)

def plot_to_base64(func):
    def wrapper(*args, **kwargs):
        fig = func(*args, **kwargs)
        minimal = kwargs.get('minimal', False)
        return plot_to_base64_method(fig, minimal)
    return wrapper