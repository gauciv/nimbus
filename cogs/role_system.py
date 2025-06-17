"""
Enhanced role management system for the AWS Cloud Club Discord bot.
Handles status, cohort, and interest-based roles with reaction-based assignment.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
import os
from typing import Dict, Set

# Role Categories and Configurations
STATUS_ROLES = {
    "�": {
        "name": "Seeker",
        "description": "A curious soul on the path of cloud wisdom"
    },
    "⚡": {
        "name": "Sage",
        "description": "A seasoned practitioner who guides others through the digital mists"
    },
    "�": {
        "name": "Ascended",
        "description": "One who has completed their initial journey and now walks new paths"
    }
}

COHORT_ROLES = {
    "✨": {
        "name": "First Year Novice",
        "description": "An initiate taking their first steps into the clouded realms"
    },
    "✨✨": {
        "name": "Second Year Apprentice",
        "description": "A student of the clouds, weaving their first spells"
    },
    "✨✨✨": {
        "name": "Third Year Adept",
        "description": "A practiced wielder of cloud magicks, crafting advanced incantations"
    },
    "✨✨✨✨": {
        "name": "Fourth Year Master",
        "description": "A master of cloud arts, preparing to ascend beyond the academy"
    }
}

INTEREST_ROLES = {
    "🕸️": {
        "name": "Web Weaver",
        "description": "Artisans who craft the very fabric of the digital realm"
    },
    "🔮": {
        "name": "Data Diviner",
        "description": "Mystics who unveil truths hidden within the streams of data"
    },
    "🏗️": {
        "name": "System Architect",
        "description": "Masters who shape the foundational pillars of our cloud sanctum"
    },
    "🛡️": {
        "name": "Security Sentinel",
        "description": "Guardians who protect our digital sanctuaries from dark forces"
    },
    "🤖": {
        "name": "AI Apprentice",
        "description": "Seekers of artificial consciousness and mechanical wisdom"
    }
}

# File to store role message IDs
ROLE_CONFIG_FILE = 'data/role_config.json'

class RoleSystem(commands.Cog):
    """Handles role management and assignment through reactions."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role_messages = self.load_role_config()

    def load_role_config(self) -> Dict[str, int]:
        """Load role message configuration from file."""
        try:
            if os.path.exists(ROLE_CONFIG_FILE):
                with open(ROLE_CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return {"status": 0, "cohort": 0, "interests": 0}
        except Exception as e:
            logging.error(f"Error loading role config: {e}")
            return {"status": 0, "cohort": 0, "interests": 0}

    def save_role_config(self):
        """Save role message configuration to file."""
        try:
            os.makedirs(os.path.dirname(ROLE_CONFIG_FILE), exist_ok=True)
            with open(ROLE_CONFIG_FILE, 'w') as f:
                json.dump(self.role_messages, f)
        except Exception as e:
            logging.error(f"Error saving role config: {e}")

    async def create_role_embed(self, category: str, roles: dict) -> discord.Embed:
        """Create an embed for role selection."""
        titles = {
            "status": "✨ Manifest Your Essence",
            "cohort": "🌌 Choose Your Path of Ascension",
            "interests": "🔮 Attune Your Elemental Affinities"
        }
        
        descriptions = {
            "status": "The Oracle foresees your current standing in our mystical realm. Choose the energy that resonates with your soul's journey.",
            "cohort": "Your journey through the clouds follows an ancient progression. Select the cycle that mirrors your current evolution.",
            "interests": "The digital cosmos holds many secrets. Align yourself with the forces that call to your spirit."
        }

        embed = discord.Embed(
            title=titles[category],
            description=descriptions[category],
            color=discord.Color.from_rgb(75, 0, 130)  # Deep mystical purple
        )

        role_text = "\n\n".join(
            f"{emoji} **{info['name']}**\n{info['description']}"
            for emoji, info in roles.items()
        )
        embed.add_field(
            name="✧ Available Manifestations ✧",
            value=role_text,
            inline=False
        )
        
        # Add a mystical footer based on the category
        footers = {
            "status": "🌟 Channel your inner light - click the symbols to reveal your true form",
            "cohort": "✨ The stars guide your progression - choose the constellation that mirrors your journey",
            "interests": "🔮 Let your spirit resonate with the elements that call to you"
        }
        embed.set_footer(text=footers[category])
        
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
                        reason="Created by role management system"
                    )
                    logging.info(f"Created role: {role_name}")
            return True
        except Exception as e:
            logging.error(f"Error ensuring roles exist: {e}")
            return False

    @app_commands.command(name="setup_roles", description="Set up the role selection system")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_roles(self, interaction: discord.Interaction):
        """Set up the role selection system with reaction-based role assignment."""
        try:
            # Verify bot permissions
            permissions = interaction.channel.permissions_for(interaction.guild.me)
            required_perms = ["manage_roles", "send_messages", "add_reactions"]
            
            missing_perms = [
                perm for perm in required_perms 
                if not getattr(permissions, perm)
            ]
            
            if missing_perms:
                await interaction.response.send_message(
                    f"❌ Missing permissions: {', '.join(missing_perms)}",
                    ephemeral=True
                )
                return

            await interaction.response.defer(ephemeral=True)

            # Ensure roles exist
            if not await self.ensure_roles_exist(interaction.guild):
                await interaction.followup.send(
                    "❌ Failed to set up roles. Check permissions.",
                    ephemeral=True
                )
                return

            # Set up each category
            categories = {
                "status": STATUS_ROLES,
                "cohort": COHORT_ROLES,
                "interests": INTEREST_ROLES
            }

            for category, roles in categories.items():
                embed = await self.create_role_embed(category, roles)
                msg = await interaction.channel.send(embed=embed)
                self.role_messages[category] = msg.id
                
                # Add reactions
                for emoji in roles.keys():
                    await msg.add_reaction(emoji)

            # Save configuration
            self.save_role_config()
            
            await interaction.followup.send(
                "✨ The ancient role sigils have been inscribed! The Oracle's channeling circles are now ready to receive the whispers of our members' true natures. May they choose their paths wisely! ✨",
                ephemeral=True
            )

        except Exception as e:
            logging.error(f"Error in setup_roles: {e}")
            await interaction.followup.send(
                "❌ An error occurred during setup.",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle role assignment when reactions are added."""
        if payload.user_id == self.bot.user.id:
            return

        # Check if this is a role message
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
        roles_dict = globals()[f"{category.upper()}_ROLES"]
        
        if emoji in roles_dict:
            role_name = roles_dict[emoji]["name"]
            role = discord.utils.get(guild.roles, name=role_name)
            
            if role:
                try:
                    await member.add_roles(role)
                    logging.info(f"Added role {role_name} to {member}")
                except Exception as e:
                    logging.error(f"Error adding role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle role removal when reactions are removed."""
        if payload.user_id == self.bot.user.id:
            return

        # Check if this is a role message
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
        roles_dict = globals()[f"{category.upper()}_ROLES"]
        
        if emoji in roles_dict:
            role_name = roles_dict[emoji]["name"]
            role = discord.utils.get(guild.roles, name=role_name)
            
            if role:
                try:
                    await member.remove_roles(role)
                    logging.info(f"Removed role {role_name} from {member}")
                except Exception as e:
                    logging.error(f"Error removing role: {e}")

async def setup(bot: commands.Bot):
    """Add the RoleSystem cog to the bot."""
    await bot.add_cog(RoleSystem(bot))
