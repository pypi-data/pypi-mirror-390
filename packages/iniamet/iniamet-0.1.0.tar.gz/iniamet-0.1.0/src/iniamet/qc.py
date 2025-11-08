"""
Quality Control (QC) module for INIA meteorological data.

Provides high-level functions to detect and filter erroneous data.
"""

import logging
from typing import Optional, Dict, List, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


# Rangos físicamente posibles para variables comunes
PHYSICAL_RANGES = {
    # Temperatura del aire (°C)
    'temperatura': {'min': -50, 'max': 60},
    'temperatura_aire': {'min': -50, 'max': 60},
    'temp': {'min': -50, 'max': 60},
    
    # Humedad relativa (%)
    'humedad': {'min': 0, 'max': 100},
    'humedad_relativa': {'min': 0, 'max': 100},
    
    # Precipitación (mm)
    'precipitacion': {'min': 0, 'max': 500},
    'lluvia': {'min': 0, 'max': 500},
    
    # Velocidad del viento (m/s)
    'viento': {'min': 0, 'max': 100},
    'velocidad_viento': {'min': 0, 'max': 100},
    
    # Radiación solar (W/m²)
    'radiacion': {'min': 0, 'max': 1500},
    'radiacion_solar': {'min': 0, 'max': 1500},
    
    # Presión atmosférica (hPa)
    'presion': {'min': 800, 'max': 1100},
    'presion_atmosferica': {'min': 800, 'max': 1100},
}

# Rangos esperados (más estrictos) - ajustados para Chile central
EXPECTED_RANGES = {
    'temperatura': {'min': -10, 'max': 40},  # Más estricto: -18.5°C será detectado
    'temperatura_aire': {'min': -10, 'max': 40},
    'humedad': {'min': 5, 'max': 100},
    'humedad_relativa': {'min': 5, 'max': 100},
    'precipitacion': {'min': 0, 'max': 200},
    'viento': {'min': 0, 'max': 50},
    'radiacion': {'min': 0, 'max': 1200},
}


