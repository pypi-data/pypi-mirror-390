"""
INIAMET - Chilean INIA Agrometeorological Data Library

An unofficial, high-level Python library for accessing Chilean INIA 
agrometeorological station data.

DISCLAIMER: This library is NOT officially affiliated with, endorsed by, 
or maintained by INIA (Instituto de Investigaciones Agropecuarias). 
It accesses publicly available data from INIA's agrometeorological API.

Example usage:
    >>> from iniamet import INIAClient
    >>> client = INIAClient()
    >>> stations = client.get_stations(region="R16")
    >>> print(len(stations))
    
    # Quality control
    >>> from iniamet.qc import apply_quality_control
    >>> clean_data = apply_quality_control(df, 'temperatura')
    
    # Visualization
    >>> from iniamet.visualization import quick_temp_map
    >>> mapa = quick_temp_map(client, region='Ñuble', date='2025-10-12')
"""

__version__ = "0.1.1"
__author__ = "INIA Climate Data Team"
__license__ = "MIT"

from .client import INIAClient
from .stations import StationManager
from .data import DataDownloader
from .regional import RegionalDownloader
from .qc import QualityControl, apply_quality_control, get_qc_report
from .utils import get_region_name, get_variable_info, REGION_MAP, VARIABLE_INFO

# Import visualization only if IPython is available (optional dependency)
try:
    from .visualization import plot_temperature_map, plot_station_map, quick_temp_map
    _HAS_VISUALIZATION = True
except ImportError:
    _HAS_VISUALIZATION = False
    plot_temperature_map = None
    plot_station_map = None
    quick_temp_map = None

__all__ = [
    "INIAClient",
    "StationManager",
    "DataDownloader",
    "RegionalDownloader",
    "QualityControl",
    "apply_quality_control",
    "get_qc_report",
    "plot_temperature_map",
    "plot_station_map",
    "quick_temp_map",
    "get_region_name",
    "get_variable_info",
    "REGION_MAP",
    "VARIABLE_INFO",
]
