# INIAMET - Chilean INIA Agrometeorological Data Library

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/iniamet.svg)](https://pypi.org/project/iniamet/)
[![Documentation Status](https://readthedocs.org/projects/iniamet/badge/?version=latest)](https://iniamet.readthedocs.io/en/latest/?badge=latest)

**High-level Python library for accessing Chilean INIA (Instituto de Investigaciones Agropecuarias) agrometeorological station data.**

> ⚠️ **DISCLAIMER**: This is an **unofficial, community-developed library**. It is **NOT officially affiliated with, endorsed by, or maintained by INIA** (Instituto de Investigaciones Agropecuarias). This library accesses publicly available data from INIA's agrometeorological API.

Access data from 400+ weather stations across Chile with a simple, intuitive API. Download temperature, precipitation, humidity, wind, radiation data and more.

## 🌟 Features

- **High-Level API**: Simple, intuitive functions to query stations and download data
- **Smart Station Management**: Automatically handles different station code formats
- **Regional Filtering**: Filter stations by Chilean regions (R01-R16)
- **Data Caching**: Built-in caching system for faster repeated queries
- **Type Safety**: Full type hints for better IDE support
- **pandas Integration**: Returns data as pandas DataFrames
- **Comprehensive Variables**: Temperature, precipitation, humidity, wind, radiation, and more

## 📦 Installation

```bash
pip install iniamet
```

Or install from source:

```bash
git clone https://github.com/reneignacio/iniamet-library
cd iniamet-library
pip install -e .
```

## 🎨 Optional: Visualization Features

If you want to use the visualization features (interactive maps), install with visualization support:

```bash
pip install iniamet[viz]
# or install all optional features:
pip install iniamet[all]
```

## 🔑 API Key Configuration

**IMPORTANT:** You need an API key to use INIAMET. Get yours from [https://agromet.inia.cl/api/v2/](https://agromet.inia.cl/api/v2/)

### Option 1: Configuration File (Recommended - Easy Setup)

```bash
# Configure your API key once
python -m iniamet.config set-key YOUR-API-KEY-HERE

# Verify it's saved
python -m iniamet.config show
```

### Option 2: Environment Variable

**Linux/Mac:**
```bash
export INIA_API_KEY='your-api-key-here'
# Add to ~/.bashrc or ~/.zshrc for persistence
```

**Windows CMD:**
```cmd
set INIA_API_KEY=your-api-key-here
# For persistence: setx INIA_API_KEY "your-api-key-here"
```

**Windows PowerShell:**
```powershell
$env:INIA_API_KEY='your-api-key-here'
# For persistence: [Environment]::SetEnvironmentVariable('INIA_API_KEY', 'your-key', 'User')
```

### Option 3: Pass Directly in Code

```python
from iniamet import INIAClient
client = INIAClient(api_key='your-api-key-here')
```

## 🚀 Quick Start

```python
from iniamet import INIAClient

# Initialize client
client = INIAClient()

# Get all stations
stations = client.get_stations()
print(f"Total stations: {len(stations)}")

# Filter by region (Ñuble)
nuble_stations = client.get_stations(region="R16")
print(f"Ñuble stations: {len(nuble_stations)}")

# Get available variables for a station
variables = client.get_variables("INIA-47")
print(variables[['variable_id', 'nombre', 'unidad']])

# Download data
from datetime import datetime

data = client.get_data(
    station="INIA-47",
    variable=2002,  # Temperatura del aire
    start_date=datetime(2024, 9, 1),
    end_date=datetime(2024, 9, 30)
)

print(data.head())
```

## 📊 Regional Download Example

```python
from iniamet import RegionalDownloader

# Download all temperature and precipitation data for Ñuble region
downloader = RegionalDownloader(region="R16")

result = downloader.download_climate_data(
    start_date="2024-09-01",
    end_date="2024-09-30",
    variables=['temperature', 'precipitation'],
    aggregation='daily'
)

# Save to CSV
result.to_csv("nuble_climate_sept2024.csv")
```

## 🗺️ Region Codes

| Code | Region |
|------|--------|
| R01  | Tarapacá |
| R02  | Antofagasta |
| R03  | Atacama |
| R04  | Coquimbo |
| R05  | Valparaíso |
| R06  | O'Higgins |
| R07  | Maule |
| R08  | Biobío |
| R09  | La Araucanía |
| R10  | Los Lagos |
| R11  | Aysén |
| R12  | Magallanes |
| R13  | Metropolitana |
| R14  | Los Ríos |
| R15  | Arica y Parinacota |
| R16  | Ñuble |

## 📚 Documentation

Full documentation available at: [https://iniamet.readthedocs.io](https://iniamet.readthedocs.io)

### Station Types

The library handles 10 different station network types:
- INIA stations
- DMC (Dirección Meteorológica de Chile)
- ARAUCO stations
- AGRICHILE network
- And more...

### Available Variables

- Temperature (air, soil, surface)
- Precipitation
- Humidity (relative, absolute)
- Wind (speed, direction)
- Solar radiation
- Atmospheric pressure
- And many more...

## 🔧 Advanced Usage

### Caching

```python
# Enable caching (default)
client = INIAClient(cache=True, cache_dir="./cache")

# Disable caching
client = INIAClient(cache=False)
```

### Batch Downloads

```python
# Download multiple variables from multiple stations
stations = ["INIA-47", "INIA-139", "INIA-211"]
variables = [2002, 2001]  # Temperature, Precipitation

data = client.bulk_download(
    stations=stations,
    variables=variables,
    start_date="2024-09-01",
    end_date="2024-09-30"
)
```

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/inia/iniamet
cd iniamet-library

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=iniamet --cov-report=html

# Format code
black src/

# Type check
mypy src/
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 📚 Documentation

Full documentation available at: **[iniamet.readthedocs.io](https://iniamet.readthedocs.io/)**

- [Installation Guide](https://iniamet.readthedocs.io/en/latest/installation.html)
- [Quick Start Tutorial](https://iniamet.readthedocs.io/en/latest/quickstart.html)
- [API Reference](https://iniamet.readthedocs.io/en/latest/api/client.html)
- [Examples](https://iniamet.readthedocs.io/en/latest/examples.html)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- **PyPI Package**: [https://pypi.org/project/iniamet/](https://pypi.org/project/iniamet/)
- **API Documentation**: [INIA Agromet API v2](https://agromet.inia.cl/api/v2)
- **INIA Official Site**: [https://www.inia.cl](https://www.inia.cl)
- **Issue Tracker**: [GitHub Issues](https://github.com/reneignacio/iniamet-library/issues)

## 📧 Contact

For questions and support, please open an issue on GitHub.

## ⚖️ Legal Disclaimer

**This is an UNOFFICIAL library**. This project is:
- NOT affiliated with INIA (Instituto de Investigaciones Agropecuarias)
- NOT endorsed or maintained by INIA
- An independent, community-developed tool
- Accessing publicly available data from INIA's API

All data accessed through this library belongs to INIA. Please refer to INIA's terms of service for data usage policies.

---

Made with ❤️ by the community for the research community.
