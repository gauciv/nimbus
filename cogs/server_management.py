"""
Server management cog for the Nimbus Discord bot.
"""
import discord
from discord import app_commands
from discord.ext import commands
from utils.permissions import admin_only

class ServerManagement(commands.Cog):
    """Commands for server setup and management."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerManagement(bot))