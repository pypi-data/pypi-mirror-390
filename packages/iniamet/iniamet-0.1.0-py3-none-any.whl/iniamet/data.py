"""
Data downloading module.

Handles time series data retrieval with caching and aggregation support.
"""

import logging
import time
from typing import Optional, List, Union, Dict
from datetime import datetime
import pandas as pd

from .api_client import APIClient
from .cache import CacheManager
from .utils import parse_date

logger = logging.getLogger(__name__)


class DataDownloader:
    """Handles data downloads from INIA API."""
    
    def __init__(self, api: APIClient, cache: Optional[CacheManager] = None):
        """
        Initialize data downloader.
        
        Args:
            api: API client instance
            cache: Optional cache manager
        """
        self.api = api
        self.cache = cache
    
    def get_data(
        self,
        station: str,
        variable: Union[int, str],
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Download time series data.
        
        Args:
            station: Station code
            variable: Variable ID
            start_date: Start date
            end_date: End date
            use_cache: Use cached data if available
            
        Returns:
            DataFrame with columns: tiempo (datetime), valor (float)
        """
        # Parse dates
        start_dt = parse_date(start_date)
        end_dt = parse_date(end_date)
        
        # Convert variable to string
        var_str = str(variable)
        
        # Check cache
        if self.cache and use_cache:
            df_cached = self.cache.get_data(station, var_str, start_dt, end_dt)
            if df_cached is not None and not df_cached.empty:
                logger.info(
                    f"Using cached data for {station}/{var_str} "
                    f"({len(df_cached)} records)"
                )
                return df_cached
        
        # Download from API
        logger.info(f"Downloading data for {station}/{var_str}...")
        
        data = self.api.get_data(
            station=station,
            variable=var_str,
            start_date=start_dt.strftime('%Y-%m-%d'),
            end_date=end_dt.strftime('%Y-%m-%d')
        )
        
        if not data:
            logger.warning(f"No data found for {station}/{var_str}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Parse tiempo column
        if 'tiempo' in df.columns:
            df['tiempo'] = pd.to_datetime(df['tiempo'])
        
        # Parse valor column
        if 'valor' in df.columns:
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
        
        # Sort by time
        if not df.empty:
            df = df.sort_values('tiempo').reset_index(drop=True)
        
        # Save to cache
        if self.cache and not df.empty:
            self.cache.save_data(station, var_str, df)
        
        logger.info(f"Downloaded {len(df)} records")
        return df
    
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
            delay: Delay between requests (seconds)
            
        Returns:
            Dictionary mapping "station_variable" to DataFrames
        """
        results = {}
        total = len(stations) * len(variables)
        current = 0
        
        logger.info(f"Bulk download: {len(stations)} stations × {len(variables)} variables = {total} tasks")
        
        for station in stations:
            for variable in variables:
                current += 1
                key = f"{station}_{variable}"
                
                logger.info(f"[{current}/{total}] Downloading {key}...")
                
                try:
                    df = self.get_data(
                        station=station,
                        variable=variable,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if not df.empty:
                        results[key] = df
                        logger.info(f"  ✓ {key}: {len(df)} records")
                    else:
                        logger.warning(f"  ⚠ {key}: No data")
                    
                    # Rate limiting
                    if current < total:
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"  ✗ {key}: {e}")
                    continue
        
        logger.info(f"Bulk download complete: {len(results)}/{total} successful")
        return results
    
    def aggregate_daily(
        self,
        df: pd.DataFrame,
        agg_func: str = 'mean'
    ) -> pd.DataFrame:
        """
        Aggregate sub-daily data to daily.
        
        Args:
            df: DataFrame with 'tiempo' and 'valor' columns
            agg_func: Aggregation function ('mean', 'sum', 'min', 'max')
            
        Returns:
            Daily aggregated DataFrame
        """
        if df.empty or 'tiempo' not in df.columns:
            return df
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        
        if agg_func == 'mean':
            df_daily = df.resample('D').mean()
        elif agg_func == 'sum':
            df_daily = df.resample('D').sum()
        elif agg_func == 'min':
            df_daily = df.resample('D').min()
        elif agg_func == 'max':
            df_daily = df.resample('D').max()
        else:
            raise ValueError(f"Unknown aggregation function: {agg_func}")
        
        df_daily = df_daily.reset_index()
        return df_daily
    
    def aggregate_temperature_daily(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate temperature data to daily min/max/mean.
        
        Args:
            df: DataFrame with 'tiempo' and 'valor' columns
            
        Returns:
            Daily DataFrame with columns: tiempo, tmean, tmin, tmax
        """
        if df.empty or 'tiempo' not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        
        df_daily = df.resample('D').agg({
            'valor': ['mean', 'min', 'max']
        })
        
        df_daily.columns = ['tmean', 'tmin', 'tmax']
        df_daily = df_daily.reset_index()
        
        return df_daily
