#!/usr/bin/env python3
"""
Script automatizado para descargar datos de temperatura horaria de múltiples regiones INIAMET.

CONFIGURACIÓN:
    Modificar las variables DEFAULT_* al inicio del script para cambiar la configuración.

Uso inteligente de argumentos:
    - Sin argumentos: Usa configuración por defecto
    - Una fecha (YYYY-MM-DD): Se interpreta como fecha de inicio, usa regiones por defecto
    - Un código de región: Usa esa región con fechas por defecto
    - Región + fecha: Especifica región y fecha de inicio
    - Región + fecha_inicio + fecha_fin: Especifica todo

Ejemplos:
    python descargar_temperatura_horaria_regiones.py                    # Configuración por defecto
    python descargar_temperatura_horaria_regiones.py 2025-01-01         # Desde enero (regiones por defecto)
    python descargar_temperatura_horaria_regiones.py R16                # Solo región Ñuble
    python descargar_temperatura_horaria_regiones.py R16 2025-01-01     # Ñuble desde enero
    python descargar_temperatura_horaria_regiones.py R16 2025-01-01 2025-01-31  # Ñuble enero completo

Este script descarga datos de temperatura horaria, aplica control de calidad completo
y guarda únicamente los datos válidos en formato CSV original.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Agregar el directorio src al path para importar la librería
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from iniamet import INIAClient, RegionalDownloader
from iniamet.utils import REGION_MAP
import pandas as pd

# =============================================================================
# CONFIGURACIÓN DEL SCRIPT - MODIFICAR ESTOS VALORES SEGÚN NECESIDAD
# =============================================================================

# Regiones a procesar (códigos separados por coma)
DEFAULT_REGIONS = "R07,R08,R09,R16"

# Período de tiempo para la descarga
DEFAULT_START_DATE = "2025-01-01"  # Fecha de inicio (YYYY-MM-DD)
DEFAULT_END_DATE = "2025-10-26"    # Fecha de fin (YYYY-MM-DD)

# Tipo de datos de temperatura
USE_HOURLY_AVERAGE = True  # True: promedio horario, False: datos cada 15 minutos

# =============================================================================
# FIN DE CONFIGURACIÓN
# =============================================================================

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Descargar datos de temperatura horaria de regiones INIAMET',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python descargar_temperatura_horaria_regiones.py                    # Usa configuración por defecto
  python descargar_temperatura_horaria_regiones.py 2025-01-01         # Solo fecha inicio (regiones por defecto)
  python descargar_temperatura_horaria_regiones.py R16                # Solo región (fechas por defecto)
  python descargar_temperatura_horaria_regiones.py R16 2025-01-01     # Región + fecha inicio
  python descargar_temperatura_horaria_regiones.py R16 2025-01-01 2025-01-31  # Todos los parámetros
        """
    )

    parser.add_argument(
        'regiones',
        nargs='?',
        default=None,
        help='Códigos de regiones separados por coma (ej: R07,R08,R09) o nombre de región'
    )

    parser.add_argument(
        'fecha_inicio',
        nargs='?',
        default=None,
        help='Fecha de inicio (YYYY-MM-DD). Por defecto: 30 días atrás'
    )

    parser.add_argument(
        'fecha_fin',
        nargs='?',
        default=None,
        help='Fecha de fin (YYYY-MM-DD). Por defecto: hoy'
    )

    return parser.parse_args()

def normalize_region_codes(region_input):
    """Convert region input to list of region codes."""
    regions = []

    # Split by comma if multiple regions
    region_parts = region_input.split(',')

    for part in region_parts:
        part = part.strip()

        # Check if it's already a region code (R01, R02, etc.)
        if part.upper() in REGION_MAP:
            regions.append(part.upper())
        else:
            # Try to find region by name
            for code, name in REGION_MAP.items():
                if name.lower() == part.lower():
                    regions.append(code)
                    break
            else:
                print(f"⚠️ Región '{part}' no encontrada. Regiones disponibles:")
                for code, name in REGION_MAP.items():
                    print(f"   {code}: {name}")
                sys.exit(1)

    return regions

