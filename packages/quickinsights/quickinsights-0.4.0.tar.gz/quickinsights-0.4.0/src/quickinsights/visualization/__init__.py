"""
Creative Visualization Module

Provides innovative and creative visualization capabilities
beyond traditional matplotlib/seaborn charts.
"""

from .charts import (
    create_radar_chart,
    create_3d_scatter,
    create_heatmap,
    create_bubble_chart
)

from .advanced_charts import (
    create_sunburst_chart,
    create_parallel_coordinates,
    create_animated_scatter,
    create_3d_surface
)

from .specialized_charts import (
    create_waterfall_chart,
    create_funnel_chart,
    create_gantt_chart,
    create_sankey_diagram
)

from .maps import (
    create_choropleth_map,
    create_scatter_mapbox,
    create_density_mapbox
)

__all__ = [
    # Basic charts
    'create_radar_chart',
    'create_3d_scatter', 
    'create_heatmap',
    'create_bubble_chart',
    
    # Advanced charts
    'create_sunburst_chart',
    'create_parallel_coordinates',
    'create_animated_scatter',
    'create_3d_surface',
    
    # Specialized charts
    'create_waterfall_chart',
    'create_funnel_chart',
    'create_gantt_chart',
    'create_sankey_diagram',
    
    # Maps
    'create_choropleth_map',
    'create_scatter_mapbox',
    'create_density_mapbox'
]
