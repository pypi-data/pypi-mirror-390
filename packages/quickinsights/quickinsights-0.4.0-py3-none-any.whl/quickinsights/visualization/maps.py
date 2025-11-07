"""
Geographic Maps Module

Provides geographic visualization capabilities including
choropleth maps, scatter maps, and density maps.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings("ignore")


def create_choropleth_map(
    df: pd.DataFrame,
    location_col: str,
    color_col: str,
    title: str = "Choropleth Map"
) -> go.Figure:
    """Create a choropleth map."""
    fig = px.choropleth(
        df, locations=location_col, color=color_col, title=title
    )
    return fig


def create_scatter_mapbox(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    color_col: Optional[str] = None,
    title: str = "Scatter Map"
) -> go.Figure:
    """Create a scatter mapbox."""
    fig = px.scatter_mapbox(
        df, lat=lat_col, lon=lon_col, color=color_col, title=title
    )
    return fig


def create_density_mapbox(
    df: pd.DataFrame,
    lat_col: str,
    lon_col: str,
    title: str = "Density Map"
) -> go.Figure:
    """Create a density mapbox."""
    fig = px.density_mapbox(
        df, lat=lat_col, lon=lon_col, title=title
    )
    return fig
