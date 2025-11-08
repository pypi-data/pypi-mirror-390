# INIAMET - Common Recipes

Quick copy-paste solutions for common tasks.

---

## 1. Get All Stations in a Region

```python
from iniamet import INIAClient

client = INIAClient()
stations = client.get_stations(region="R16")  # Ñuble

print(f"Found {len(stations)} stations")
print(stations[['codigo', 'nombre', 'elevacion']])
```

---

## 2. Download One Month of Temperature

```python
from iniamet import INIAClient

client = INIAClient()
data = client.get_data(
    station="INIA-47",
    variable=2002,  # Temperature
    start_date="2024-09-01",
    end_date="2024-09-30"
)

print(f"Downloaded {len(data)} records")
print(f"Mean temperature: {data['valor'].mean():.2f}°C")
```

---

## 3. Download Temperature + Precipitation for Multiple Stations

```python
from iniamet import INIAClient

client = INIAClient()
stations = ["INIA-47", "INIA-139", "INIA-211"]
variables = [2002, 2001]  # Temperature, Precipitation

data = client.bulk_download(
    stations=stations,
    variables=variables,
    start_date="2024-09-01",
    end_date="2024-09-30"
)

for key, df in data.items():
    print(f"{key}: {len(df)} records")
```

---

## 4. Regional Download with Daily Aggregation

```python
from iniamet import RegionalDownloader

downloader = RegionalDownloader(region="R16")

df = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature', 'precipitation'],
    aggregation='daily'
)

df.to_csv("regional_climate.csv", index=False)
```

---

## 5. Get All INIA Stations Nationwide

```python
from iniamet import INIAClient

client = INIAClient()
inia_stations = client.get_stations(station_type="INIA")

print(f"Total INIA stations: {len(inia_stations)}")

# Group by region
by_region = inia_stations.groupby('region').size()
print("\nINIA stations by region:")
print(by_region.sort_values(ascending=False))
```

---

## 6. Find Stations with Specific Variable

```python
from iniamet import INIAClient

client = INIAClient()
all_stations = client.get_stations()

# Check which stations have precipitation data
stations_with_precip = []

for codigo in all_stations['codigo'][:10]:  # First 10 for quick test
    if client.validate_station_variable(codigo, 2001):  # Precipitation
        stations_with_precip.append(codigo)

print(f"Stations with precipitation: {stations_with_precip}")
```

---

## 7. Download and Aggregate to Daily Temperature Stats

```python
from iniamet import INIAClient

client = INIAClient()

# Download 15-minute data
data = client.get_data(
    station="INIA-47",
    variable=2002,
    start_date="2024-09-01",
    end_date="2024-09-30"
)

# Aggregate to daily
daily = client.data_downloader.aggregate_temperature_daily(data)

print(daily[['tiempo', 'tmean', 'tmin', 'tmax']].head())
```

---

## 8. Download Data for Specific Date Range Only

```python
from iniamet import INIAClient

client = INIAClient()

# Download specific week
data = client.get_data(
    station="INIA-47",
    variable=2002,
    start_date="2024-09-15",
    end_date="2024-09-21"
)

print(f"Week data: {len(data)} records")
```

---

## 9. Export Station Metadata to CSV

```python
from iniamet import INIAClient

client = INIAClient()
stations = client.get_stations(region="R16")

# Select columns for export
metadata = stations[['codigo', 'nombre', 'region', 'latitud', 'longitud', 'elevacion']]

metadata.to_csv("station_metadata.csv", index=False)
print(f"Exported {len(metadata)} stations")
```

---

## 10. Download Multiple Variables, Merge by Time

```python
from iniamet import INIAClient
import pandas as pd

client = INIAClient()

# Download temperature
temp = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
temp = temp.rename(columns={'valor': 'temperature'})

# Download precipitation
precip = client.get_data("INIA-47", 2001, "2024-09-01", "2024-09-30")
precip = precip.rename(columns={'valor': 'precipitation'})

# Merge
combined = pd.merge(temp, precip, on='tiempo', how='outer')

print(combined.head())
```

---

## 11. Download for All Regions (Loop)

```python
from iniamet import RegionalDownloader

regions = ["R07", "R08", "R16"]  # Maule, Biobío, Ñuble

for region in regions:
    print(f"Downloading {region}...")
    
    downloader = RegionalDownloader(region=region)
    df = downloader.download_climate_data(
        start_date="2024-09-01",
        end_date="2024-09-30",
        variables=['temperature', 'precipitation'],
        aggregation='daily'
    )
    
    filename = f"climate_{region.lower()}_sept2024.csv"
    df.to_csv(filename, index=False)
    print(f"  ✓ Saved {filename} ({len(df)} records)\n")
```

---

## 12. Check Variable Names for a Station

