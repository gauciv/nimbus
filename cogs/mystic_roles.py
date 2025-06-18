"""
Mystical role management system for the Nimbus Discord bot.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Dict, Set
from utils.oracle import log_vision, OracleVision

# Role Categories and Configurations
STATUS_ROLES = {
    "🎓": {
        "name": "Student",
        "description": "An aspiring cloud practitioner on their learning journey"
    },
    "💼": {
        "name": "Professional (Sage)",
        "description": "An experienced practitioner sharing knowledge with the community"
    },
    "👨‍🎓": {
        "name": "Alumni (Ascended)",
        "description": "A graduate who continues to contribute to our community"
    }
}

COHORT_ROLES = {
    "1️⃣": {
        "name": "First Year",
        "description": "Beginning your journey into cloud computing"
    },
    "2️⃣": {
        "name": "Second Year",
        "description": "Building upon your foundational knowledge"
    },
    "3️⃣": {
        "name": "Third Year",
        "description": "Developing advanced cloud solutions"
    },
    "4️⃣": {
        "name": "Fourth Year",
        "description": "Mastering cloud architecture and preparing for industry"
    }
}

INTEREST_ROLES = {
    "🕸️": {
        "name": "Web Developer (Web Weaver)",
        "description": "Focused on web development and cloud-native applications"
    },
    "🔮": {
        "name": "Data Scientist (Data Sage)",
        "description": "Exploring data analytics and business intelligence"
    },
    "🏗️": {
        "name": "Cloud Architect (System Crafter)",
        "description": "Designing and implementing cloud infrastructure"
    },
    "🛡️": {
        "name": "Security Engineer (Digital Guardian)",
        "description": "Specializing in cloud security and compliance"
    },
    "🤖": {
        "name": "AI/ML Engineer (Tech Mystic)",
        "description": "Working with machine learning and artificial intelligence"
    }
}

# File to store role message IDs
ROLE_CONFIG_FILE = 'data/mystic_roles.json'

class MysticRoles(commands.Cog):
    """Handles the mystical role management system."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role_messages = self.load_role_config()

    def load_role_config(self) -> Dict[str, int]:
        """Load role message configuration from file using centralized config utility."""
        from utils.config import load_json_data
        return load_json_data(ROLE_CONFIG_FILE, {"status": 0, "cohort": 0, "interests": 0})

    def save_role_config(self):
        """Save role message configuration to file using centralized config utility."""
        from utils.config import save_json_data
        save_json_data(ROLE_CONFIG_FILE, self.role_messages)

    async def create_mystical_embed(self, category: str, roles: dict) -> discord.Embed:
        """Create a formatted embed for role selection."""
        if category == "status":
            title = "✨ Choose Your Path"
            description = "Select a role that represents your current journey in the AWS Cloud Club."
            section_name = "⚡ Community Roles"
        elif category == "cohort":
            title = "📚 Academic Year"
            description = "Select your current year of study to connect with peers at your level."
            section_name = "📖 Year Levels"
        else:  # interests
            title = "🎯 Areas of Interest"
            description = "Choose the areas of cloud computing that interest you most. These roles will unlock relevant channels!"
            section_name = "💫 Specializations"

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.dark_purple()
        )

        # Add mystical separator
        embed.add_field(
            name="═══════✧══════",
            value="Channel your inner light - click the symbols to reveal your true form",
            inline=False
        )

        # Format roles with mystical flair
        role_text = "\n\n".join(
            f"{emoji} **{info['name']}**\n╰─ *{info['description']}*"
            for emoji, info in roles.items()
        )
        
        embed.add_field(name=section_name, value=role_text, inline=False)
        
        # Add mystical footer
        embed.add_field(
            name="═══════✧══════",
            value="*The symbols await your touch - choose wisely, for they shape your path*",
            inline=False
        )
        
        return embed

    async def ensure_roles_exist(self, guild: discord.Guild) -> bool:
        """Ensure all configured roles exist in the guild."""
        try:
            all_roles = {**STATUS_ROLES, **COHORT_ROLES, **INTEREST_ROLES}
            existing_roles = {role.name: role for role in guild.roles}
            
            for info in all_roles.values():
                role_name = info['name']
                if role_name not in existing_roles:
                    await guild.create_role(
                        name=role_name,
                        mentionable=True,
                        reason="Created by the mystical role system"
                    )
                    logging.info(f"Manifested role: {role_name}")
            return True
        except Exception as e:
            logging.error(f"Error manifesting roles: {e}")
            return False

    @app_commands.command(name="setup_roles", description="🌟 Initialize the mystical role selection system")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_roles(self, interaction: discord.Interaction):
        """Set up the mystical role selection system."""
        try:
            # Verify ethereal permissions
            permissions = interaction.channel.permissions_for(interaction.guild.me)
            required_perms = ["manage_roles", "send_messages", "add_reactions"]
            
            missing_perms = [
                perm for perm in required_perms 
                if not getattr(permissions, perm)
            ]
            
            if missing_perms:
                await interaction.response.send_message(
                    f"❌ The mystical energies are blocked. Missing permissions: {', '.join(missing_perms)}",
                    ephemeral=True
                )
                return

            await interaction.response.defer(ephemeral=True)

            # Manifest the roles
            if not await self.ensure_roles_exist(interaction.guild):
                await interaction.followup.send(
                    "❌ The ethereal energies resist. Unable to manifest roles.",
                    ephemeral=True
                )
                return

            # Create the mystical selection interface
            categories = {
                "status": STATUS_ROLES,
                "cohort": COHORT_ROLES,
                "interests": INTEREST_ROLES
            }

            for category, roles in categories.items():
                embed = await self.create_mystical_embed(category, roles)
                msg = await interaction.channel.send(embed=embed)
                self.role_messages[category] = msg.id
                
                # Add mystical reactions
                for emoji in roles.keys():
                    await msg.add_reaction(emoji)

            # Save the ethereal configuration
            self.save_role_config()
            
            await interaction.followup.send(
                "✨ The mystical role selection system has been manifested!",
                ephemeral=True
            )

        except Exception as e:
            logging.error(f"Error in setup_roles: {e}")
            log_vision(OracleVision.OMEN, "Failed to setup mystical role system", e)
            await interaction.followup.send(
                "❌ A disturbance in the ethereal plane prevents the setup.",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Channel role energy when reactions are added."""
        if payload.user_id == self.bot.user.id:
            return

        # Check if this is a mystical role message
        category = None
        for cat, msg_id in self.role_messages.items():
            if payload.message_id == msg_id:
                category = cat
                break

        if not category:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        emoji = str(payload.emoji)
        
        # Map category to the correct role dictionary
        role_dicts = {
            "status": STATUS_ROLES,
            "cohort": COHORT_ROLES,
            "interests": INTEREST_ROLES  # Note: Dictionary name doesn't have 's'
        }
        
        roles_dict = role_dicts.get(category)
        
        if emoji in roles_dict:
            role_name = roles_dict[emoji]["name"]
            role = discord.utils.get(guild.roles, name=role_name)
            
            if role:
                try:
                    await member.add_roles(role)
                    logging.info(f"Channeled role {role_name} to {member}")
                except Exception as e:
                    log_vision(OracleVision.OMEN, f"Error channeling role energy for {member}", e)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Release role energy when reactions are removed."""
        if payload.user_id == self.bot.user.id:
            return

        category = None
        for cat, msg_id in self.role_messages.items():
            if payload.message_id == msg_id:
                category = cat
                break

        if not category:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        emoji = str(payload.emoji)
        
        # Map category to the correct role dictionary
        role_dicts = {
            "status": STATUS_ROLES,
            "cohort": COHORT_ROLES,
            "interests": INTEREST_ROLES  # Note: Dictionary name doesn't have 's'
        }
        
        roles_dict = role_dicts.get(category)
        
        if roles_dict and emoji in roles_dict:
            role_name = roles_dict[emoji]["name"]
            role = discord.utils.get(guild.roles, name=role_name)
            
            if role:
                try:
                    await member.remove_roles(role)
                    logging.info(f"Released role {role_name} from {member}")
                except Exception as e:
                    log_vision(OracleVision.OMEN, f"Error releasing role energy for {member}", e)

async def setup(bot: commands.Bot):
    """Manifest the MysticRoles cog in the ethereal plane."""
    await bot.add_cog(MysticRoles(bot))
