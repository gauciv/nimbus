"""
Configuration utilities for the Nimbus Discord bot.
Handles loading and validating configuration from config.json.
"""
import json
import logging
import os
import sys
import traceback
from typing import Dict, Any

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
            logging.info("Successfully loaded config.json")
            
            # Validate required fields
            if 'token' not in config:
                raise KeyError("Bot token not found in config.json")
            if not isinstance(config['token'], str) or not config['token'].strip():
                raise ValueError("Bot token is empty or invalid")
                
            return config
    except FileNotFoundError:
        logging.critical(f"{CONFIG_FILE} not found! Please create a config.json file with your bot token.")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.critical(f"{CONFIG_FILE} is not a valid JSON file!")
        sys.exit(1)
    except (KeyError, ValueError) as e:
        logging.critical(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Unexpected error loading config: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

def load_json_data(filename: str, default=None):
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
    except Exception as e:
        logging.error(f"Error loading {filename}: {e}")
        return default

def save_json_data(filename: str, data):
    """
    Save data to a JSON file.
    
    Args:
        filename: Name of the JSON file to save to
        data: Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving {filename}: {e}")
        return False