import discord
from discord.ext import commands
import logging
import json
import sys

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

# Load config
try:
    with open('config.json') as f:
        config = json.load(f)
        print("Loaded config.json successfully")
except Exception as e:
    print(f"Error loading config.json: {e}")
    sys.exit(1)

# Create bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user.name}')

print("Starting bot...")
bot.run(config['token'])
