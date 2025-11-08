"""
Regional downloader for bulk climate data downloads.

Simplifies downloading data for entire regions with common climate variables.
"""

import logging
from typing import Optional, List, Union
from datetime import datetime
import pandas as pd

from .client import INIAClient
from .utils import parse_date, normalize_text

logger = logging.getLogger(__name__)


class RegionalDownloader:
    """High-level downloader for regional climate data."""
    
    # Common variable mappings
    VARIABLE_MAPPING = {
        'temperature': 2002,  # Temperatura del Aire Media
        'precipitation': 2001,  # Precipitación
        'humidity': 2007,  # Humedad Relativa Media
        'wind_speed': 2013,  # Velocidad Viento Media
        'radiation': 2022,  # Radiación Media
        'pressure': 2125,  # Presión Atmosférica
    }
    
    def __init__(
        self,
        region: str,
        client: Optional[INIAClient] = None
    ):
        """
        Initialize regional downloader.
        
        Args:
            region: Region code (e.g., "R16") or name (e.g., "Ñuble")
            client: Optional INIAClient instance (creates new if not provided)
        """
        self.region = region
        self.client = client or INIAClient()
        
        # Get stations for region
        self.stations = self.client.get_stations(region=region)
        
        if self.stations.empty:
            logger.warning(f"No stations found for region {region}")
        else:
            logger.info(f"Found {len(self.stations)} stations in region {region}")
    
    def download_climate_data(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        variables: Optional[List[str]] = None,
        aggregation: str = 'daily',
        station_filter: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Download and consolidate climate data for region.
        
        Args:
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            variables: List of variable names (e.g., ['temperature', 'precipitation'])
                      If None, downloads temperature and precipitation
            aggregation: 'daily', 'raw', or pandas resample rule (e.g., 'W', 'M')
            station_filter: Optional list of specific station codes to download
            
        Returns:
            Consolidated DataFrame with all stations and variables
            
        Example:
            >>> downloader = RegionalDownloader("R16")
            >>> df = downloader.download_climate_data(
            ...     start_date="2024-09-01",
            ...     end_date="2024-09-30",
            ...     variables=['temperature', 'precipitation'],
            ...     aggregation='daily'
            ... )
        """
        # Default variables
        if variables is None:
            variables = ['temperature', 'precipitation']
        
        # Resolve variable IDs
        var_ids = []
        for var in variables:
            if var.lower() in self.VARIABLE_MAPPING:
                var_ids.append(self.VARIABLE_MAPPING[var.lower()])
            else:
                logger.warning(f"Unknown variable: {var}")
        
        if not var_ids:
            logger.error("No valid variables specified")
            return pd.DataFrame()
        
        # Filter stations if requested
        stations_to_use = self.stations.copy()
        if station_filter:
            stations_to_use = stations_to_use[
                stations_to_use['codigo'].isin(station_filter)
            ]
        
        if stations_to_use.empty:
            logger.error("No stations to download")
            return pd.DataFrame()
        
        # Download data for each station
        all_data = []
        
        for idx, station_row in stations_to_use.iterrows():
            station_code = station_row['codigo']
            station_name = station_row['nombre']
            
            logger.info(f"[{idx+1}/{len(stations_to_use)}] {station_code} - {station_name}")
            
            station_data = {
                'estacion_codigo': station_code,
                'estacion_nombre': station_name,
                'region': station_row['region'],
                'latitud': station_row['latitud'],
                'longitud': station_row['longitud'],
                'elevacion': station_row['elevacion']
            }
            
            # Download each variable
            for var_id in var_ids:
                try:
                    df = self.client.get_data(
                        station=station_code,
                        variable=var_id,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if df.empty:
                        logger.warning(f"  No data for variable {var_id}")
                        continue
                    
                    # Apply aggregation
                    if aggregation == 'daily':
                        df = self._aggregate_daily(df, var_id)
                    elif aggregation != 'raw':
                        df = self._aggregate_custom(df, aggregation)
                    
                    # Add variable columns to station data
                    for col in df.columns:
                        if col != 'tiempo':
                            station_data[col] = df[col].values
                    
                    if 'tiempo' not in station_data:
                        station_data['tiempo'] = df['tiempo'].values
                    
                    logger.info(f"  ✓ Variable {var_id}: {len(df)} records")
                    
                except Exception as e:
                    logger.error(f"  ✗ Variable {var_id}: {e}")
                    continue
            
            # Create DataFrame for this station
            if 'tiempo' in station_data:
                df_station = pd.DataFrame({
                    'tiempo': station_data['tiempo']
                })
                
                for key, value in station_data.items():
                    if key != 'tiempo':
                        if isinstance(value, (list, pd.Series)):
                            df_station[key] = value
                        else:
                            df_station[key] = value
                
                all_data.append(df_station)
        
        # Consolidate all stations
        if not all_data:
            logger.error("No data downloaded")
            return pd.DataFrame()
        
        df_final = pd.concat(all_data, ignore_index=True)
        df_final = df_final.sort_values(['estacion_codigo', 'tiempo'])
        df_final = df_final.reset_index(drop=True)
        
        logger.info(f"Download complete: {len(df_final)} total records")
        return df_final
    
    def _aggregate_daily(self, df: pd.DataFrame, var_id: int) -> pd.DataFrame:
        """Aggregate data to daily based on variable type."""
        if df.empty:
            return df
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        
        # Temperature: compute min/max/mean
        if var_id == 2002:  # Temperature
            df_daily = df.resample('D').agg({
                'valor': ['mean', 'min', 'max']
            })
            df_daily.columns = ['tmedia', 'tmin', 'tmax']
        
        # Precipitation: sum
        elif var_id == 2001:  # Precipitation
            df_daily = df.resample('D').sum()
            df_daily.columns = ['pp_acum']
        
        # Others: mean
        else:
            df_daily = df.resample('D').mean()
            df_daily.columns = [f'var_{var_id}']
        
        df_daily = df_daily.reset_index()
        return df_daily
    
    def _aggregate_custom(self, df: pd.DataFrame, rule: str) -> pd.DataFrame:
        """Apply custom aggregation rule."""
        if df.empty:
            return df
        
        df = df.copy()
        df.set_index('tiempo', inplace=True)
        df_agg = df.resample(rule).mean()
        df_agg = df_agg.reset_index()
        return df_agg
    
    def save_to_csv(
        self,
        df: pd.DataFrame,
        filename: Optional[str] = None
    ) -> str:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Output filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            region_code = self.region if self.region.startswith('R') else 'region'
            filename = f"clima_{region_code.lower()}.csv"
        
        df.to_csv(filename, index=False)
        logger.info(f"Saved to {filename} ({len(df)} records)")
        
        return filename
