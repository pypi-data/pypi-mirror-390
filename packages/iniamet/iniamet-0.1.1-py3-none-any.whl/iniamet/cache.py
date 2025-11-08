"""
Caching system for INIA data.

Provides simple JSON-based caching for stations, variables, and time series data.
"""

import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages local cache for API responses."""
    
    def __init__(self, cache_dir: str = "./iniamet_cache"):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.stations_cache = self.cache_dir / "stations"
        self.variables_cache = self.cache_dir / "variables"
        self.data_cache = self.cache_dir / "data"
        
        self.stations_cache.mkdir(exist_ok=True)
        self.variables_cache.mkdir(exist_ok=True)
        self.data_cache.mkdir(exist_ok=True)
        
        logger.info(f"Cache directory: {self.cache_dir}")
    
    def get_stations(self) -> Optional[pd.DataFrame]:
        """
        Get cached stations.
        
        Returns:
            DataFrame if cache exists, None otherwise
        """
        cache_file = self.stations_cache / "all_stations.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except Exception as e:
            logger.warning(f"Failed to load stations cache: {e}")
            return None
    
    def save_stations(self, df: pd.DataFrame):
        """
        Save stations to cache.
        
        Args:
            df: Stations DataFrame
        """
        cache_file = self.stations_cache / "all_stations.json"
        
        try:
            data = df.to_dict(orient='records')
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(df)} stations to cache")
        except Exception as e:
            logger.error(f"Failed to save stations cache: {e}")
    
    def get_variables(self, station: str) -> Optional[pd.DataFrame]:
        """
        Get cached variables for a station.
        
        Args:
            station: Station code
            
        Returns:
            DataFrame if cache exists, None otherwise
        """
        cache_file = self.variables_cache / f"{station}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except Exception as e:
            logger.warning(f"Failed to load variables cache for {station}: {e}")
            return None
    
    def save_variables(self, station: str, df: pd.DataFrame):
        """
        Save variables to cache.
        
        Args:
            station: Station code
            df: Variables DataFrame
        """
        cache_file = self.variables_cache / f"{station}.json"
        
        try:
            data = df.to_dict(orient='records')
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved {len(df)} variables for {station} to cache")
        except Exception as e:
            logger.error(f"Failed to save variables cache for {station}: {e}")
    
    def get_data(
        self,
        station: str,
        variable: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Get cached time series data.
        
        Args:
            station: Station code
            variable: Variable ID
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame if cache exists and covers date range, None otherwise
        """
        cache_file = self.data_cache / f"{station}_{variable}.parquet"
        
        if not cache_file.exists():
            return None
        
        try:
            df = pd.read_parquet(cache_file)
            
            # Check if cache covers requested date range
            if df.empty:
                return None
            
            df['tiempo'] = pd.to_datetime(df['tiempo'])
            cache_start = df['tiempo'].min()
            cache_end = df['tiempo'].max()
            
            if cache_start <= start_date and cache_end >= end_date:
                # Filter to requested range
                mask = (df['tiempo'] >= start_date) & (df['tiempo'] <= end_date)
                return df[mask].copy()
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to load data cache for {station}/{variable}: {e}")
            return None
    
    def save_data(self, station: str, variable: str, df: pd.DataFrame):
        """
        Save time series data to cache.
        
        Args:
            station: Station code
            variable: Variable ID
            df: Data DataFrame
        """
        if df.empty:
            return
        
        cache_file = self.data_cache / f"{station}_{variable}.parquet"
        
        try:
            # Merge with existing cache if present
            if cache_file.exists():
                df_existing = pd.read_parquet(cache_file)
                df_existing['tiempo'] = pd.to_datetime(df_existing['tiempo'])
                
                # Combine and deduplicate
                df_combined = pd.concat([df_existing, df], ignore_index=True)
                df_combined = df_combined.drop_duplicates(subset=['tiempo'])
                df_combined = df_combined.sort_values('tiempo')
                
                df_combined.to_parquet(cache_file, index=False)
                logger.debug(f"Updated cache for {station}/{variable} ({len(df_combined)} records)")
            else:
                df.to_parquet(cache_file, index=False)
                logger.debug(f"Saved cache for {station}/{variable} ({len(df)} records)")
                
        except Exception as e:
            logger.error(f"Failed to save data cache for {station}/{variable}: {e}")
    
    def clear_cache(self):
        """Clear all cache files."""
        import shutil
        try:
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
