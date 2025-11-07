"""
API utilities for the per_datasets module
"""

import requests
import json
from typing import Dict, Any

# Global variable to store API configuration
_API_CONFIG: Dict[str, Any] = {
    'api_key': None,
    'base_url': 'https://perd-server.onrender.com/datasets'  # Fixed internal URL
}


def get_headers() -> Dict[str, str]:
    """
    Get the headers for API requests
    
    Returns:
        Dict containing the required headers
        
    Raises:
        RuntimeError: If the module hasn't been initialized with an API key
    """
    if _API_CONFIG['api_key'] is None:
        raise RuntimeError("per_datasets not initialized. Call pds.initialize(apiKey='your_key') first.")
    
    return {'X-API-Key': _API_CONFIG['api_key']}


def make_request() -> Dict[str, Any]:
    """
    Make an authenticated request to the API
    
    Returns:
        Dict containing the API response
    """
    try:
        headers = get_headers()
        response = requests.get(_API_CONFIG['base_url'], headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to API endpoint: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from API: {e}")


def get_api_config() -> Dict[str, Any]:
    """Get the API configuration"""
    return _API_CONFIG


def set_api_key(api_key: str) -> None:
    """Set the API key in the configuration"""
    _API_CONFIG['api_key'] = api_key