"""
Advanced Creative Charts Module

Provides advanced visualization charts including sunburst charts,
parallel coordinates, animated scatter plots, and 3D surfaces.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings("ignore")


def create_sunburst_chart(
    df: pd.DataFrame,
    path: List[str],
    values: Optional[str] = None,
    title: str = "Sunburst Chart"
) -> go.Figure:
    """Create a sunburst chart."""
    fig = px.sunburst(
        df, path=path, values=values, title=title
    )
    return fig


def create_parallel_coordinates(
    df: pd.DataFrame,
    numeric_cols: List[str],
    color_col: Optional[str] = None,
    title: str = "Parallel Coordinates"
) -> go.Figure:
    """Create parallel coordinates plot."""
    fig = px.parallel_coordinates(
        df, dimensions=numeric_cols, color=color_col, title=title
    )
    return fig


def create_animated_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    animation_col: str,
    title: str = "Animated Scatter"
) -> go.Figure:
    """Create animated scatter plot."""
    fig = px.scatter(
        df, x=x_col, y=y_col, animation_frame=animation_col, title=title
    )
    return fig


def create_3d_surface(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    z_col: str,
    title: str = "3D Surface"
) -> go.Figure:
    """Create 3D surface plot."""
    fig = go.Figure(data=[go.Surface(
        x=df[x_col].unique(),
        y=df[y_col].unique(),
        z=df.pivot_table(values=z_col, index=y_col, columns=x_col).values
    )])
    
    fig.update_layout(title=title)
    return fig
