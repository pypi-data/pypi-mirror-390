"""
load function for the reservoir module
"""

import json
import requests
import pandas as pd
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

from ..talkaholic.reservoir import Reservoir
from ..utils.config import load_stored_api_key
from ..utils.display import digital_screen
from ..utils.api import get_api_config, get_headers, make_request


def load(reservoir_id: str) -> pd.DataFrame:
    """
    ## load(reservoir id)
    
    Loads a specific reservoir model by ID from the reservoir datasets in the database.
    
    Args:
        reservoir_id (str): The ID of the reservoir to load
        
    ### **returns**
    
    [`pandas.DataFrame`]
        A DataFrame containing all rows of the reservoir dataset
        
    Raises:
        RuntimeError: If the module hasn't been initialized
        ValueError: If the reservoir ID is invalid or not found
    """
    try:
        headers = get_headers()
        _API_CONFIG = get_api_config()
        url = f"{_API_CONFIG['base_url']}/{reservoir_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        api_data = response.json()
        
        # Handle the actual API response structure
        if 'data' in api_data and 'columns' in api_data:
            data = api_data['data']
            columns = api_data['columns']
            returned_reservoir_id = api_data.get('dataset_id', reservoir_id)
            
            if len(data) == 0:
                raise ValueError("API returned reservoir with no data")
            
            # Convert all rows to a DataFrame
            df = pd.DataFrame(data)
            
            # Return the DataFrame with all rows
            return df
        else:
            raise ValueError("API response does not contain 'data' and 'columns' fields")
        
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to API endpoint: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response from API: {e}")
    except Exception as e:
        if "not initialized" in str(e):
            raise e
        raise RuntimeError(f"Error loading reservoir {reservoir_id}: {e}")