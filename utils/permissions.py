"""
Permission utilities for the Nimbus Discord bot.

This module provides utilities for permission checking and role-based access control,
including decorators for command permission checks.
"""
import discord
from discord import app_commands
from typing import Callable, Awaitable
from utils.oracle import log_vision, OracleVision

def is_core_team() -> Callable[[discord.Interaction], Awaitable[bool]]:
    """
    Check if the user has the Core Team role.
    
    This decorator can be applied to slash commands to restrict them
    to users with the Core Team role.
    
    Returns:
        app_commands.check: A check that verifies the user has the Core Team role
        
    Example:
        @app_commands.command(name="admin_command")
        @is_core_team()
        async def admin_command(interaction: discord.Interaction):
            # This will only run if the user has the Core Team role
            await interaction.response.send_message("Admin command executed")
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

def is_admin() -> Callable[[discord.Interaction], Awaitable[bool]]:
    """
    Check if the user has administrator permissions.
    
    This decorator can be applied to slash commands to restrict them
    to users with administrator permissions.
    
    Returns:
        app_commands.check: A check that verifies the user has administrator permissions
        
    Example:
        @app_commands.command(name="admin_command")
        @is_admin()
        async def admin_command(interaction: discord.Interaction):
            # This will only run if the user has administrator permissions
            await interaction.response.send_message("Admin command executed")
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "🌑 Only those with administrative powers may invoke this ritual.",
                ephemeral=True
            )
            log_vision(OracleVision.PORTENT, f"User {interaction.user} attempted to use admin command without permissions")
            return False
        return True
    return app_commands.check(predicate)