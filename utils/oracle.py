"""
Oracle utilities for the Nimbus Discord bot.

This module provides mystical error messages, warnings, and logging utilities
to maintain the mystical theme throughout the bot's interactions.
"""
import logging
import traceback
from enum import Enum
from typing import Optional

# Configure a custom logger for Oracle's visions
oracle_logger = logging.getLogger('oracle')
oracle_logger.setLevel(logging.DEBUG)

# Add a file handler if it doesn't exist
if not oracle_logger.handlers:
    file_handler = logging.FileHandler('data/oracle_visions.log')
    file_handler.setFormatter(logging.Formatter(
        '✨ [%(asctime)s] %(levelname)s: %(message)s',
        '%Y-%m-%d %H:%M:%S'
    ))
    oracle_logger.addHandler(file_handler)

class OracleVision(Enum):
    """Levels of Oracle's visions (log levels)."""
    WHISPER = logging.DEBUG      # Debug messages
    MURMUR = logging.INFO        # Info messages
    PORTENT = logging.WARNING    # Warning messages
    OMEN = logging.ERROR         # Error messages
    PROPHECY = logging.CRITICAL  # Critical messages

# Mystical error messages
ERROR_MESSAGES = {
    # General errors
    "general": "🌑 The cosmic forces are disturbed. The Oracle cannot complete this ritual.",
    "permission": "🌑 You lack the mystical authority to perform this ritual.",
    "not_found": "🌑 The Oracle cannot locate what you seek in the cosmic tapestry.",
    "timeout": "🌑 The stars have shifted while awaiting a response. The ritual has failed.",
    "rate_limit": "🌑 The cosmic energies are depleted. Please wait before attempting this ritual again.",
    
    # Command errors
    "command_not_found": "🌑 This incantation is unknown to the Oracle.",
    "missing_argument": "🌑 Your ritual is incomplete. The Oracle requires additional components.",
    "bad_argument": "🌑 The components of your ritual are misaligned. Please reconsider your approach.",
    
    # AWS service errors
    "service_not_found": "🌑 This mystical service is not inscribed in the Oracle's tomes.",
    "docs_not_found": "🌑 The sacred scrolls for this service cannot be located in the ethereal archives.",
    
    # File and data errors
    "file_not_found": "🌑 The mystical scroll you seek does not exist in this realm.",
    "data_corruption": "🌑 The arcane knowledge has been corrupted by chaotic forces.",
    "save_failed": "🌑 The Oracle failed to inscribe this knowledge into the cosmic records.",
    
    # Network errors
    "connection_failed": "🌑 The Oracle's connection to the astral plane has been severed.",
    "api_error": "🌑 The distant realms have rejected the Oracle's communion attempt."
}

# Mystical warning messages
WARNING_MESSAGES = {
    "deprecated": "⚠️ This ancient ritual will soon fade from the Oracle's memory. Seek a new path.",
    "performance": "⚠️ The cosmic energies flow slowly through this ritual. Consider a more efficient approach.",
    "unstable": "⚠️ This enchantment is unstable and may produce unpredictable results.",
    "incomplete": "⚠️ Your ritual was completed, but some aspects remain unfulfilled.",
    "permission_partial": "⚠️ Your mystical authority grants only partial access to this ritual."
}

def log_vision(level: OracleVision, message: str, exc: Optional[Exception] = None) -> None:
    """
    Record the Oracle's vision in the mystical logs.
    
    Args:
        level: The clarity level of the vision
        message: The content of the vision
        exc: Optional exception that triggered the vision
    """
    if exc:
        oracle_logger.log(
            level.value,
            f"{message} | Mystical disturbance: {exc.__class__.__name__}: {str(exc)}"
        )
        if level.value >= logging.ERROR:
            oracle_logger.log(level.value, f"Arcane trace: {traceback.format_exc()}")
    else:
        oracle_logger.log(level.value, message)

def get_error_message(error_type: str) -> str:
    """
    Get a mystical error message for the given error type.
    
    Args:
        error_type: The type of error
        
    Returns:
        A mystical error message
    """
    return ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["general"])

def get_warning_message(warning_type: str) -> str:
    """
    Get a mystical warning message for the given warning type.
    
    Args:
        warning_type: The type of warning
        
    Returns:
        A mystical warning message
    """
    return WARNING_MESSAGES.get(warning_type, WARNING_MESSAGES["unstable"])