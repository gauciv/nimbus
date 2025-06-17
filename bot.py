"""
Nimbus Discord Bot - A comprehensive Discord bot for AWS Cloud Club communities.

This bot provides features for:
- Server management and setup
- Role assignment and management
- Event scheduling and announcements
- AWS service information and documentation
- Welcome messages and onboarding
- Community engagement tools

Author: AWS Cloud Club
Version: 2.0
"""
import discord
from discord.ext import commands
import logging
import os
import sys
import traceback
import asyncio
from utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/bot_debug.log')
    ]
)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

# Catch and log any uncaught exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to log uncaught exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# Load configuration
config = load_config()

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Create bot instance with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

# List of cogs to load
COGS = [
    'cogs.role_management',
    'cogs.welcome',
    'cogs.events',
    'cogs.aws_info',
    'cogs.server_management',
    'cogs.info'
]

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    logging.info(f'Bot is online! Logged in as {bot.user.name} (ID: {bot.user.id})')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")
    
    logging.info('------')

async def load_extensions():
    """Load all cogs/extensions."""
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            logging.info(f"Loaded extension: {cog}")
        except Exception as e:
            logging.error(f"Failed to load extension {cog}: {e}")
            traceback.print_exc()

async def main():
    """Main function to start the bot."""
    try:
        # Load all extensions
        await load_extensions()
        
        # Start the bot
        await bot.start(config['token'])
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        logging.info("Received keyboard interrupt. Shutting down...")
        await bot.close()
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())