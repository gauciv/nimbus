"""
Welcome system for new members.
"""
import discord
from discord.ext import commands

class Welcome(commands.Cog):
    """Handles welcome messages and onboarding."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))