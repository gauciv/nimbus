"""
Structured logging configuration for Nimbus Discord Bot.
"""
import structlog
import logging
import sys
from pathlib import Path
from utils.config import config

def setup_logging():
    """Configure structured logging."""
    
    # Ensure logs directory exists
    Path("data/logs").mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if config.environment == "production" 
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, config.log_level),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("data/logs/bot.log"),
        ]
    )
    
    # Reduce Discord.py verbosity
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

def get_logger(name: str):
    """Get a structured logger instance."""
    return structlog.get_logger(name)