"""
Information and help commands.
"""
import discord
from discord.ext import commands

class Info(commands.Cog):
    """Information and help commands."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))