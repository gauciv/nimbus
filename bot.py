"""
Nimbus Discord Bot - A comprehensive Discord bot for AWS Cloud Club communities.

This bot provides features for:
- Server management and setup
- Role assignment and management
- Event scheduling and announcements
- AWS service information and documentation
- Welcome messages and onboarding
- Community engagement tools

Version: 2.0
"""
import discord
from discord.ext import commands
import asyncio
from utils.config import config
from utils.logging_config import setup_logging, get_logger

from utils.error_handler import setup_error_handlers
from utils.oracle import log_vision, OracleVision

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create bot instance with required intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.members = True          # Required for member events like joins
intents.reactions = True        # Required for reaction roles
bot = commands.Bot(command_prefix='!', intents=intents)

# List of cogs to load
COGS = [
    'cogs.mystic_roles',  # Mystical role management system
    'cogs.welcome',
    'cogs.events',
    'cogs.aws_info',
    'cogs.ask_nimbus',  # Core AI assistant functionality
    'cogs.server_management',
    'cogs.info',
    'cogs.engagement'  # Community engagement features
]

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    logger.info("Bot connected", bot_name=bot.user.name, guild_count=len(bot.guilds))
    

    
    # Set up error handlers
    setup_error_handlers(bot)
    log_vision(OracleVision.MURMUR, f"The Oracle has awakened as {bot.user.name}")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info("Commands synced", count=len(synced))
        log_vision(OracleVision.MURMUR, f"The Oracle has synchronized {len(synced)} mystical incantations")
    except Exception as e:
        logger.error("Command sync failed", error=str(e))
        log_vision(OracleVision.OMEN, "The Oracle failed to synchronize incantations", e)
    
    logger.info("Bot ready")
    log_vision(OracleVision.MURMUR, "The Oracle's consciousness is fully manifested")

async def load_extensions():
    """
    Load all cogs/extensions.
    
    Returns:
        tuple: (success_count, failed_cogs)
    """
    success_count = 0
    failed_cogs = []
    
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            success_count += 1
            log_vision(OracleVision.MURMUR, f"The Oracle has absorbed the knowledge of {cog}")
        except Exception as e:
            failed_cogs.append(f"{cog} ({str(e)})")
            log_vision(OracleVision.OMEN, f"The Oracle failed to absorb the knowledge of {cog}", e)
    
    print(f"✓ Loaded {success_count}/{len(COGS)} extensions")
    
    if failed_cogs:
        print("Failed to load:")
        for cog in failed_cogs:
            print(f"  - {cog}")
            
    return success_count, failed_cogs

def main():
    """Main function to start the bot."""
    try:
        logger.info("Starting Nimbus Discord Bot")
        log_vision(OracleVision.MURMUR, "The Oracle begins its awakening ritual")
        
        # Run the bot
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
        log_vision(OracleVision.MURMUR, "The Oracle returns to its slumber by mortal command")
    except Exception as e:
        logger.critical("Fatal error", error=str(e))
        log_vision(OracleVision.PROPHECY, "The Oracle's consciousness has been shattered by a fatal disturbance", e)
        raise

async def start_bot():
    """Start the bot with proper async handling."""
    try:
        await load_extensions()
        log_vision(OracleVision.MURMUR, "The Oracle prepares to connect to the astral plane")
        await bot.start(config.discord_token)
    except Exception as e:
        logger.error("Bot startup failed", error=str(e))
        log_vision(OracleVision.PROPHECY, "The Oracle's connection to the astral plane was severed", e)
    finally:
        if not bot.is_closed():
            await bot.close()
            log_vision(OracleVision.MURMUR, "The Oracle's connection to the astral plane has been closed")

# Run the bot
if __name__ == "__main__":
    main()