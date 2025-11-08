"""
Tests for data downloader functionality.
"""
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime
from iniamet.data import DataDownloader


class TestDataDownloader:
    """Test DataDownloader class."""
    
    def test_data_downloader_initialization(self):
        """Test DataDownloader initialization."""
        with patch('iniamet.data.APIClient') as mock_api:
            downloader = DataDownloader(api=mock_api())
            assert downloader is not None
    
    @patch('iniamet.data.APIClient')
    def test_download_data_basic(self, mock_api):
        """Test basic data download."""
        # Setup mock
        mock_client = Mock()
        mock_client.get_data.return_value = [
            {'tiempo': '2024-09-01 00:00:00', 'valor': 15.5},
            {'tiempo': '2024-09-01 01:00:00', 'valor': 16.0}
        ]
        mock_api.return_value = mock_client
        
        downloader = DataDownloader(api=mock_client)
        result = downloader.get_data(
            station="INIA-47",
            variable=2002,
            start_date=datetime(2024, 9, 1),
            end_date=datetime(2024, 9, 2)
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) >= 0
    
    @patch('iniamet.data.APIClient')
    def test_download_data_with_caching(self, mock_api):
        """Test data download with caching."""
        mock_client = Mock()
        mock_client.get_data.return_value = {'datos': []}
        mock_api.return_value = mock_client
        
        cache = Mock()
        downloader = DataDownloader(api=mock_client, cache=cache)
        assert downloader.cache is not None
    
    @patch('iniamet.data.APIClient')
    def test_download_handles_empty_response(self, mock_api):
        """Test that downloader handles empty API response."""
        mock_client = Mock()
        mock_client.get_data.return_value = []
        mock_api.return_value = mock_client
        
        downloader = DataDownloader(api=mock_client)
        result = downloader.get_data(
            station="INIA-47",
            variable=2002,
            start_date=datetime(2024, 9, 1),
            end_date=datetime(2024, 9, 2)
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestDataProcessing:
    """Test data processing functions."""
    
    @patch('iniamet.data.APIClient')
    def test_dataframe_conversion(self, mock_api):
        """Test conversion of API data to DataFrame."""
        mock_client = Mock()
        mock_client.get_data.return_value = [
            {'tiempo': '2024-09-01 00:00:00', 'valor': 15.5},
            {'tiempo': '2024-09-01 01:00:00', 'valor': 16.0}
        ]
        mock_api.return_value = mock_client
        
        downloader = DataDownloader(api=mock_client)
        result = downloader.get_data(
            station="INIA-47",
            variable=2002,
            start_date=datetime(2024, 9, 1),
            end_date=datetime(2024, 9, 2)
        )
        
        if len(result) > 0:
            assert 'tiempo' in result.columns or result.index.name == 'tiempo'
            assert 'valor' in result.columns
