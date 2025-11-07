"""
Basic Creative Charts Module

Provides fundamental creative visualization charts including
radar charts, 3D scatter plots, heatmaps, and bubble charts.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings("ignore")


def create_radar_chart(
    df: pd.DataFrame,
    numeric_cols: List[str], 
    title: str = "Radar Chart Analysis"
) -> go.Figure:
    """
    Create a radar chart for multiple numeric columns.
    
    Args:
        df: Input dataframe
        numeric_cols: List of numeric columns to visualize
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    # Normalize data
    df_numeric = df[numeric_cols].copy()
    df_normalized = (df_numeric - df_numeric.min()) / (
        df_numeric.max() - df_numeric.min()
    )
    
    # Calculate mean values
    mean_values = df_normalized.mean()
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatterpolar(
            r=mean_values.values,
            theta=numeric_cols,
            fill="toself",
            name="Mean Values",
            line_color="#FF6B6B",
        )
    )
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title=title,
        font=dict(size=14),
    )
    
    return fig


def create_3d_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    z_col: str,
    color_col: Optional[str] = None,
    size_col: Optional[str] = None,
    title: str = "3D Scatter Plot"
) -> go.Figure:
    """
    Create a 3D scatter plot.
    
    Args:
        df: Input dataframe
        x_col: X-axis column
        y_col: Y-axis column
        z_col: Z-axis column
        color_col: Color coding column
        size_col: Size coding column
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    if color_col and size_col:
        fig = px.scatter_3d(
            df, x=x_col, y=y_col, z=z_col, 
            color=color_col, size=size_col,
            title=title
        )
    elif color_col:
        fig = px.scatter_3d(
            df, x=x_col, y=y_col, z=z_col,
            color=color_col, title=title
        )
    else:
        fig = px.scatter_3d(
            df, x=x_col, y=y_col, z=z_col,
            title=title
        )
    
    fig.update_layout(
        scene=dict(
            xaxis_title=x_col,
            yaxis_title=y_col,
            zaxis_title=z_col
        )
    )
    
    return fig


def create_heatmap(
    df: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None,
    title: str = "Correlation Heatmap"
) -> go.Figure:
    """
    Create a correlation heatmap.
    
    Args:
        df: Input dataframe
        numeric_cols: List of numeric columns (if None, auto-detect)
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    correlation_matrix = df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Features",
        yaxis_title="Features"
    )
    
    return fig


def create_bubble_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: str,
    color_col: Optional[str] = None,
    title: str = "Bubble Chart"
) -> go.Figure:
    """
    Create a bubble chart.
    
    Args:
        df: Input dataframe
        x_col: X-axis column
        y_col: Y-axis column
        size_col: Bubble size column
        color_col: Color coding column
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    if color_col:
        fig = px.scatter(
            df, x=x_col, y=y_col, size=size_col, color=color_col,
            title=title, hover_data=[x_col, y_col, size_col, color_col]
        )
    else:
        fig = px.scatter(
            df, x=x_col, y=y_col, size=size_col,
            title=title, hover_data=[x_col, y_col, size_col]
        )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig
