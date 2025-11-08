"""
Visualization module for INIA meteorological data.

High-level functions to create interactive maps and plots.
"""

import logging
from typing import Optional, Union, List
from datetime import datetime
import pandas as pd
import folium
from folium.plugins import HeatMap
from IPython.display import IFrame, display

logger = logging.getLogger(__name__)


def plot_temperature_map(
    stations_df: pd.DataFrame,
    temperature_data: pd.DataFrame,
    date: str,
    output_file: str = 'temp_map.html',
    marker_radius: int = 4,
    heatmap_radius: int = 50,
    heatmap_blur: int = 35,
    zoom_start: int = 10,
    show_inline: bool = True
) -> folium.Map:
    """
    Create an interactive temperature map with one line of code.
    
    Args:
        stations_df: DataFrame with station info (codigo, nombre, latitud, longitud)
        temperature_data: DataFrame with temperature data (codigo, tmax)
        date: Date string for title
        output_file: Output HTML filename
        marker_radius: Size of station markers (smaller = less visual clutter)
        heatmap_radius: Radius of heatmap influence (larger = smoother interpolation)
        heatmap_blur: Blur amount for heatmap (larger = smoother)
        zoom_start: Initial zoom level
        show_inline: Display map inline in Jupyter notebook
        
    Returns:
        Folium Map object
        
    Example:
        >>> from iniamet.visualization import plot_temperature_map
        >>> mapa = plot_temperature_map(
        ...     stations_df=nuble_stations,
        ...     temperature_data=df_temp,
        ...     date='2025-10-12'
        ... )
    """
    # Merge station info with temperature data
    df = stations_df.merge(
        temperature_data[['codigo', 'tmax']], 
        on='codigo', 
        how='inner'
    )
    
    # Ensure numeric coordinates
    df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
    df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
    df = df.dropna(subset=['latitud', 'longitud', 'tmax'])
    
    if len(df) == 0:
        logger.error("No valid data to plot")
        return None
    
    # Calculate map center
    center_lat = df['latitud'].mean()
    center_lon = df['longitud'].mean()
    
    # Create base map
    mapa = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )
    
    # Color scale function
    def get_color(temp):
        if temp < 10:
            return 'blue'
        elif temp < 15:
            return 'lightblue'
        elif temp < 20:
            return 'green'
        elif temp < 25:
            return 'orange'
        elif temp < 30:
            return 'red'
        else:
            return 'darkred'
    
    # Add markers
    for _, row in df.iterrows():
        color = get_color(row['tmax'])
        
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin: 0; color: #2c3e50;">{row['codigo']}</h4>
            <p style="margin: 3px 0;"><b>{row.get('nombre', '')}</b></p>
            <hr style="margin: 5px 0;">
            <p style="margin: 3px 0;">🌡️ <b>Tmax:</b> {row['tmax']:.1f}°C</p>
            <p style="margin: 3px 0;">📅 <b>Fecha:</b> {date}</p>
            <p style="margin: 3px 0; font-size: 10px;">
                📍 {row['latitud']:.6f}, {row['longitud']:.6f}
            </p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['latitud'], row['longitud']],
            radius=marker_radius,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(mapa)
    
    # Add heatmap (temporarily disabled due to folium bug)
    # TODO: Re-enable when folium issue is fixed
    # heat_data = [[row['latitud'], row['longitud'], row['tmax']] 
    #              for _, row in df.iterrows()]
    # HeatMap(
    #     heat_data, 
    #     radius=int(heatmap_radius), 
    #     blur=int(heatmap_blur)
    # ).add_to(mapa)
    
    # Add title
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 50px; 
                width: 350px; height: 70px; 
                background-color: white; 
                border: 2px solid grey; 
                z-index: 9999; 
                padding: 10px;
                border-radius: 5px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <h3 style="margin: 0;">🗺️ Temperaturas Máximas</h3>
        <p style="margin: 5px 0; font-size: 12px;">
            📅 {date} | 📊 {len(df)} estaciones
        </p>
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(title_html))
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; 
                width: 180px; 
                background-color: white; 
                border: 2px solid grey; 
                z-index: 9999; 
                padding: 10px;
                border-radius: 5px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 10px 0;">🌡️ Temperatura (°C)</h4>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background: blue; margin-right: 10px; border-radius: 3px;"></div>
            <span>&lt; 10°C</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background: lightblue; margin-right: 10px; border-radius: 3px;"></div>
            <span>10-15°C</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background: green; margin-right: 10px; border-radius: 3px;"></div>
            <span>15-20°C</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background: orange; margin-right: 10px; border-radius: 3px;"></div>
            <span>20-25°C</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background: red; margin-right: 10px; border-radius: 3px;"></div>
            <span>25-30°C</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 20px; height: 20px; background: darkred; margin-right: 10px; border-radius: 3px;"></div>
            <span>&gt; 30°C</span>
        </div>
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    mapa.save(output_file)
    logger.info(f"✅ Map saved to {output_file}")
    
    # Display inline if requested
    if show_inline:
        try:
            display(IFrame(output_file, width=900, height=600))
        except Exception as e:
            logger.warning(f"Could not display inline: {e}")
    
    return mapa


