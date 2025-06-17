"""
Nimbus Discord Bot - A comprehensive Discord bot for AWS Cloud Club communities.
Version: 2.0
"""
import discord
from discord.ext import commands
import logging
import os
import sys
import asyncio
from utils.config import load_config

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Load configuration
config = load_config()

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
    print(f"\n✅ Bot is online! Logged in as {bot.user.name}")
    print(f"Connected to {len(bot.guilds)} server(s)")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✓ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"✗ Failed to sync commands: {str(e)}")
    
    print("Bot is ready to use!")

async def load_extensions():
    """Load all cogs/extensions."""
    success_count = 0
    failed_cogs = []
    
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            success_count += 1
        except Exception as e:
            failed_cogs.append(f"{cog} ({str(e)})")
    
    print(f"✓ Loaded {success_count}/{len(COGS)} extensions")
    
    if failed_cogs:
        print("Failed to load:")
        for cog in failed_cogs:
            print(f"  - {cog}")

def main():
    """Main function to start the bot."""
    try:
        print("Starting Nimbus Discord Bot...")
        
        # Run the bot
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)

async def start_bot():
    """Start the bot with proper async handling."""
    try:
        await load_extensions()
        await bot.start(config['token'])
    except Exception as e:
        print(f"Error starting bot: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

# Run the bot
if __name__ == "__main__":
    main()