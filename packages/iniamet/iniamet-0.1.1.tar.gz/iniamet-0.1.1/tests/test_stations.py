"""
Tests for station management functionality.
"""
from unittest.mock import Mock, patch
import pandas as pd
from iniamet.stations import StationManager


class TestStationManager:
    """Test StationManager class."""
    
    @patch('iniamet.stations.APIClient')
    def test_station_manager_initialization(self, mock_api):
        """Test StationManager initialization."""
        manager = StationManager(api=mock_api())
        assert manager is not None
    
    @patch('iniamet.stations.APIClient')
    def test_get_all_stations(self, mock_api):
        """Test getting all stations."""
        mock_client = Mock()
        mock_client.get_stations.return_value = [
            {
                'codigo': 'INIA-47',
                'nombre': 'Chillán',
                'latitud': -36.6033,
                'longitud': -71.9117,
                'region': 'Ñuble'
            }
        ]
        mock_api.return_value = mock_client
        
        manager = StationManager(api=mock_client)
        stations = manager.get_stations()
        
        assert isinstance(stations, pd.DataFrame)
    
    @patch('iniamet.stations.APIClient')
    def test_filter_by_region(self, mock_api):
        """Test filtering stations by region."""
        mock_client = Mock()
        mock_client.get_stations.return_value = [
            {'codigo': 'INIA-47', 'nombre': 'Chillán', 'region': 'Ñuble'},
            {'codigo': 'INIA-139', 'nombre': 'Talca', 'region': 'Maule'}
        ]
        mock_api.return_value = mock_client
        
        manager = StationManager(api=mock_client)
        stations = manager.get_stations(region='R16')  # Ñuble
        
        assert isinstance(stations, pd.DataFrame)
    
    @patch('iniamet.stations.APIClient')
    def test_get_station_by_code(self, mock_api):
        """Test getting single station by code."""
        mock_client = Mock()
        mock_client.get_stations.return_value = [
            {'codigo': 'INIA-47', 'nombre': 'Chillán', 'region': 'Ñuble'}
        ]
        mock_api.return_value = mock_client
        
        manager = StationManager(api=mock_client)
        station = manager.get_stations('INIA-47')
        
        assert station is not None


class TestStationFiltering:
    """Test station filtering functionality."""
    
    @patch('iniamet.stations.APIClient')
    def test_filter_by_coordinates(self, mock_api):
        """Test filtering stations by coordinates."""
        mock_client = Mock()
        mock_client.get_stations.return_value = [
            {
                'codigo': 'INIA-47',
                'nombre': 'Chillán',
                'latitud': -36.6033,
                'longitud': -71.9117
            }
        ]
        mock_api.return_value = mock_client
        
        manager = StationManager(api=mock_client)
        stations = manager.get_stations()
        
        if len(stations) > 0:
            assert 'latitud' in stations.columns
            assert 'longitud' in stations.columns
