"""
Role management utilities for the Nimbus Discord bot.
Handles role definitions, creation, and assignment.
"""
import discord
import logging
from typing import Dict, Set
from utils.config import load_json_data, save_json_data

# Role configuration
YEAR_ROLES = {
    "1️⃣": "First Year",
    "2️⃣": "Second Year",
    "3️⃣": "Third Year",
    "4️⃣": "Fourth Year",
    "🎓": "Graduate"
}

INTEREST_ROLES = {
    "🌐": "Web Dev",
    "📊": "Data Science",
    "🤖": "AI/ML",
    "📱": "Mobile Dev",
    "🔒": "Cybersecurity"
}

# File to store role message IDs
ROLE_MESSAGE_FILE = 'data/role_messages.json'

# Load role message IDs from file
role_message_ids: Set[int] = set(load_json_data(ROLE_MESSAGE_FILE, []))

def save_role_messages() -> bool:
    """
    Save role message IDs to file.
    
    Returns:
        bool: True if successful, False otherwise
    """
    return save_json_data(ROLE_MESSAGE_FILE, list(role_message_ids))

def create_role_embed() -> discord.Embed:
    """
    Create the role selection embed.
    
    Returns:
        discord.Embed: Formatted embed for role selection
    """
    embed = discord.Embed(
        title="Role Selection",
        description="React with the emojis below to get your roles!",
        color=discord.Color.blue()
    )
    
    # Year level section
    year_description = "\n".join([f"{emoji} - {role}" for emoji, role in YEAR_ROLES.items()])
    embed.add_field(
        name="📚 Year Level",
        value=year_description,
        inline=False
    )
    
    # Interests section
    interests_description = "\n".join([f"{emoji} - {role}" for emoji, role in INTEREST_ROLES.items()])
    embed.add_field(
        name="🎯 Primary Interests",
        value=interests_description,
        inline=False
    )
    
    embed.set_footer(text="Click on a reaction to add/remove the role!")
    return embed

async def ensure_roles_exist(guild: discord.Guild) -> bool:
    """
    Ensure all configured roles exist in the guild.
    
    Args:
        guild: Discord guild to check/create roles in
        
    Returns:
        bool: True if successful, False if errors occurred
    """
    try:
        # Combine all role names
        all_roles = {**YEAR_ROLES, **INTEREST_ROLES}
        existing_roles = {role.name for role in guild.roles}
        
        # Create missing roles
        for role_name in all_roles.values():
            if role_name not in existing_roles:
                await guild.create_role(
                    name=role_name,
                    mentionable=True,
                    reason="Created by role selection system"
                )
                logging.info(f"Created role: {role_name}")
        
        return True
    except discord.Forbidden:
        logging.error("Bot doesn't have permission to create roles")
        return False
    except Exception as e:
        logging.error(f"Error ensuring roles exist: {e}")
        return False