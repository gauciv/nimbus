"""
Permission utilities for the Nimbus Discord bot.
Handles permission checks and role-based access control.
"""
import discord
from discord import app_commands

def is_core_team():
    """
    Check if the user has the Core Team role.
    
    Returns:
        app_commands.check: A check that verifies the user has the Core Team role
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        core_team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
        if not core_team_role:
            await interaction.response.send_message(
                "❌ Core Team role not found in the server.",
                ephemeral=True
            )
            return False
        return core_team_role in interaction.user.roles
    return app_commands.check(predicate)