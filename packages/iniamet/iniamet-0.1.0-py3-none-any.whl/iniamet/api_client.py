"""
API Client for INIA Agromet API v2

Handles low-level HTTP requests to the INIA API with retry logic,
error handling, and response parsing.

Important: Users must configure their own API key. See README for instructions.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import os
import requests

logger = logging.getLogger(__name__)


class APIClient:
    """Low-level API client for INIA Agromet API v2."""
    
    BASE_URL = "https://agromet.inia.cl/api/v2"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize API client.
        
        Args:
            api_key: API key for INIA Agromet API. If not provided, will look for:
                     1. INIA_API_KEY environment variable
                     2. ~/.iniamet/config file
                     3. Will raise error if none found
            timeout: Request timeout in seconds
            
        Raises:
            ValueError: If no API key is provided or found
            
        Example:
            >>> # Option 1: Pass directly
            >>> client = APIClient(api_key="your-api-key-here")
            
            >>> # Option 2: Set environment variable
            >>> import os
            >>> os.environ['INIA_API_KEY'] = 'your-api-key-here'
            >>> client = APIClient()
            
            >>> # Option 3: Use config file (run: iniamet config)
            >>> client = APIClient()
        """
        # Try to get API key from multiple sources
        self.api_key = self._get_api_key(api_key)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Python/INIAMET-Library/0.1.0'
        })
    
    def _get_api_key(self, provided_key: Optional[str] = None) -> str:
        """
        Get API key from multiple sources in order of priority.
        
        Priority:
            1. Directly provided key
            2. INIA_API_KEY environment variable
            3. ~/.iniamet/config file
            
        Returns:
            API key string
            
        Raises:
            ValueError: If no API key is found
        """
        # 1. Check provided key
        if provided_key:
            return provided_key
        
        # 2. Check environment variable
        env_key = os.environ.get('INIA_API_KEY')
        if env_key:
            logger.info("Using API key from INIA_API_KEY environment variable")
            return env_key
        
        # 3. Check config file
        config_file = Path.home() / '.iniamet' / 'config'
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.startswith('api_key='):
                            key = line.split('=', 1)[1].strip()
                            if key:
                                logger.info(f"Using API key from {config_file}")
                                return key
            except Exception as e:
                logger.warning(f"Error reading config file: {e}")
        
        # No API key found
        raise ValueError(
            "\n" + "="*70 + "\n"
            "ERROR: No API key configured!\n\n"
            "To use INIAMET, you need to configure your INIA API key.\n\n"
            "You can get your API key from: https://agromet.inia.cl/api/v2/\n\n"
            "Then configure it using ONE of these methods:\n\n"
            "1. Environment variable (recommended):\n"
            "   export INIA_API_KEY='your-api-key-here'  # Linux/Mac\n"
            "   set INIA_API_KEY=your-api-key-here       # Windows CMD\n"
            "   $env:INIA_API_KEY='your-api-key-here'    # Windows PowerShell\n\n"
            "2. Config file:\n"
            "   python -m iniamet.config set-key your-api-key-here\n\n"
            "3. Pass directly in code:\n"
            "   from iniamet import INIAClient\n"
            "   client = INIAClient(api_key='your-api-key-here')\n\n"
            "For more information, see: https://github.com/inia-chile/iniamet#api-key\n"
            + "="*70
        )
    
    def _request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        retry: int = 3
    ) -> Any:
        """
        Make HTTP request to API with retry logic.
        
        Args:
            endpoint: API endpoint (e.g., 'estaciones', 'variables')
            params: Query parameters
            retry: Number of retry attempts
            
        Returns:
            Parsed JSON response
            
        Raises:
            requests.exceptions.RequestException: If request fails after retries
        """
        url = f"{self.BASE_URL}/{endpoint}/"
        
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        for attempt in range(retry):
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                # API v2 wraps responses in {'response': [...]}
                if isinstance(data, dict) and 'response' in data:
                    return data['response']
                
                return data
                
            except requests.exceptions.RequestException as e:
                if attempt < retry - 1:
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{retry}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {retry} attempts: {e}")
                    raise
        
        return None
    
    def get_stations(self) -> List[Dict[str, Any]]:
        """
        Get all stations from API.
        
        Returns:
            List of station dictionaries
        """
        logger.info("Fetching stations from API...")
        data = self._request('estaciones')
        
        if not data or not isinstance(data, list):
            logger.error("Invalid response from stations endpoint")
            return []
        
        logger.info(f"Retrieved {len(data)} stations")
        return data
    
    def get_variables(self, station: str) -> List[Dict[str, Any]]:
        """
        Get available variables for a station.
        
        Args:
            station: Station code
            
        Returns:
            List of variable dictionaries
        """
        logger.info(f"Fetching variables for station {station}...")
        params = {'estacion': station}
        data = self._request('variables', params)
        
        if not data or not isinstance(data, list):
            logger.warning(f"No variables found for station {station}")
            return []
        
        logger.info(f"Retrieved {len(data)} variables for {station}")
        return data
    
    def get_data(
        self,
        station: str,
        variable: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for a station and variable.
        
        Args:
            station: Station code
            variable: Variable ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of data point dictionaries with 'tiempo' and 'valor'
        """
        logger.info(
            f"Fetching data for {station}/{variable} "
            f"from {start_date} to {end_date}..."
        )
        
        params = {
            'estacion': station,
            'variable': str(variable),
            'desde': start_date,
            'hasta': end_date
        }
        
        data = self._request('muestras', params)
        
        if not data or not isinstance(data, list):
            logger.warning(f"No data found for {station}/{variable}")
            return []
        
        logger.info(f"Retrieved {len(data)} data points")
        return data
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
