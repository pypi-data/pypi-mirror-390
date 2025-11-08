"""
Tests for API client functionality.
"""
from unittest.mock import Mock, patch
from iniamet.api_client import APIClient


class TestAPIClient:
    """Test cases for APIClient class."""
    
    def test_api_client_initialization(self):
        """Test that APIClient initializes correctly."""
        # Ensure we have an API key in the environment
        client = APIClient()
        assert client.api_key is not None
        assert client.timeout == 30
        assert client.session is not None
    
    def test_api_client_with_custom_key(self):
        """Test APIClient with custom API key."""
        custom_key = "test_key_123"
        client = APIClient(api_key=custom_key)
        assert client.api_key == custom_key
    
    def test_api_client_with_custom_timeout(self):
        """Test APIClient with custom timeout."""
        client = APIClient(timeout=60)
        assert client.timeout == 60
    
    @patch('iniamet.api_client.requests.Session.get')
    def test_request_success(self, mock_get):
        """Test successful API request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response
        
        client = APIClient()
        result = client._request("estaciones")
        
        assert result == {"data": "test"}
        mock_get.assert_called_once()
    
    @patch('iniamet.api_client.requests.Session.get')
    def test_request_retry_on_failure(self, mock_get):
        """Test that request retries on failure."""
        import requests
        # Setup mock to fail then succeed
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError("Server error")
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json = Mock(return_value={"data": "test"})
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        client = APIClient()
        result = client._request("estaciones", retry=2)
        
        assert result == {"data": "test"}
        assert mock_get.call_count == 2


class TestAPIEndpoints:
    """Test API endpoint methods."""
    
    @patch('iniamet.api_client.APIClient._request')
    def test_get_stations(self, mock_request):
        """Test get_stations method."""
        mock_request.return_value = [
            {"codigo": "INIA-47", "nombre": "Chillán"}
        ]
        
        client = APIClient()
        result = client.get_stations()
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_request.assert_called_once_with("estaciones")
    
    @patch('iniamet.api_client.APIClient._request')
    def test_get_variables(self, mock_request):
        """Test get_variables method."""
        mock_request.return_value = {
            "variables": [
                {"id": 2002, "nombre": "Temperatura"}
            ]
        }
        
        client = APIClient()
        result = client.get_variables("INIA-47")
        
        assert isinstance(result, list)
        mock_request.assert_called_once()
    
    @patch('iniamet.api_client.APIClient._request')
    def test_get_data(self, mock_request):
        """Test get_data method."""
        mock_request.return_value = {
            "datos": [
                {"tiempo": "2024-09-01", "valor": 15.5}
            ]
        }
        
        client = APIClient()
        result = client.get_data("INIA-47", 2002, "2024-09-01", "2024-09-30")
        
        assert isinstance(result, list)
        mock_request.assert_called_once()