class QualityControl:
    """
    Quality control for meteorological data.
    
    Provides methods to detect and filter common data quality issues:
    - Physically impossible values
    - Extreme values (outliers)
    - Stuck sensors (repeated values)
    - Sudden unrealistic changes
    - Consecutive zeros
    """
    
    def __init__(self):
        """Initialize QC engine."""
        self.qc_flags = []
    
    def detect_impossible_values(
        self,
        df: pd.DataFrame,
        variable_name: str = 'temperatura',
        value_col: str = 'valor'
    ) -> pd.DataFrame:
        """
        Detect physically impossible values.
        
        Args:
            df: DataFrame with time series data
            variable_name: Variable type (temperatura, humedad, etc.)
            value_col: Column name containing values
            
        Returns:
            DataFrame with added column 'qc_impossible' (True = invalid)
            
        Example:
            >>> qc = QualityControl()
            >>> df_clean = qc.detect_impossible_values(df, 'temperatura')
            >>> print(f"Invalid values: {df_clean['qc_impossible'].sum()}")
        """
        df = df.copy()
        
        # Get physical range
        var_key = self._normalize_variable_name(variable_name)
        ranges = PHYSICAL_RANGES.get(var_key, {'min': -np.inf, 'max': np.inf})
        
        # Flag impossible values
        df['qc_impossible'] = (
            (df[value_col] < ranges['min']) | 
            (df[value_col] > ranges['max'])
        )
        
        n_invalid = df['qc_impossible'].sum()
        if n_invalid > 0:
            logger.warning(
                f"Found {n_invalid} physically impossible values "
                f"(outside {ranges['min']}-{ranges['max']})"
            )
        
        return df
    
    def detect_extreme_values(
        self,
        df: pd.DataFrame,
        variable_name: str = 'temperatura',
        value_col: str = 'valor',
        method: str = 'range'
    ) -> pd.DataFrame:
        """
        Detect extreme values (Test de rango fijo - WMO, 1993; Zahumensky, 2004).
        
        Args:
            df: DataFrame with time series data
            variable_name: Variable type
            value_col: Column name containing values
            method: Detection method ('range' or 'iqr')
            
        Returns:
            DataFrame with added column 'qc_extreme' (True = outlier)
            
        Example:
            >>> qc = QualityControl()
            >>> df_clean = qc.detect_extreme_values(df, 'temperatura')
        """
        df = df.copy()
        
        if method == 'range':
            # Test de rango fijo (WMO, 1993)
            var_key = self._normalize_variable_name(variable_name)
            ranges = EXPECTED_RANGES.get(var_key, {'min': -np.inf, 'max': np.inf})
            
            df['qc_extreme'] = (
                (df[value_col] < ranges['min']) | 
                (df[value_col] > ranges['max'])
            )
        
        elif method == 'iqr':
            # Use IQR method
            Q1 = df[value_col].quantile(0.25)
            Q3 = df[value_col].quantile(0.75)
            IQR = Q3 - Q1
            
            df['qc_extreme'] = (
                (df[value_col] < (Q1 - 3 * IQR)) | 
                (df[value_col] > (Q3 + 3 * IQR))
            )
        
        n_extreme = df['qc_extreme'].sum()
        if n_extreme > 0:
            logger.warning(f"Found {n_extreme} extreme values (WMO fixed range test)")
        
        return df
    
    def detect_stuck_sensor(
        self,
        df: pd.DataFrame,
        value_col: str = 'valor',
        min_repeats: int = 4,
        tolerance: float = 0.001
    ) -> pd.DataFrame:
        """
        Detect stuck sensor (Test de persistencia - Meek & Hatfield, 1994).
        
        Verifica que los registros no sean iguales durante un periodo de 4 horas.
        
        Args:
            df: DataFrame with time series data
            value_col: Column name containing values
            min_repeats: Minimum consecutive repeats to flag (default 4 horas)
            tolerance: Tolerance for "same" value
            
        Returns:
            DataFrame with added column 'qc_stuck' (True = stuck)
            
        Example:
            >>> qc = QualityControl()
            >>> df_clean = qc.detect_stuck_sensor(df, min_repeats=4)
        """
        df = df.copy()
        df['qc_stuck'] = False
        
        if len(df) < min_repeats:
            return df
        
        # Find consecutive repeats (Test de persistencia)
        diff = df[value_col].diff().abs()
        is_same = diff <= tolerance
        
        # Count consecutive
        groups = (is_same != is_same.shift()).cumsum()
        repeat_counts = is_same.groupby(groups).transform('sum')
        
        # Flag if >= min_repeats (4 horas por defecto - Meek & Hatfield, 1994)
        df['qc_stuck'] = (is_same) & (repeat_counts >= min_repeats - 1)
        
        n_stuck = df['qc_stuck'].sum()
        if n_stuck > 0:
            logger.warning(f"Found {n_stuck} stuck sensor readings (persistence test)")
        
        return df
    
    def detect_sudden_changes(
        self,
        df: pd.DataFrame,
        variable_name: str = 'temperatura',
        value_col: str = 'valor',
        time_col: str = 'tiempo',
        max_change_per_hour: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Detect sudden unrealistic changes (Test de consistencia temporal - WMO, 1993).
        
        Para temperatura: 
        - Datos cada 15 min: verifica saltos > 4°C por hora
        - Datos horarios: verifica saltos > 10°C por hora
        - Ignora cambios si hay gaps > 2 horas
        
        Args:
            df: DataFrame with time series data
            variable_name: Variable type
            value_col: Column name containing values
            time_col: Column name containing timestamps
            max_change_per_hour: Max allowed change per hour (auto if None)
            
        Returns:
            DataFrame with added column 'qc_sudden' (True = sudden change)
            
        Example:
            >>> qc = QualityControl()
            >>> df_clean = qc.detect_sudden_changes(df, 'temperatura')
        """
        df = df.copy()
        df['qc_sudden'] = False
        
        if len(df) < 2:
            return df
        
        # Calculate time differences in hours
        df[time_col] = pd.to_datetime(df[time_col])
        time_diff = df[time_col].diff().dt.total_seconds() / 3600
        
        # Calculate median time interval to determine data frequency
        median_interval = time_diff.median()
        
        # Thresholds según test de consistencia temporal (WMO, 1993)
        if max_change_per_hour is None:
            var_key = self._normalize_variable_name(variable_name)
            
            if var_key == 'temperatura':
                # Adaptive threshold based on data frequency
                if median_interval <= 0.5:  # ~15-30 min intervals
                    max_change_per_hour = 4.0   # 4°C por hora para datos de alta frecuencia
                else:  # hourly or coarser
                    max_change_per_hour = 10.0  # 10°C por hora para datos horarios
            else:
                # Default thresholds for other variables
                thresholds = {
                    'humedad': 45.0,      # 45% (Estevez, 2011)
                    'presion': 10.0,      # 10 hPa por hora
                    'radiacion': 555.0,   # 555 W/m² (Meek & Hatfield, 1994)
                    'viento': 10.0,       # 10 m/s (Meek & Hatfield, 1994)
                }
                max_change_per_hour = thresholds.get(var_key, 999.0)
        
        # Calculate value changes
        value_diff = df[value_col].diff().abs()
        
        # Rate of change per hour (Test de consistencia temporal)
        change_rate = value_diff / time_diff.replace(0, np.nan)
        
        # Flag sudden changes, but ignore if gap > 2 hours (to avoid false positives from missing data)
        df['qc_sudden'] = (change_rate > max_change_per_hour) & (time_diff <= 2.0)
        
        n_sudden = df['qc_sudden'].sum()
        if n_sudden > 0:
            logger.warning(f"Found {n_sudden} sudden changes (temporal consistency test, >{max_change_per_hour:.1f}/h, gaps <=2h)")
        
        return df
    
    def detect_consecutive_zeros(
        self,
        df: pd.DataFrame,
        value_col: str = 'valor',
        min_zeros: int = 10
    ) -> pd.DataFrame:
        """
        Detect suspicious consecutive zeros.
        
        Args:
            df: DataFrame with time series data
            value_col: Column name containing values
            min_zeros: Minimum consecutive zeros to flag
            
        Returns:
            DataFrame with added column 'qc_zeros' (True = suspicious)
            
        Example:
            >>> qc = QualityControl()
            >>> df_clean = qc.detect_consecutive_zeros(df, min_zeros=5)
        """
        df = df.copy()
        df['qc_zeros'] = False
        
        if len(df) < min_zeros:
            return df
        
        # Find zeros
        is_zero = df[value_col] == 0
        
        # Count consecutive
        groups = (is_zero != is_zero.shift()).cumsum()
        zero_counts = is_zero.groupby(groups).transform('sum')
        
        # Flag if >= min_zeros
        df['qc_zeros'] = (is_zero) & (zero_counts >= min_zeros)
        
        n_zeros = df['qc_zeros'].sum()
        if n_zeros > 0:
            logger.warning(f"Found {n_zeros} suspicious consecutive zeros")
        
        return df
    
    def check_internal_consistency_temperature(
        self,
        df: pd.DataFrame,
        tmin_col: str = 'tmin',
        tmean_col: str = 'tmean',
        tmax_col: str = 'tmax'
    ) -> pd.DataFrame:
        """
        Test de consistencia interna para temperatura (Feng et al., 2004; Kunkel et al., 1998).
        
        Verifica que: Tmax > Tmean > Tmin
        
        Args:
            df: DataFrame con datos de temperatura
            tmin_col: Columna de temperatura mínima
            tmean_col: Columna de temperatura media
            tmax_col: Columna de temperatura máxima
            
        Returns:
            DataFrame con columna 'qc_temp_consistency' (True = inconsistente)
        """
        df = df.copy()
        
        # Verificar que existan las columnas necesarias
        required = [tmin_col, tmean_col, tmax_col]
        if not all(col in df.columns for col in required):
            logger.warning("Missing temperature columns for internal consistency check")
            df['qc_temp_consistency'] = False
            return df
        
        # Test: Tmax > Tmean > Tmin (WMO, 1993; Feng et al., 2004)
        df['qc_temp_consistency'] = (
            (df[tmax_col] <= df[tmean_col]) |
            (df[tmean_col] <= df[tmin_col]) |
            (df[tmax_col] <= df[tmin_col])
        )
        
        n_inconsistent = df['qc_temp_consistency'].sum()
        if n_inconsistent > 0:
            logger.warning(f"Found {n_inconsistent} temperature internal consistency violations (Tmax > Tmean > Tmin)")
        
        return df
    
    def check_internal_consistency_wind(
        self,
        df: pd.DataFrame,
        wind_col: str = 'viento',
        wind_max_col: str = 'viento_max',
        direction_col: str = 'direccion'
    ) -> pd.DataFrame:
        """
        Test de consistencia interna para viento (Meek & Hatfield, 1994).
        
        Verifica que:
        1. Viento_max > Viento_medio
        2. Si Viento = 0, entonces Dirección = 0
        
        Args:
            df: DataFrame con datos de viento
            wind_col: Columna de velocidad media del viento
            wind_max_col: Columna de velocidad máxima del viento
            direction_col: Columna de dirección del viento
            
        Returns:
            DataFrame con columna 'qc_wind_consistency' (True = inconsistente)
        """
        df = df.copy()
        df['qc_wind_consistency'] = False
        
        # Test 1: Viento_max > Viento_medio
        if wind_col in df.columns and wind_max_col in df.columns:
            df.loc[df[wind_max_col] < df[wind_col], 'qc_wind_consistency'] = True
        
        # Test 2: Si Viento = 0, entonces Dirección = 0
        if wind_col in df.columns and direction_col in df.columns:
            wind_zero = df[wind_col].abs() < 0.01
            direction_nonzero = df[direction_col].abs() > 0.01
            df.loc[wind_zero & direction_nonzero, 'qc_wind_consistency'] = True
        
        n_inconsistent = df['qc_wind_consistency'].sum()
        if n_inconsistent > 0:
            logger.warning(f"Found {n_inconsistent} wind internal consistency violations")
        
        return df
    
    def apply_all_checks(
        self,
        df: pd.DataFrame,
        variable_name: str = 'temperatura',
        value_col: str = 'valor',
        time_col: str = 'tiempo'
    ) -> pd.DataFrame:
        """
        Apply all quality control checks.
        
        Args:
            df: DataFrame with time series data
            variable_name: Variable type
            value_col: Column name containing values
            time_col: Column name containing timestamps
            
        Returns:
            DataFrame with QC flags and 'qc_passed' column (True = good data)
            
        Example:
            >>> qc = QualityControl()
            >>> df_clean = qc.apply_all_checks(df, 'temperatura')
            >>> good_data = df_clean[df_clean['qc_passed']]
            >>> print(f"Passed QC: {len(good_data)}/{len(df_clean)}")
        """
        # Apply all checks
        df = self.detect_impossible_values(df, variable_name, value_col)
        df = self.detect_extreme_values(df, variable_name, value_col)
        df = self.detect_stuck_sensor(df, value_col)
        df = self.detect_sudden_changes(df, variable_name, value_col, time_col)
        df = self.detect_consecutive_zeros(df, value_col)
        
        # Combined flag: passed if no flags are True
        df['qc_passed'] = ~(
            df['qc_impossible'] | 
            df['qc_extreme'] | 
            df['qc_stuck'] | 
            df['qc_sudden'] | 
            df['qc_zeros']
        )
        
        # Summary
        n_total = len(df)
        n_passed = df['qc_passed'].sum()
        n_failed = n_total - n_passed
        
        logger.info(f"QC Summary: {n_passed}/{n_total} passed ({n_failed} flagged)")
        
        return df
    
    def get_qc_summary(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Get summary of QC results.
        
        Args:
            df: DataFrame with QC flags
            
        Returns:
            Dictionary with counts for each flag type
            
        Example:
            >>> qc = QualityControl()
            >>> df_clean = qc.apply_all_checks(df)
            >>> summary = qc.get_qc_summary(df_clean)
            >>> print(summary)
        """
        summary = {
            'total': len(df),
            'passed': df['qc_passed'].sum() if 'qc_passed' in df else 0,
            'impossible': df['qc_impossible'].sum() if 'qc_impossible' in df else 0,
            'extreme': df['qc_extreme'].sum() if 'qc_extreme' in df else 0,
            'stuck': df['qc_stuck'].sum() if 'qc_stuck' in df else 0,
            'sudden': df['qc_sudden'].sum() if 'qc_sudden' in df else 0,
            'zeros': df['qc_zeros'].sum() if 'qc_zeros' in df else 0,
        }
        
        return summary
    
    @staticmethod
    def _normalize_variable_name(name: str) -> str:
        """Normalize variable name for lookup."""
        name = name.lower().strip()
        
        # Common variations
        if 'temp' in name:
            return 'temperatura'
        elif 'hum' in name:
            return 'humedad'
        elif 'prec' in name or 'lluv' in name:
            return 'precipitacion'
        elif 'vient' in name:
            return 'viento'
        elif 'radia' in name:
            return 'radiacion'
        elif 'presion' in name:
            return 'presion'
        
        return name


# High-level convenience functions
def apply_quality_control(
    df: pd.DataFrame,
    variable_name: str = 'temperatura',
    value_col: str = 'valor',
    time_col: str = 'tiempo',
    return_clean_only: bool = True
) -> pd.DataFrame:
    """
    High-level function to apply quality control filters.
    
    Args:
        df: DataFrame with time series data
        variable_name: Variable type
        value_col: Column containing values
        time_col: Column containing timestamps
        return_clean_only: If True, return only data that passed QC
        
    Returns:
        DataFrame with QC flags (or only clean data)
        
    Example:
        >>> from iniamet.qc import apply_quality_control
        >>> clean_data = apply_quality_control(df, 'temperatura')
        >>> print(f"Clean records: {len(clean_data)}")
    """
    qc = QualityControl()
    df_qc = qc.apply_all_checks(df, variable_name, value_col, time_col)
    
    if return_clean_only:
        return df_qc[df_qc['qc_passed']].copy()
    else:
        return df_qc


def get_qc_report(df: pd.DataFrame) -> str:
    """
    Generate a text report of QC results.
    
    Args:
        df: DataFrame with QC flags
        
    Returns:
        Formatted text report
        
    Example:
        >>> from iniamet.qc import apply_quality_control, get_qc_report
        >>> df_qc = apply_quality_control(df, return_clean_only=False)
        >>> print(get_qc_report(df_qc))
    """
    qc = QualityControl()
    summary = qc.get_qc_summary(df)
    
    report = f"""
╔══════════════════════════════════════╗
║     QUALITY CONTROL REPORT          ║
╠══════════════════════════════════════╣
║ Total records:        {summary['total']:>7} ║
║ Passed QC:            {summary['passed']:>7} ║
║ Failed QC:            {summary['total']-summary['passed']:>7} ║
╠══════════════════════════════════════╣
║ Impossible values:    {summary['impossible']:>7} ║
║ Extreme values:       {summary['extreme']:>7} ║
║ Stuck sensor:         {summary['stuck']:>7} ║
║ Sudden changes:       {summary['sudden']:>7} ║
║ Consecutive zeros:    {summary['zeros']:>7} ║
╚══════════════════════════════════════╝
"""
    
    return report
