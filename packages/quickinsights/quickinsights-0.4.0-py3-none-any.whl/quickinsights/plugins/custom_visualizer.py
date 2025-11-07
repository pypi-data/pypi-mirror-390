"""
Custom Visualizer Plugin

Example plugin that demonstrates custom visualization capabilities.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Any, Dict, List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from plugin_system import (
    VisualizerPlugin, 
    PluginInfo, 
    PluginType, 
    PluginPriority
)


class CustomVisualizerPlugin(VisualizerPlugin):
    """Custom visualization plugin with advanced charting capabilities"""
    
    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        return PluginInfo(
            name="CustomVisualizer",
            version="1.0.0",
            description="Custom visualization plugin with advanced charting and styling options",
            author="QuickInsights Team",
            plugin_type=PluginType.VISUALIZER,
            priority=PluginPriority.NORMAL,
            dependencies=["matplotlib", "seaborn", "pandas"],
            entry_point="custom_visualizer"
        )
    
    def initialize(self, context: Dict[str, Any]) -> None:
        """Initialize the plugin"""
        self.context = context
        self.initialized = True
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
    
    def visualize(self, data: Any, **kwargs) -> Any:
        """Create custom visualizations"""
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        
        chart_type = kwargs.get('chart_type', 'auto')
        title = kwargs.get('title', 'Custom Visualization')
        figsize = kwargs.get('figsize', (12, 8))
        save_path = kwargs.get('save_path', None)
        
        # Auto-detect chart type based on data
        if chart_type == 'auto':
            chart_type = self._detect_chart_type(data)
        
        # Create visualization based on type
        if chart_type == 'correlation_heatmap':
            return self._create_correlation_heatmap(data, title, figsize, save_path)
        elif chart_type == 'distribution_plot':
            return self._create_distribution_plot(data, title, figsize, save_path)
        elif chart_type == 'pair_plot':
            return self._create_pair_plot(data, title, figsize, save_path)
        elif chart_type == 'box_plot':
            return self._create_box_plot(data, title, figsize, save_path)
        else:
            return self._create_summary_plot(data, title, figsize, save_path)
    
    def _detect_chart_type(self, data: pd.DataFrame) -> str:
        """Auto-detect the best chart type for the data"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        categorical_cols = data.select_dtypes(include=['object', 'category']).columns
        
        if len(numeric_cols) > 3:
            return 'correlation_heatmap'
        elif len(numeric_cols) > 1:
            return 'pair_plot'
        elif len(numeric_cols) == 1:
            return 'distribution_plot'
        else:
            return 'summary_plot'
    
    def _create_correlation_heatmap(self, data: pd.DataFrame, title: str, figsize: tuple, save_path: Optional[str]) -> plt.Figure:
        """Create correlation heatmap"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for correlation heatmap")
        
        fig, ax = plt.subplots(figsize=figsize)
        correlation_matrix = data[numeric_cols].corr()
        
        # Create heatmap
        sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap='coolwarm',
            center=0,
            square=True,
            ax=ax,
            cbar_kws={'shrink': 0.8}
        )
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _create_distribution_plot(self, data: pd.DataFrame, title: str, figsize: tuple, save_path: Optional[str]) -> plt.Figure:
        """Create distribution plot"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns found for distribution plot")
        
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes
        else:
            axes = axes.flatten()
        
        for i, col in enumerate(numeric_cols):
            if i < len(axes):
                data[col].hist(bins=30, ax=axes[i], alpha=0.7, edgecolor='black')
                axes[i].set_title(f'Distribution of {col}')
                axes[i].set_xlabel(col)
                axes[i].set_ylabel('Frequency')
        
        # Hide unused subplots
        for i in range(len(numeric_cols), len(axes)):
            axes[i].set_visible(False)
        
        fig.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _create_pair_plot(self, data: pd.DataFrame, title: str, figsize: tuple, save_path: Optional[str]) -> plt.Figure:
        """Create pair plot"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            raise ValueError("Need at least 2 numeric columns for pair plot")
        
        # Limit to first 5 columns for readability
        cols_to_plot = numeric_cols[:5]
        
        fig = sns.pairplot(data[cols_to_plot], diag_kind='hist', plot_kws={'alpha': 0.6})
        fig.fig.suptitle(title, y=1.02, fontsize=16, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig.fig
    
    def _create_box_plot(self, data: pd.DataFrame, title: str, figsize: tuple, save_path: Optional[str]) -> plt.Figure:
        """Create box plot"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns found for box plot")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Prepare data for box plot
        plot_data = []
        labels = []
        for col in numeric_cols:
            plot_data.append(data[col].dropna())
            labels.append(col)
        
        ax.boxplot(plot_data, labels=labels)
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_ylabel('Value')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _create_summary_plot(self, data: pd.DataFrame, title: str, figsize: tuple, save_path: Optional[str]) -> plt.Figure:
        """Create summary plot with data overview"""
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        # Data shape info
        axes[0, 0].text(0.1, 0.5, f"Rows: {data.shape[0]}\nColumns: {data.shape[1]}", 
                       fontsize=12, transform=axes[0, 0].transAxes)
        axes[0, 0].set_title('Data Shape')
        axes[0, 0].axis('off')
        
        # Data types
        dtype_counts = data.dtypes.value_counts()
        axes[0, 1].pie(dtype_counts.values, labels=dtype_counts.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Data Types')
        
        # Missing values
        missing_data = data.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if len(missing_data) > 0:
            axes[1, 0].bar(range(len(missing_data)), missing_data.values)
            axes[1, 0].set_xticks(range(len(missing_data)))
            axes[1, 0].set_xticklabels(missing_data.index, rotation=45)
            axes[1, 0].set_title('Missing Values')
        else:
            axes[1, 0].text(0.5, 0.5, 'No Missing Values', 
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Missing Values')
        
        # Memory usage
        memory_usage = data.memory_usage(deep=True)
        axes[1, 1].bar(range(len(memory_usage)), memory_usage.values)
        axes[1, 1].set_xticks(range(len(memory_usage)))
        axes[1, 1].set_xticklabels(memory_usage.index, rotation=45)
        axes[1, 1].set_title('Memory Usage (bytes)')
        
        fig.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        self.initialized = False
        if hasattr(self, 'context'):
            del self.context
