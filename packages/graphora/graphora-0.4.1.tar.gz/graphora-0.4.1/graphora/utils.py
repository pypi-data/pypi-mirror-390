"""
Graphora Utilities

Helper functions for the Graphora client library.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Union, Optional


def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load YAML from a file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dictionary containing the parsed YAML
    """
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """
    Save data as YAML to a file.
    
    Args:
        data: Data to save
        file_path: Path to save the YAML file
    """
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def get_api_url(environment: Optional[str] = None) -> str:
    """
    Get the API URL for the specified environment.
    
    Args:
        environment: Environment to get the URL for (e.g., 'prod', 'staging')
                    If None, uses the GRAPHORA_ENVIRONMENT environment variable
                    or defaults to 'prod'
                    
    Returns:
        API URL for the specified environment
    """
    env = environment or os.environ.get("GRAPHORA_ENVIRONMENT", "prod")
    
    if env == "prod":
        return os.environ.get("GRAPHORA_API_URL", "https://api.graphora.io")
    elif env == "staging":
        return os.environ.get("GRAPHORA_STAGING_API_URL", "https://api-staging.graphora.io")
    elif env == "dev":
        return os.environ.get("GRAPHORA_DEV_API_URL", "https://api-dev.graphora.io")
    else:
        return os.environ.get("GRAPHORA_API_URL", "https://api.graphora.io")
