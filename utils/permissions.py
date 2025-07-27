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
    Check if the user has the Core Team role, administrator permissions, or is the server owner.
    
    This decorator can be applied to slash commands to restrict them
    to users with the Core Team role or higher permissions.
    
    Returns:
        app_commands.check: A check that verifies the user has the Core Team role or admin permissions
        
    Example:
        @app_commands.command(name="admin_command")
        @is_core_team()
        async def admin_command(interaction: discord.Interaction):
            # This will only run if the user has the Core Team role
            await interaction.response.send_message("Admin command executed")
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        # Check if user is server owner or has administrator permissions (admins can use core team commands)
        if interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator:
            return True
        
        # Check for Core Team role
        core_team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
        if core_team_role and core_team_role in interaction.user.roles:
            return True
            
        return False
    return app_commands.check(predicate)

def is_admin() -> Callable[[discord.Interaction], Awaitable[bool]]:
    """
    Check if the user has administrator permissions or is the server owner.
    
    This decorator can be applied to slash commands to restrict them
    to users with administrator permissions or server owners.
    
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
        # Check if user is server owner or has administrator permissions
        if interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator:
            return True
        log_vision(OracleVision.PORTENT, f"User {interaction.user} attempted to use admin command without permissions")
        return False
    return app_commands.check(predicate)

# Permission level decorators
def admin_only():
    """Decorator for commands that require administrator permissions."""
    return is_admin()

def core_team_only():
    """Decorator for commands that require Core Team role."""
    return is_core_team()

def everyone():
    """Decorator for commands available to everyone (no restrictions)."""
    def decorator(func):
        return func
    return decorator

# Permission level mapping for easy reference
PERMISSION_LEVELS = {
    'admin': admin_only,
    'core_team': core_team_only, 
    'everyone': everyone
}