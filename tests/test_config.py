"""
Tests for configuration system.
"""
import pytest
import os
from unittest.mock import patch
from utils.config import BotConfig

def test_config_validation():
    """Test configuration validation."""
    with patch.dict(os.environ, {'DISCORD_TOKEN': 'test_token'}):
        config = BotConfig()
        assert config.discord_token == 'test_token'

def test_invalid_token():
    """Test invalid token handling."""
    with patch.dict(os.environ, {'DISCORD_TOKEN': ''}):
        with pytest.raises(ValueError):
            BotConfig()

def test_log_level_validation():
    """Test log level validation."""
    with patch.dict(os.environ, {'DISCORD_TOKEN': 'test', 'LOG_LEVEL': 'INVALID'}):
        with pytest.raises(ValueError):
            BotConfig()