"""
Simple logging configuration for Nimbus Discord Bot.
"""
import logging
import os
from utils.config import config

def setup_logging():
    """Configure basic logging."""
    os.makedirs('data', exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data/bot.log')
        ]
    )
    
    # Reduce Discord.py verbosity
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)

def get_logger(name: str):
    """Get a logger instance."""
    return logging.getLogger(name)