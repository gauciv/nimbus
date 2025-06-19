"""
Error handling utilities for the Nimbus Discord bot.

This module provides mystical error handling for command errors.
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Union, Callable, Coroutine, Any

from utils.oracle import log_vision, OracleVision, get_error_message

async def handle_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
) -> None:
    """
    Handle command errors with mystical messages.
    
    Args:
        interaction: The interaction that triggered the error
        error: The error that occurred
    """
    error_message = ""
    
    # Handle specific error types
    if isinstance(error, app_commands.CommandNotFound):
        error_message = get_error_message("command_not_found")
        log_vision(OracleVision.PORTENT, f"Unknown incantation attempted: {error}")
        
    elif isinstance(error, app_commands.MissingPermissions):
        error_message = get_error_message("permission")
        log_vision(OracleVision.PORTENT, f"User lacks mystical authority: {error}")
        
    elif isinstance(error, app_commands.BotMissingPermissions):
        error_message = "🌑 The Oracle lacks the mystical authority to perform this ritual."
        log_vision(OracleVision.PORTENT, f"Bot lacks mystical authority: {error}")
        
    # Note: MissingRequiredArgument doesn't exist in discord.py 2.x for app_commands
    # Missing arguments are handled by Discord's built-in validation
        
    # Note: BadArgument doesn't exist in discord.py 2.x for app_commands
    # Bad arguments are handled by Discord's built-in validation
        
    elif isinstance(error, app_commands.CommandOnCooldown):
        error_message = get_error_message("rate_limit")
        log_vision(OracleVision.PORTENT, f"Ritual attempted too frequently: {error}")
        
    elif isinstance(error, app_commands.CheckFailure):
        # Determine the specific permission error based on the command
        if "admin" in str(error).lower() or "administrator" in str(error).lower():
            error_message = "🌑 Only those with administrative powers may invoke this ritual."
        elif "core team" in str(error).lower():
            error_message = "❌ This command requires Core Team permissions."
        else:
            error_message = get_error_message("permission")
        log_vision(OracleVision.PORTENT, f"Ritual check failed: {error}")
        
    else:
        # Generic error handling
        error_message = get_error_message("general")
        log_vision(OracleVision.OMEN, f"Unhandled mystical disturbance in command", error)
    
    # Send the error message if the interaction hasn't been responded to
    if not interaction.response.is_done():
        await interaction.response.send_message(error_message, ephemeral=True)
    else:
        # Try to send a followup if the interaction has already been responded to
        try:
            await interaction.followup.send(error_message, ephemeral=True)
        except discord.errors.HTTPException:
            # If we can't send a followup, log it
            log_vision(OracleVision.PORTENT, "Could not send error message to user")

def setup_error_handlers(bot: commands.Bot) -> None:
    """
    Set up error handlers for the bot.
    
    Args:
        bot: The Discord bot instance
    """
    # Set up the app command error handler
    bot.tree.on_error = handle_command_error
    
    # Set up the command error handler
    @bot.event
    async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
        """Handle command errors with mystical messages."""
        error_message = ""
        
        # Handle specific error types
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found errors
            
        elif isinstance(error, commands.MissingRequiredArgument):
            error_message = get_error_message("missing_argument")
            log_vision(OracleVision.PORTENT, f"Ritual components missing: {error}")
            
        elif isinstance(error, commands.BadArgument):
            error_message = get_error_message("bad_argument")
            log_vision(OracleVision.PORTENT, f"Ritual components misaligned: {error}")
            
        elif isinstance(error, commands.MissingPermissions):
            error_message = get_error_message("permission")
            log_vision(OracleVision.PORTENT, f"User lacks mystical authority: {error}")
            
        elif isinstance(error, commands.BotMissingPermissions):
            error_message = "🌑 The Oracle lacks the mystical authority to perform this ritual."
            log_vision(OracleVision.PORTENT, f"Bot lacks mystical authority: {error}")
            
        elif isinstance(error, commands.CommandOnCooldown):
            error_message = get_error_message("rate_limit")
            log_vision(OracleVision.PORTENT, f"Ritual attempted too frequently: {error}")
            
        elif isinstance(error, commands.CheckFailure):
            error_message = get_error_message("permission")
            log_vision(OracleVision.PORTENT, f"Ritual check failed: {error}")
            
        else:
            # Generic error handling
            error_message = get_error_message("general")
            log_vision(OracleVision.OMEN, f"Unhandled mystical disturbance in command", error)
        
        # Send the error message
        await ctx.send(error_message)