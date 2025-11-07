"""
Specialized Creative Charts Module

Provides specialized visualization charts including waterfall charts,
funnel charts, Gantt charts, and Sankey diagrams.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings("ignore")


def create_waterfall_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Waterfall Chart"
) -> go.Figure:
    """Create a waterfall chart."""
    fig = go.Figure(go.Waterfall(
        x=df[x_col],
        y=df[y_col],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(title=title)
    return fig


def create_funnel_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Funnel Chart"
) -> go.Figure:
    """Create a funnel chart."""
    fig = go.Figure(go.Funnel(
        x=df[x_col],
        y=df[y_col]
    ))
    
    fig.update_layout(title=title)
    return fig


def create_gantt_chart(
    df: pd.DataFrame,
    task_col: str,
    start_col: str,
    finish_col: str,
    title: str = "Gantt Chart"
) -> go.Figure:
    """Create a Gantt chart."""
    fig = go.Figure(data=[
        go.Bar(
            x=df[start_col],
            y=df[task_col],
            width=df[finish_col] - df[start_col],
            orientation='h'
        )
    ])
    
    fig.update_layout(title=title)
    return fig


def create_sankey_diagram(
    df: pd.DataFrame,
    source_col: str,
    target_col: str,
    value_col: str,
    title: str = "Sankey Diagram"
) -> go.Figure:
    """Create a Sankey diagram."""
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=list(set(df[source_col].tolist() + df[target_col].tolist())),
            color="blue"
        ),
        link=dict(
            source=df[source_col],
            target=df[target_col],
            value=df[value_col]
        )
    )])
    
    fig.update_layout(title=title)
    return fig
