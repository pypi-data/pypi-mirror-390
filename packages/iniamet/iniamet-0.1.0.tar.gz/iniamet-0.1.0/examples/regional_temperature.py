"""
Example: Regional temperature download

Download hourly temperature data for a specific region.
Demonstrates regional data download with quality control.
"""

from iniamet import INIAClient, RegionalDownloader, apply_quality_control
from datetime import datetime, timedelta


def main():
    """Download regional temperature data."""
    
    # Configuration
    region = "R16"  # Nuble region
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # Last 7 days
    
    print(f"Regional Temperature Download Example")
    print(f"   Region: {region} (Nuble)")
    print(f"   Period: {start_date.date()} to {end_date.date()}")
    print()
    
    # Initialize client
    print("Initializing INIA client...")
    client = INIAClient()
    
    # Get stations in the region
    print(f"\nGetting stations in region {region}...")
    stations = client.get_stations(region=region)
    print(f"   Found {len(stations)} stations")
    
    if len(stations) == 0:
        print("No stations found in this region")
        return
    
    # Show station list
    print("\nAvailable stations:")
    for idx, row in stations.head(5).iterrows():
        print(f"   * {row['codigo']}: {row['nombre']}")
    if len(stations) > 5:
        print(f"   ... and {len(stations) - 5} more")
    
    # Download temperature data for the region
    print("\nDownloading temperature data...")
    print("   (This may take a few minutes)")
    
    downloader = RegionalDownloader(region=region)
    
    try:
        data = downloader.download_climate_data(
            start_date=start_date,
            end_date=end_date,
            variables=['temperature'],
            aggregation='hourly'
        )
        
        if data.empty:
            print("No temperature data obtained")
            return
        
        print(f"Data downloaded: {len(data)} records")
        
        # Apply quality control
        print("\nApplying quality control...")
        clean_data = apply_quality_control(data, 'temperatura')
        
        removed = len(data) - len(clean_data)
        print(f"   Original records: {len(data)}")
        print(f"   Clean records: {len(clean_data)}")
        print(f"   Removed: {removed}")
        
        # Calculate statistics
        print("\nRegional Temperature Statistics:")
        stats = clean_data.groupby('station')['valor'].agg([
            ('mean', 'mean'),
            ('min', 'min'),
            ('max', 'max'),
            ('count', 'count')
        ]).round(2)
        
        print(stats.head(10))
        
        # Overall statistics
        print(f"\nOverall Region Statistics:")
        print(f"   Mean temperature: {clean_data['valor'].mean():.2f} C")
        print(f"   Min temperature: {clean_data['valor'].min():.2f} C")
        print(f"   Max temperature: {clean_data['valor'].max():.2f} C")
        
        # Save to file
        output_file = f"regional_temp_{region}.csv"
        clean_data.to_csv(output_file, index=False)
        print(f"\nData saved to: {output_file}")
        
        print("\nExample completed successfully!")
        
    except Exception as e:
        print(f"\nError downloading data: {e}")


if __name__ == "__main__":
    main()
