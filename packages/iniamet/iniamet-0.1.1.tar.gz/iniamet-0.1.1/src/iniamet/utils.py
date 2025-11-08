"""
Utility functions for the INIAMET library.
"""

from datetime import datetime, date
from typing import Union, Optional


# Region code mapping
REGION_MAP = {
    "R01": "Tarapacá",
    "R02": "Antofagasta",
    "R03": "Atacama",
    "R04": "Coquimbo",
    "R05": "Valparaíso",
    "R06": "O'Higgins",
    "R07": "Maule",
    "R08": "Biobío",
    "R09": "La Araucanía",
    "R10": "Los Lagos",
    "R11": "Aysén",
    "R12": "Magallanes",
    "R13": "Metropolitana",
    "R14": "Los Ríos",
    "R15": "Arica y Parinacota",
    "R16": "Ñuble"
}

# Variable metadata mapping
VARIABLE_INFO = {
    2001: {
        'nombre': 'Humedad Relativa',
        'unidad': '%',
        'color': 'blue',
        'descripcion': 'Humedad relativa del aire'
    },
    2002: {
        'nombre': 'Temperatura',
        'unidad': '°C',
        'color': 'red',
        'descripcion': 'Temperatura del aire'
    },
    2003: {
        'nombre': 'Precipitación',
        'unidad': 'mm',
        'color': 'green',
        'descripcion': 'Precipitación acumulada'
    },
    2004: {
        'nombre': 'Radiación Solar',
        'unidad': 'W/m²',
        'color': 'orange',
        'descripcion': 'Radiación solar global'
    },
    2005: {
        'nombre': 'Velocidad Viento',
        'unidad': 'm/s',
        'color': 'purple',
        'descripcion': 'Velocidad del viento'
    },
    2006: {
        'nombre': 'Dirección Viento',
        'unidad': '°',
        'color': 'cyan',
        'descripcion': 'Dirección del viento'
    },
    2007: {
        'nombre': 'Presión Atmosférica',
        'unidad': 'hPa',
        'color': 'brown',
        'descripcion': 'Presión atmosférica'
    },
    2008: {
        'nombre': 'Temperatura Mínima',
        'unidad': '°C',
        'color': 'Blues',
        'descripcion': 'Temperatura mínima del aire'
    },
    2009: {
        'nombre': 'Temperatura Máxima',
        'unidad': '°C',
        'color': 'Reds',
        'descripcion': 'Temperatura máxima del aire'
    }
}


def get_variable_info(variable_id: int) -> dict:
    """
    Get metadata for a variable ID.
    
    Args:
        variable_id: Variable ID from INIA API
        
    Returns:
        Dictionary with variable metadata (nombre, unidad, color, descripcion)
        
    Example:
        >>> info = get_variable_info(2002)
        >>> print(info['nombre'])
        'Temperatura'
    """
    if variable_id not in VARIABLE_INFO:
        return {
            'nombre': f'Variable {variable_id}',
            'unidad': '',
            'color': 'gray',
            'descripcion': f'Variable desconocida (ID: {variable_id})'
        }
    return VARIABLE_INFO[variable_id]


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison (lowercase + remove accents).
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
        
    Example:
        >>> normalize_text("Precipitación")
        'precipitacion'
    """
    text = text.lower()
    
    # Remove Spanish accents
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def parse_date(date: Union[str, datetime, date]) -> datetime:
    """
    Parse date from string, datetime, or date.
    
    Args:
        date: Date as string (YYYY-MM-DD), datetime object, or date object
        
    Returns:
        datetime object
        
    Raises:
        ValueError: If date format is invalid
    """
    # Handle different input types
    if isinstance(date, str):
        try:
            return datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError(
                f"Invalid date format: {date}. Expected YYYY-MM-DD"
            )
    elif isinstance(date, datetime):
        return date
    elif isinstance(date, date):
        return datetime.combine(date, datetime.min.time())
    else:
        raise TypeError(f"Expected str, datetime, or date, got {type(date)}")


def format_station_code(code: str) -> str:
    """
    Normalize station code format.
    
    Args:
        code: Station code
        
    Returns:
        Normalized code (uppercase)
    """
    return code.strip().upper()


def get_region_name(code: str) -> str:
    """
    Get region name from code or name.

    Args:
        code: Region code (e.g., "R16") or region name (e.g., "Ñuble")

    Returns:
        Region name (e.g., "Ñuble")

    Raises:
        ValueError: If code/name is invalid
    """
    code = code.upper().strip()

    # If it's already a region code (starts with R), return the name
    if code in REGION_MAP:
        return REGION_MAP[code]

    # If it's a region name, find the corresponding code
    for region_code, region_name in REGION_MAP.items():
        if region_name.upper() == code:
            return region_name

    # Try to find partial matches (e.g., "COQUIMBO" should match "Coquimbo")
    for region_code, region_name in REGION_MAP.items():
        if code in region_name.upper() or region_name.upper() in code:
            return region_name

    # If not found, return the input as-is (graceful degradation)
    return code.title()


def get_region_code(name: str) -> Optional[str]:
    """
    Get region code from name.
    
    Args:
        name: Region name (e.g., "Ñuble") or code (e.g., "R16")
        
    Returns:
        Region code (e.g., "R16") or None if invalid
    """
    # If already a code, return it
    if name.upper() in REGION_MAP:
        return name.upper()
    
    name_normalized = normalize_text(name)
    
    for code, region_name in REGION_MAP.items():
        if normalize_text(region_name) == name_normalized:
            return code
    
    return None
