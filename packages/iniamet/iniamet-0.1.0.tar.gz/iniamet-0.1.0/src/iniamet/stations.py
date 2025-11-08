"""
Station management module.

Handles station queries, filtering, and variable validation.
"""

import logging
from typing import Optional, List, Union
import pandas as pd

from .api_client import APIClient
from .cache import CacheManager
from .utils import normalize_text, REGION_MAP

logger = logging.getLogger(__name__)


class StationManager:
    """Manages station catalog and queries."""
    
    def __init__(self, api: APIClient, cache: Optional[CacheManager] = None):
        """
        Initialize station manager.
        
        Args:
            api: API client instance
            cache: Optional cache manager
        """
        self.api = api
        self.cache = cache
        self._stations_cache: Optional[pd.DataFrame] = None
    
    def get_stations(
        self,
        region: Optional[str] = None,
        station_type: Optional[str] = None,
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        Get stations with optional filtering.
        
        Args:
            region: Region code (e.g., "R16") or name (e.g., "Ñuble")
            station_type: Station type prefix (e.g., "INIA", "DMC")
            force_update: Force refresh from API
            
        Returns:
            DataFrame with columns: codigo, nombre, region, comuna, 
                                   latitud, longitud, elevacion, tipo
        """
        # Check memory cache
        if self._stations_cache is not None and not force_update:
            logger.info("Using cached stations from memory")
            df = self._stations_cache.copy()
        else:
            # Try disk cache
            if self.cache and not force_update:
                df = self.cache.get_stations()
                if df is not None:
                    logger.info("Using cached stations from disk")
                    self._stations_cache = df.copy()
                    return self._filter_stations(df, region, station_type)
            
            # Fetch from API
            logger.info("Fetching stations from API...")
            data = self.api.get_stations()
            
            if not data:
                return pd.DataFrame()
            
            # Normalize station data
            stations = []
            for item in data:
                # Extract station type from code (e.g., "INIA" from "INIA-47")
                codigo = item.get('identificador', '')
                tipo = codigo.split('-')[0] if '-' in codigo else 'OTHER'
                
                stations.append({
                    'codigo': codigo,
                    'nombre': item.get('nombre', ''),
                    'region': item.get('region', ''),
                    'comuna': item.get('comuna', ''),
                    'latitud': item.get('latitud'),
                    'longitud': item.get('longitud'),
                    'elevacion': item.get('elevacion'),
                    'tipo': tipo,
                    'primera_lectura': item.get('primer_dato', '')
                })
            
            df = pd.DataFrame(stations)
            
            # Save to caches
            if self.cache:
                self.cache.save_stations(df)
            self._stations_cache = df.copy()
            
            logger.info(f"Retrieved {len(df)} stations")
        
        return self._filter_stations(df, region, station_type)
    
    def _filter_stations(
        self,
        df: pd.DataFrame,
        region: Optional[str] = None,
        station_type: Optional[str] = None
    ) -> pd.DataFrame:
        """Apply filters to station DataFrame."""
        if df.empty:
            return df
        
        result = df.copy()
        
        # Filter by region
        if region:
            # Convert region code to name if needed
            if region.upper().startswith('R'):
                region_name = REGION_MAP.get(region.upper())
                if region_name:
                    result = result[result['region'] == region_name]
                else:
                    logger.warning(f"Unknown region code: {region}")
                    return pd.DataFrame()
            else:
                # Direct region name match
                result = result[
                    result['region'].str.lower() == region.lower()
                ]
        
        # Filter by station type
        if station_type:
            result = result[
                result['tipo'].str.upper() == station_type.upper()
            ]
        
        logger.info(f"Filtered to {len(result)} stations")
        return result.reset_index(drop=True)
    
    def get_variables(
        self,
        station: str,
        force_update: bool = False
    ) -> pd.DataFrame:
        """
        Get available variables for a station.
        
        Args:
            station: Station code
            force_update: Force refresh from API
            
        Returns:
            DataFrame with columns: variable_id, nombre, unidad
        """
        # Check cache
        if self.cache and not force_update:
            df = self.cache.get_variables(station)
            if df is not None:
                logger.info(f"Using cached variables for {station}")
                return df
        
        # Fetch from API
        logger.info(f"Fetching variables for {station}...")
        data = self.api.get_variables(station)
        
        if not data:
            return pd.DataFrame()
        
        # Normalize variable data
        variables = []
        for item in data:
            variables.append({
                'variable_id': item.get('identificador'),
                'nombre': item.get('nombre', ''),
                'unidad': item.get('unidad', '')
            })
        
        df = pd.DataFrame(variables)
        
        # Save to cache
        if self.cache:
            self.cache.save_variables(station, df)
        
        logger.info(f"Retrieved {len(df)} variables for {station}")
        return df
    
    def validate_station_variable(
        self,
        station: str,
        variable: Union[int, str]
    ) -> bool:
        """
        Check if a variable exists for a station.
        
        Args:
            station: Station code
            variable: Variable ID (int) or name (str)
            
        Returns:
            True if variable exists, False otherwise
        """
        df_vars = self.get_variables(station)
        
        if df_vars.empty:
            return False
        
        # Check by ID
        if isinstance(variable, int) or variable.isdigit():
            var_id = int(variable)
            return var_id in df_vars['variable_id'].values
        
        # Check by name (fuzzy match)
        variable_lower = normalize_text(str(variable))
        for nombre in df_vars['nombre']:
            if variable_lower in normalize_text(nombre):
                return True
        
        return False
    
    def find_variable_id(
        self,
        station: str,
        variable_name: str
    ) -> Optional[int]:
        """
        Find variable ID by name.
        
        Args:
            station: Station code
            variable_name: Variable name (e.g., "temperatura", "precipitacion")
            
        Returns:
            Variable ID if found, None otherwise
        """
        df_vars = self.get_variables(station)
        
        if df_vars.empty:
            return None
        
        variable_lower = normalize_text(variable_name)
        
        for _, row in df_vars.iterrows():
            if variable_lower in normalize_text(row['nombre']):
                return int(row['variable_id'])
        
        return None