```python
from iniamet import INIAClient

client = INIAClient()
variables = client.get_variables("INIA-47")

print("Available variables:")
for _, var in variables.iterrows():
    print(f"  ID: {var['variable_id']:4} | {var['nombre']:40} | {var['unidad']}")
```

---

## 13. Download Data Without Caching

```python
from iniamet import INIAClient

# Disable cache for fresh data
client = INIAClient(cache=False)

data = client.get_data(
    station="INIA-47",
    variable=2002,
    start_date="2024-09-01",
    end_date="2024-09-30"
)

print(f"Fresh data: {len(data)} records")
```

---

## 14. Get Highest/Lowest Elevation Stations

```python
from iniamet import INIAClient

client = INIAClient()
stations = client.get_stations()

# Remove NaN elevations
stations = stations.dropna(subset=['elevacion'])

# Highest
highest = stations.nlargest(5, 'elevacion')
print("Highest elevation stations:")
print(highest[['codigo', 'nombre', 'elevacion', 'region']])

# Lowest
lowest = stations.nsmallest(5, 'elevacion')
print("\nLowest elevation stations:")
print(lowest[['codigo', 'nombre', 'elevacion', 'region']])
```

---

## 15. Download Last 7 Days of Data

```python
from iniamet import INIAClient
from datetime import datetime, timedelta

client = INIAClient()

# Calculate dates
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

data = client.get_data(
    station="INIA-47",
    variable=2002,
    start_date=start_date,
    end_date=end_date
)

print(f"Last 7 days: {len(data)} records")
```

---

## 16. Create Summary Statistics by Station

```python
from iniamet import RegionalDownloader

downloader = RegionalDownloader(region="R16")

df = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature', 'precipitation'],
    aggregation='daily'
)

# Compute statistics
summary = df.groupby(['estacion_codigo', 'estacion_nombre']).agg({
    'tmin': ['min', 'mean'],
    'tmax': ['max', 'mean'],
    'pp_acum': 'sum',
    'latitud': 'first',
    'longitud': 'first',
    'elevacion': 'first'
}).round(2)

print(summary)
```

---

## 17. Filter Stations by Elevation Range

```python
from iniamet import INIAClient

client = INIAClient()
stations = client.get_stations(region="R16")

# Stations between 100-500m elevation
mid_elevation = stations[
    (stations['elevacion'] >= 100) & 
    (stations['elevacion'] <= 500)
]

print(f"Stations 100-500m: {len(mid_elevation)}")
print(mid_elevation[['codigo', 'nombre', 'elevacion']])
```

---

## 18. Download with Progress Logging

```python
from iniamet import INIAClient
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

client = INIAClient()

data = client.bulk_download(
    stations=["INIA-47", "INIA-139", "INIA-211"],
    variables=[2002, 2001],
    start_date="2024-09-01",
    end_date="2024-09-30",
    delay=1.0
)

print(f"Downloaded {len(data)} station-variable combinations")
```

---

## 19. Create Spatial Coverage Map Data

```python
from iniamet import INIAClient

client = INIAClient()
stations = client.get_stations()

# Extract coordinates
coords = stations[['codigo', 'nombre', 'region', 'latitud', 'longitud']].copy()
coords = coords.dropna(subset=['latitud', 'longitud'])

# Export for mapping
coords.to_csv("station_coordinates.csv", index=False)

print(f"Exported {len(coords)} station coordinates")
print(f"Lat range: {coords['latitud'].min():.2f} to {coords['latitud'].max():.2f}")
print(f"Lon range: {coords['longitud'].min():.2f} to {coords['longitud'].max():.2f}")
```

---

## 20. Download and Compare Two Time Periods

```python
from iniamet import INIAClient

client = INIAClient()

# Period 1: September 2023
data_2023 = client.get_data("INIA-47", 2002, "2023-09-01", "2023-09-30")

# Period 2: September 2024
data_2024 = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")

print(f"2023: Mean = {data_2023['valor'].mean():.2f}°C")
print(f"2024: Mean = {data_2024['valor'].mean():.2f}°C")
print(f"Difference: {data_2024['valor'].mean() - data_2023['valor'].mean():.2f}°C")
```

---

## Need Help?

- Check `examples/` directory for complete workflows
- Read `docs/QUICK_REFERENCE.md` for detailed documentation
- Enable logging with `logging.basicConfig(level=logging.DEBUG)`
- Use `client.get_variables(station)` to find available variables

---

**Pro Tips:**

1. Always enable caching for repeated queries: `client = INIAClient(cache=True)`
2. Use `bulk_download()` instead of loops for multiple stations
3. Set `delay` parameter in bulk downloads to avoid rate limiting
4. Check station availability with `validate_station_variable()` before downloading
5. Use daily aggregation when sub-daily data not needed to reduce file sizes