def generate_output_filename(regions, start_date, end_date, use_hourly_average):
    """Generate automatic filename based on regions and dates."""
    # Use region codes for filename
    if len(regions) == 1:
        region_str = regions[0]
    elif len(regions) <= 3:
        region_str = '_'.join(regions)
    else:
        region_str = '_'.join(regions)

    # Format dates
    start_str = start_date.replace('-', '')
    end_str = end_date.replace('-', '')

    # Add aggregation type to filename
    agg_type = 'horaria' if use_hourly_average else '15min'
    filename = f"temperatura_{agg_type}_{region_str}_{start_str}_a_{end_str}.csv"
    return filename

def descargar_temperatura_horaria_regiones(regions, start_date, end_date, output_file, use_hourly_average=True):
    """
    Descarga datos de temperatura horaria de múltiples regiones.

    Args:
        regions (list): Lista de códigos de regiones
        start_date (str): Fecha de inicio (YYYY-MM-DD)
        end_date (str): Fecha de fin (YYYY-MM-DD)
        output_file (str): Nombre del archivo CSV de salida
        use_hourly_average (bool): True para promedio horario, False para datos cada 15 minutos
    """
    data_type = "promedio horario" if use_hourly_average else "cada 15 minutos"
    print(f"🚀 Descarga de temperatura {data_type} - Regiones: {', '.join(regions)}")
    print(f"📅 Período: {start_date} a {end_date}")

    try:
        # Crear cliente INIAMET
        client = INIAClient()

        all_data = []
        total_stations = 0

        # Determinar tipo de agregación
        aggregation = 'h' if use_hourly_average else 'raw'

        # Procesar cada región
        for region_code in regions:
            region_name = REGION_MAP.get(region_code, region_code)
            print(f"\n📍 Procesando región {region_code}: {region_name}")

            try:
                # Crear downloader regional
                downloader = RegionalDownloader(region_code, client)
                stations = downloader.stations

                print(f"   ✅ {len(stations)} estaciones encontradas")

                if len(stations) == 0:
                    print(f"   ⚠️ No hay estaciones en {region_name}")
                    continue

                total_stations += len(stations)

                # Descargar datos de temperatura
                data_type_desc = "promedio horario" if use_hourly_average else "cada 15 minutos"
                print(f"   🌡️ Descargando datos de temperatura ({data_type_desc})...")
                data = downloader.download_climate_data(
                    start_date=start_date,
                    end_date=end_date,
                    variables=['temperature'],
                    aggregation=aggregation
                )

                if not data.empty:
                    print(f"   ✅ {len(data)} registros descargados")

                    # Aplicar control de calidad
                    print(f"   🔍 Aplicando control de calidad...")
                    from iniamet.qc import QualityControl
                    qc = QualityControl()
                    data_with_qc = qc.apply_all_checks(data, 'temperatura')

                    # Filtrar solo datos válidos
                    clean_data = data_with_qc[data_with_qc['qc_passed'] == True].copy()

                    # Mantener solo columnas originales
                    original_columns = ['tiempo', 'estacion_codigo', 'estacion_nombre', 'region',
                                      'latitud', 'longitud', 'elevacion', 'valor']
                    clean_data = clean_data[original_columns]

                    print(f"   ✅ {len(clean_data)} registros válidos después de QC")

                    all_data.append(clean_data)
                else:
                    print(f"   ⚠️ No se obtuvieron datos para {region_name}")

            except Exception as e:
                print(f"   ❌ Error procesando {region_name}: {e}")
                continue

        # Combinar todos los datos
        if not all_data:
            print("❌ No se obtuvieron datos de ninguna región")
            return None

        final_data = pd.concat(all_data, ignore_index=True)
        print(f"\n📊 Datos consolidados:")
        print(f"   • Total de registros: {len(final_data)}")
        print(f"   • Total de estaciones: {final_data['estacion_codigo'].nunique()}")
        print(f"   • Regiones procesadas: {len(regions)}")

        if 'valor' in final_data.columns:
            temp_stats = final_data['valor'].describe()
            print("\n🌡️ Estadísticas de temperatura:")
            print(f"   • Media: {temp_stats['mean']:.1f}°C")
            print(f"   • Mínima: {temp_stats['min']:.1f}°C")
            print(f"   • Máxima: {temp_stats['max']:.1f}°C")

        # Redondear valores de temperatura a 2 decimales
        if 'valor' in final_data.columns:
            final_data['valor'] = final_data['valor'].round(2)

        # Guardar como CSV
        print(f"\n💾 Guardando datos en: {output_file}")
        final_data.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Archivo CSV creado exitosamente")

        # Información adicional del archivo
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"   📏 Tamaño del archivo: {file_size:.1f} KB")

        return final_data

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Función principal del script."""

    # Parsear argumentos
    args = parse_arguments()

    # Usar configuración por defecto si no se pasan argumentos
    # Cuando no se pasan argumentos, usar valores por defecto
    if len(sys.argv) == 1:  # Solo el nombre del script
        regiones = DEFAULT_REGIONS
        fecha_inicio = DEFAULT_START_DATE
        fecha_fin = DEFAULT_END_DATE
        usar_promedio_horario = USE_HOURLY_AVERAGE
    else:
        # Lógica inteligente para detectar el tipo de argumentos
        if args.regiones and args.fecha_inicio is None and args.fecha_fin is None:
            # Solo se pasó un argumento
            if args.regiones and len(args.regiones.split('-')) == 3:
                # Parece ser una fecha (formato YYYY-MM-DD), usar como fecha de inicio
                regiones = DEFAULT_REGIONS
                fecha_inicio = args.regiones
                fecha_fin = DEFAULT_END_DATE
            else:
                # Parece ser una región
                regiones = args.regiones
                fecha_inicio = DEFAULT_START_DATE
                fecha_fin = DEFAULT_END_DATE
        elif args.regiones and args.fecha_inicio and args.fecha_fin is None:
            # Se pasaron dos argumentos: regiones y fecha_inicio
            regiones = args.regiones
            fecha_inicio = args.fecha_inicio
            fecha_fin = DEFAULT_END_DATE
        else:
            # Se pasaron todos los argumentos o usar defaults
            regiones = args.regiones if args.regiones is not None else DEFAULT_REGIONS
            fecha_inicio = args.fecha_inicio if args.fecha_inicio is not None else DEFAULT_START_DATE
            fecha_fin = args.fecha_fin if args.fecha_fin is not None else DEFAULT_END_DATE

        usar_promedio_horario = USE_HOURLY_AVERAGE

    # Normalizar códigos de regiones
    regions = normalize_region_codes(regiones)

    # Configurar fechas
    end_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    start_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()

    # Generar nombre de archivo automáticamente
    output_filename = generate_output_filename(regions, str(start_date), str(end_date), usar_promedio_horario)

    # Crear directorio de salida (relativo al directorio raíz del proyecto)
    output_dir = project_root / "outputs" / datetime.now().strftime("%Y-%m-%d") / "temperatura_horaria_regiones"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / output_filename

    print("=" * 80)
    print("🌡️ DESCARGA AUTOMATIZADA DE TEMPERATURA HORARIA")
    print("=" * 80)
    print(f"📍 Regiones: {', '.join(regions)}")
    print(f"📅 Período: {start_date} a {end_date}")
    print(f"📁 Archivo: {output_filename}")
    print("=" * 80)

    # Ejecutar descarga
    data = descargar_temperatura_horaria_regiones(
        regions=regions,
        start_date=str(start_date),
        end_date=str(end_date),
        output_file=str(output_file),
        use_hourly_average=usar_promedio_horario
    )

    if data is not None:
        print("\n" + "=" * 80)
        print("✅ DESCARGA COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print(f"📁 Archivo generado: {output_file}")
        print("🎯 El CSV incluye:")
        data_type_desc = "promedio horario" if usar_promedio_horario else "cada 15 minutos"
        print(f"   • Datos de temperatura ({data_type_desc})")
        print("   • Formato original (solo columnas esenciales)")
        print("   • Solo datos que pasaron control de calidad")
        print(f"   • {len(regions)} regiones procesadas")
        print("\n💡 Próximos pasos:")
        print("   • Abrir el CSV en Excel o software de análisis")
        print("   • Crear gráficos de series temporales")
        print("   • Realizar análisis estadísticos")
        print("   • Comparar entre regiones")
    else:
        print("\n❌ Error en la descarga de datos")
        sys.exit(1)

if __name__ == "__main__":
    main()