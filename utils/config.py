"""
Modern configuration system for Nimbus Discord Bot.

Uses Pydantic for validation and environment variables for security.
"""
import os
import json
from typing import Optional, Any
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BotConfig(BaseSettings):
    """Main bot configuration with validation."""
    
    # Discord Configuration
    discord_token: str = Field(..., env='DISCORD_TOKEN')
    guild_id: Optional[int] = Field(None, env='GUILD_ID')
    
    # Environment
    log_level: str = Field('INFO', env='LOG_LEVEL')
    
    # AI Configuration
    huggingface_api_key: Optional[str] = Field(None, env='HUGGINGFACE_API_KEY')
    groq_api_key: Optional[str] = Field(None, env='GROQ_API_KEY')
    
    @validator('discord_token')
    def validate_token(cls, v):
        if not v or not v.strip():
            raise ValueError('Discord token cannot be empty')
        return v.strip()
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = '.env'
        case_sensitive = False

# Global config instance
config = BotConfig()

def load_config() -> dict:
    """Legacy compatibility function."""
    return {'token': config.discord_token, 'guild_id': config.guild_id}

def load_json_data(filename: str, default: Any = None) -> Any:
    """Load data from a JSON file."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return default
    except Exception:
        return default

def save_json_data(filename: str, data: Any) -> bool:
    """Save data to a JSON file."""
    try:
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False