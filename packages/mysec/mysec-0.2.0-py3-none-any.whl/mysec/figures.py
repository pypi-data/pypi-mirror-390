from typing import List

import plotly.graph_objects as go

from mysec.models import SecData


def add_trace(figure: go.Figure, sec_data: SecData) -> go.Figure:
    figure.add_trace(
        go.Scatter(
            x=sec_data.data["occurrences"],
            y=sec_data.coefficient * sec_data.data["total_value"],
            mode="markers",
            text=sec_data.data.apply(
                lambda row: f"<b>{row['name']}</b> ({row['ticker']})<br>"
                f"<i>Companies:</i> {row['companies'].split(',')[:2]}",
                axis=1,
            ),
            marker={"color": sec_data.color},
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Occurrences: %{x}<br>"
                "Total Value: %{y:,}<extra></extra>"
            ),
        )
    )
    return figure


def plot_sec_data(figure: go.Figure, sec_data: List[SecData]) -> go.Figure:
    for sec_data_ in sec_data:
        figure = add_trace(figure, sec_data_)
    return figure
