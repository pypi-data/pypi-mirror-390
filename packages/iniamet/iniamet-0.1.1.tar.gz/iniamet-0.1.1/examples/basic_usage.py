"""
Example: Basic usage of INIAMET library

This example demonstrates the fundamental operations:
- Initialize client
- Get stations
- Download data
- Basic analysis
"""

from iniamet import INIAClient
from datetime import datetime, timedelta

def main():
    # Initialize client
    # API key will be read from config file or environment variable
    client = INIAClient()
    
    # Get all stations
    print("📡 Fetching all stations...")
    stations = client.get_stations()
    print(f"   Found {len(stations)} stations")
    
    # Filter by region (Ñuble)
    print("\n🗺️  Filtering stations by region...")
    nuble_stations = client.get_stations(region="R16")
    print(f"   Found {len(nuble_stations)} stations in Ñuble")
    print(f"   Examples: {', '.join(nuble_stations['nombre'].head(3).tolist())}")
    
    # Get available variables for a specific station
    print("\n📊 Getting available variables for INIA-47...")
    variables = client.get_variables("INIA-47")
    print(f"   Found {len(variables)} variables")
    print("\n   Top variables:")
    print(variables[['variable_id', 'nombre', 'unidad']].head(10).to_string(index=False))
    
    # Download temperature data for last 7 days
    print("\n🌡️  Downloading temperature data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    data = client.get_data(
        station="INIA-47",
        variable=2002,  # Air temperature
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"   Downloaded {len(data)} records")
    print("\n   Sample data:")
    print(data.head(10))
    
    # Basic statistics
    print("\n📈 Temperature Statistics:")
    print(f"   Mean: {data['valor'].mean():.2f}°C")
    print(f"   Min:  {data['valor'].min():.2f}°C")
    print(f"   Max:  {data['valor'].max():.2f}°C")
    print(f"   Std:  {data['valor'].std():.2f}°C")
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    main()
