"""
Event management cog for the Nimbus Discord bot.
"""
import discord
from discord.ext import commands

class EventCommands(commands.Cog):
    """Event management commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(EventCommands(bot))