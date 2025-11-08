"""
High-level client for INIA agrometeorological data.

This is the main entry point for the library.
"""

import logging
from typing import Optional, List, Union, Dict
from datetime import datetime
import pandas as pd

from .api_client import APIClient
from .stations import StationManager
from .data import DataDownloader
from .cache import CacheManager

logger = logging.getLogger(__name__)


class INIAClient:
    """
    High-level client for accessing INIA agrometeorological station data.
    
    This is the main class that users interact with. It provides simple,
    high-level methods to query stations and download data.
    
    Example:
        >>> client = INIAClient()
        >>> stations = client.get_stations(region="R16")
        >>> data = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache: bool = True,
        cache_dir: str = "./iniamet_cache"
    ):
        """
        Initialize INIA client.
        
        Args:
            api_key: Optional custom API key
            cache: Enable/disable caching
            cache_dir: Directory for cache files
        """
        self.api = APIClient(api_key=api_key)
        self.cache_manager = CacheManager(cache_dir=cache_dir) if cache else None
        self.station_manager = StationManager(self.api, self.cache_manager)
        self.data_downloader = DataDownloader(self.api, self.cache_manager)
        
        logger.info("INIA Client initialized")
    
    def get_stations(
        self,
        region: Optional[str] = None,
        station_type: Optional[str] = None,
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        Get list of available stations.
        
        Args:
            region: Filter by region code (e.g., "R16" for Ñuble)
            station_type: Filter by station type (e.g., "INIA", "DMC")
            force_update: Force refresh from API (bypass cache)
            
        Returns:
            DataFrame with station information
            
        Example:
            >>> stations = client.get_stations(region="R16")
            >>> print(stations[['codigo', 'nombre', 'region']])
        """
        return self.station_manager.get_stations(
            region=region,
            station_type=station_type,
            force_update=force_update
        )
    
    def get_variables(
        self,
        station: str,
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        Get available variables for a station.
        
        Args:
            station: Station code
            force_update: Force refresh from API (bypass cache)
            
        Returns:
            DataFrame with variable information
            
        Example:
            >>> variables = client.get_variables("INIA-47")
            >>> print(variables[['variable_id', 'nombre', 'unidad']])
        """
        return self.station_manager.get_variables(
            station=station,
            force_update=force_update
        )
    
    def get_data(
        self,
        station: str,
        variable: Union[int, str],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Download time series data for a station and variable.
        
        Args:
            station: Station code
            variable: Variable ID (int) or name (str)
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            use_cache: Use cached data if available
            
        Returns:
            DataFrame with columns: tiempo, valor
            
        Example:
            >>> data = client.get_data(
            ...     station="INIA-47",
            ...     variable=2002,
            ...     start_date="2024-09-01",
            ...     end_date="2024-09-30"
            ... )
            >>> print(data.head())
        """
        return self.data_downloader.get_data(
            station=station,
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            use_cache=use_cache
        )
    
    def bulk_download(
        self,
        stations: List[str],
        variables: List[Union[int, str]],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        delay: float = 0.5
    ) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple stations and variables.
        
        Args:
            stations: List of station codes
            variables: List of variable IDs
            start_date: Start date
            end_date: End date
            delay: Delay between requests (seconds) to avoid rate limiting
            
        Returns:
            Dictionary mapping "station_variable" to DataFrames
            
        Example:
            >>> data = client.bulk_download(
            ...     stations=["INIA-47", "INIA-139"],
            ...     variables=[2002, 2001],
            ...     start_date="2024-09-01",
            ...     end_date="2024-09-30"
            ... )
        """
        return self.data_downloader.bulk_download(
            stations=stations,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
            delay=delay
        )
    
    def validate_station_variable(
        self,
        station: str,
        variable: Union[int, str]
    ) -> bool:
        """
        Check if a variable is available for a station.
        
        Args:
            station: Station code
            variable: Variable ID or name
            
        Returns:
            True if variable is available, False otherwise
        """
        return self.station_manager.validate_station_variable(
            station=station,
            variable=variable
        )
    
    def close(self):
        """Close connections and cleanup."""
        self.api.close()
        logger.info("INIA Client closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
