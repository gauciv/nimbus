"""
Configuration utilities for the Nimbus Discord bot.

This module handles loading and validating configuration from config.json,
as well as providing utilities for loading and saving JSON data.
"""
import json
import os
import sys
from typing import Dict, Any, Optional

# Constants
CONFIG_FILE = 'config.json'

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.json file.
    
    Returns:
        Dict containing configuration values
    
    Raises:
        SystemExit: If config file is missing, invalid, or contains errors
    """
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            
            # Validate required fields
            if 'token' not in config:
                print("❌ Bot token not found in config.json")
                sys.exit(1)
            if not isinstance(config['token'], str) or not config['token'].strip():
                print("❌ Bot token is empty or invalid")
                sys.exit(1)
                
            # Mask token in logs for security - only show that it was loaded
            print(f"✓ Configuration loaded (Token: ***masked***)")
                
            return config
    except FileNotFoundError:
        print(f"❌ {CONFIG_FILE} not found! Please create a config.json file with your bot token.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ {CONFIG_FILE} is not a valid JSON file!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error loading config: {str(e)}")
        sys.exit(1)

def load_json_data(filename: str, default: Any = None) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        filename: Name of the JSON file to load
        default: Default value to return if file doesn't exist or has errors
        
    Returns:
        Loaded data or default value if loading fails
    """
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return default
    except Exception:
        return default

def save_json_data(filename: str, data: Any) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        filename: Name of the JSON file to save to
        data: Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False