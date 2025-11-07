"""
Configuration utilities for the per_datasets module
"""

import json
from typing import Optional, Dict, Any
from pathlib import Path


def get_config_file() -> Path:
    """Get the path to the configuration file"""
    home = Path.home()
    config_dir = home / ".per_datasets"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_stored_api_key() -> Optional[str]:
    """Load API key from global configuration"""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
        except (json.JSONDecodeError, IOError):
            return None
    return None