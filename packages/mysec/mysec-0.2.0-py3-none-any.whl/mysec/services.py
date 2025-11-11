from bearish.database.crud import BearishDb  # type: ignore
import plotly.graph_objects as go

from mysec.figures import plot_sec_data
from mysec.queries import total_decrease, total_increase


def sec(bearish_db: BearishDb) -> go.Figure:
    fig = go.Figure()
    decrease = total_decrease(bearish_db)
    increase = total_increase(bearish_db)
    fig = plot_sec_data(fig, [increase, decrease])
    return fig
