#!/usr/bin/env python3
"""
Script para crear un mapa HTML con todas las estaciones INIAMET disponibles.

Este script genera un mapa interactivo que muestra la ubicación de todas las
estaciones meteorológicas disponibles en la red INIA de Chile.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importar la librería
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from iniamet import INIAClient, plot_station_map
import pandas as pd

def crear_mapa_todas_estaciones(output_file="todas_estaciones.html"):
    """
    Crea un mapa HTML con todas las estaciones disponibles.

    Args:
        output_file (str): Nombre del archivo HTML de salida
    """
    print("🚀 Inicializando cliente INIAMET...")
    client = INIAClient()

    print("📡 Obteniendo todas las estaciones disponibles...")
    try:
        # Obtener todas las estaciones sin filtro
        stations = client.get_stations()
        print(f"✅ Encontradas {len(stations)} estaciones")

        if len(stations) == 0:
            print("❌ No se encontraron estaciones")
            return None

        # Mostrar resumen por región
        region_counts = stations['region'].value_counts()
        print("\n📊 Resumen por región:")
        for region, count in region_counts.items():
            print(f"   {region}: {count} estaciones")

        # Mostrar resumen por tipo
        tipo_counts = stations['tipo'].value_counts()
        print("\n🏷️ Resumen por tipo:")
        for tipo, count in tipo_counts.items():
            print(f"   {tipo}: {count} estaciones")

        print(f"\n🗺️ Creando mapa interactivo: {output_file}")

        # Crear el mapa
        mapa = plot_station_map(
            stations_df=stations,
            output_file=output_file,
            zoom_start=5,  # Zoom más amplio para ver todo Chile
            show_inline=False  # No mostrar inline en script
        )

        if mapa is not None:
            print(f"✅ Mapa creado exitosamente: {output_file}")
            print(f"   📍 Ubicación: {os.path.abspath(output_file)}")

            # Información adicional
            print("\n📋 Información del mapa:")
            print(f"   • Total de estaciones: {len(stations)}")
            print(f"   • Regiones: {len(region_counts)}")
            print(f"   • Tipos de estación: {len(tipo_counts)}")

            # Abrir el mapa automáticamente
            try:
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(output_file)}")
                print("🌐 Mapa abierto en navegador")
            except Exception as e:
                print(f"⚠️ No se pudo abrir automáticamente: {e}")

        return mapa

    except Exception as e:
        print(f"❌ Error al crear el mapa: {e}")
        return None

    except Exception as e:
        print(f"❌ Error al crear el mapa: {e}")
        return None

if __name__ == "__main__":
    # Crear directorio de salida si no existe
    output_dir = Path("outputs") / "2025-10-22" / "todas_estaciones"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Archivo de salida
    output_file = output_dir / "mapa_todas_estaciones.html"

    print("=" * 60)
    print("🗺️ GENERADOR DE MAPA - TODAS LAS ESTACIONES INIAMET")
    print("=" * 60)

    # Crear el mapa
    mapa = crear_mapa_todas_estaciones(str(output_file))

    if mapa is not None:
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"📁 Archivo generado: {output_file}")
        print("🎯 El mapa incluye:")
        print("   • Ubicación exacta de todas las estaciones")
        print("   • Información detallada al hacer clic en cada marcador")
        print("   • Vista panorámica de toda la red INIA")
        print("   • Navegación interactiva con zoom")
    else:
        print("\n❌ Error en la generación del mapa")
        sys.exit(1)