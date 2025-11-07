"""
Initialization utilities for the per_datasets module
"""

import requests
from typing import Optional

from .config import load_stored_api_key
from .display import digital_screen
from .api import set_api_key, get_api_config, _API_CONFIG


def initialize(api_key: Optional[str] = None) -> None:
    """
    Initialize the per_datasets module with API credentials
    
    Args:
        api_key: The API key for authentication (optional if stored globally)
        
    Raises:
        ValueError: If no API key is provided and none is stored globally
    """
    # If no API key provided, try to load from global config
    if not api_key:
        api_key = load_stored_api_key()
        if not api_key:
            raise ValueError(
                "No API key provided and no global API key found. "
                "Please provide an API key or set one globally using: "
                "per-datasets set-key <your_api_key>"
            )
    
    if not api_key or not api_key.strip():
        raise ValueError("API key cannot be empty")
    
    set_api_key(api_key.strip())
    
    # Base URL is fixed and internal - not configurable by users
    
    # Check if the API key is valid by making a simple request
    try:
        headers = {'X-API-Key': api_key}
        response = requests.get(_API_CONFIG['base_url'], headers=headers, timeout=10)  # Increased timeout
        if response.status_code == 200:
            data = response.json()
            dataset_id = data.get('dataset_id', 'Unknown')
            # Display active status with dataset ID on separate lines
            status_text = f"STATUS: ACTIVE\nAPI KEY: pk...{api_key[-4:] if len(api_key) > 4 else api_key}\nDATASET ID: {dataset_id}"
            digital_screen(status_text)
        else:
            # Display inactive status with more details
            status_text = f"STATUS: INACTIVE\nAPI KEY: pk...{api_key[-4:] if len(api_key) > 4 else api_key}\nHTTP CODE: {response.status_code}"
            digital_screen(status_text)
            print(f"⚠️  Warning: API returned status {response.status_code}.")
    except requests.exceptions.Timeout:
        # Display inactive status for timeout
        status_text = f"STATUS: INACTIVE\nAPI KEY: pk...{api_key[-4:] if len(api_key) > 4 else api_key}\nREASON: TIMEOUT"
        digital_screen(status_text)
        print("⚠️  Warning: Connection timeout during initialization.")
    except requests.exceptions.ConnectionError:
        # Display inactive status for connection error
        status_text = f"STATUS: INACTIVE\nAPI KEY: pk...{api_key[-4:] if len(api_key) > 4 else api_key}\nREASON: CONNECTION ERROR"
        digital_screen(status_text)
        print("⚠️  Warning: Connection error during initialization.")
    except Exception as e:
        # Display inactive status for other errors
        status_text = f"STATUS: INACTIVE\nAPI KEY: pk...{api_key[-4:] if len(api_key) > 4 else api_key}\nREASON: {type(e).__name__}"
        digital_screen(status_text)
        print(f"⚠️  Warning: Error during initialization: {e}.")