def plot_station_map(
    stations_df: pd.DataFrame,
    output_file: str = 'stations_map.html',
    zoom_start: int = 6,
    show_inline: bool = True
) -> folium.Map:
    """
    Create a simple map showing all station locations.
    
    Args:
        stations_df: DataFrame with station info (codigo, nombre, latitud, longitud)
        output_file: Output HTML filename
        zoom_start: Initial zoom level
        show_inline: Display map inline in Jupyter notebook
        
    Returns:
        Folium Map object
        
    Example:
        >>> from iniamet.visualization import plot_station_map
        >>> mapa = plot_station_map(nuble_stations)
    """
    # Clean data
    df = stations_df.copy()
    df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
    df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
    df = df.dropna(subset=['latitud', 'longitud'])
    
    if len(df) == 0:
        logger.error("No valid stations to plot")
        return None
    
    # Calculate center
    center_lat = df['latitud'].mean()
    center_lon = df['longitud'].mean()
    
    # Create map
    mapa = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )
    
    # Add markers
    for _, row in df.iterrows():
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin: 0;">{row['codigo']}</h4>
            <p style="margin: 3px 0;"><b>{row.get('nombre', '')}</b></p>
            <hr style="margin: 5px 0;">
            <p style="margin: 3px 0;">🏛️ {row.get('tipo', '')}</p>
            <p style="margin: 3px 0;">📍 {row.get('region', '')}</p>
            <p style="margin: 3px 0; font-size: 10px;">
                {row['latitud']:.6f}, {row['longitud']:.6f}
            </p>
        </div>
        """
        
        folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)
    
    # Save
    mapa.save(output_file)
    logger.info(f"✅ Map saved to {output_file}")
    
    # Display inline
    if show_inline:
        try:
            display(IFrame(output_file, width=900, height=600))
        except Exception as e:
            logger.warning(f"Could not display inline: {e}")
    
    return mapa


def quick_temp_map(
    client,
    region: str = 'Ñuble',
    date: str = None,
    variable: int = 2002,
    output_file: str = 'temp_map.html',
    apply_qc: bool = True,
    **map_kwargs
):
    """
    Ultra high-level: create temperature map with ONE function call.
    
    Fetches stations, downloads data, applies QC, and creates map.
    
    Args:
        client: INIAClient instance
        region: Region name (e.g., 'Ñuble')
        date: Date string (YYYY-MM-DD), defaults to today
        variable: Variable ID (2002 = temperature)
        output_file: Output HTML filename
        apply_qc: Apply quality control filters
        **map_kwargs: Additional arguments for plot_temperature_map
        
    Returns:
        Folium Map object
        
    Example:
        >>> from iniamet import INIAClient
        >>> from iniamet.visualization import quick_temp_map
        >>> client = INIAClient()
        >>> mapa = quick_temp_map(client, region='Ñuble', date='2025-10-12')
    """
    from .qc import apply_quality_control
    
    # Default date to today
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    logger.info(f"Creating temperature map for {region} on {date}")
    
    # Get stations
    stations = client.get_stations()
    region_stations = stations[stations['region'] == region].copy()
    region_stations = region_stations.dropna(subset=['latitud', 'longitud'])
    
    logger.info(f"Found {len(region_stations)} stations in {region}")
    
    # Download temperature data
    temp_data = []
    for _, station in region_stations.iterrows():
        try:
            df = client.get_data(
                station=station['codigo'],
                variable=variable,
                start_date=date,
                end_date=date
            )
            
            if df is not None and not df.empty:
                # Apply QC if requested
                if apply_qc:
                    df = apply_quality_control(df, 'temperatura')
                
                if not df.empty:
                    tmax = df['valor'].max()
                    if pd.notna(tmax):
                        temp_data.append({
                            'codigo': station['codigo'],
                            'tmax': float(tmax)
                        })
        except Exception as e:
            logger.debug(f"Error with {station['codigo']}: {e}")
    
    logger.info(f"Got temperature data for {len(temp_data)} stations")
    
    if not temp_data:
        logger.error("No temperature data available")
        return None
    
    # Create DataFrame
    df_temp = pd.DataFrame(temp_data)
    
    # Create map
    return plot_temperature_map(
        stations_df=region_stations,
        temperature_data=df_temp,
        date=date,
        output_file=output_file,
        **map_kwargs
    )
