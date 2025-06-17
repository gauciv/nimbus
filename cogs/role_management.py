"""
Role management cog for the Nimbus Discord bot.
Handles role setup, assignment, and removal.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.roles import (
    YEAR_ROLES, INTEREST_ROLES, role_message_ids, 
    save_role_messages, create_role_embed, ensure_roles_exist
)
from utils.permissions import is_core_team

class RoleManagement(commands.Cog):
    """Commands and listeners for role management."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the role management cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
    
    @app_commands.command(name="setup_roles", description="Set up the role selection message (Admin only)")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_roles(self, interaction: discord.Interaction):
        """Create the role selection message."""
        try:
            # Check bot permissions first
            permissions = interaction.channel.permissions_for(interaction.guild.me)
            missing_perms = []
            
            if not permissions.manage_roles:
                missing_perms.append("Manage Roles")
            if not permissions.send_messages:
                missing_perms.append("Send Messages")
            if not permissions.add_reactions:
                missing_perms.append("Add Reactions")
            
            if missing_perms:
                await interaction.response.send_message(
                    f"❌ I'm missing the following permissions:\n" + 
                    "\n".join(f"• {perm}" for perm in missing_perms),
                    ephemeral=True
                )
                return
            
            logging.info(f"Setting up roles in channel {interaction.channel.name}")
            
            # First ensure all roles exist
            if not await ensure_roles_exist(interaction.guild):
                await interaction.response.send_message(
                    "❌ Failed to set up roles. Please check the bot's permissions.",
                    ephemeral=True
                )
                return
            
            # Create and send the embed
            embed = create_role_embed()
            await interaction.response.send_message("Setting up role selection...", ephemeral=True)
            
            try:
                # Send the role message
                role_message = await interaction.channel.send(embed=embed)
                role_message_ids.add(role_message.id)
                
                # Save the role message ID
                save_role_messages()
                
                # Add reactions
                for emoji in [*YEAR_ROLES.keys(), *INTEREST_ROLES.keys()]:
                    try:
                        await role_message.add_reaction(emoji)
                    except discord.HTTPException as e:
                        logging.error(f"Failed to add reaction {emoji}: {e}")
                
                logging.info(f"Successfully set up role message (ID: {role_message.id})")
                await interaction.edit_original_response(content="✅ Role selection has been set up!")
                
            except discord.Forbidden:
                logging.error("Failed to send role message or add reactions")
                await interaction.edit_original_response(
                    content="❌ Failed to set up roles. Please check the bot's permissions."
                )
            
        except discord.Forbidden as e:
            logging.error(f"Permission error setting up roles: {e}")
            await interaction.response.send_message(
                "❌ I don't have permission to set up roles. I need:\n"
                "• Manage Roles permission\n"
                "• Send Messages permission\n"
                "• Add Reactions permission",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Error setting up roles: {str(e)}", exc_info=True)
            await interaction.response.send_message(
                "❌ An error occurred while setting up roles.",
                ephemeral=True
            )
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle role assignment when a reaction is added."""
        try:
            # Ignore bot's own reactions
            if payload.user_id == self.bot.user.id:
                return
            
            # Check if this is a role message
            if payload.message_id not in role_message_ids:
                return
            
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                logging.error(f"Could not find guild with ID {payload.guild_id}")
                return
                
            member = guild.get_member(payload.user_id)
            if not member:
                logging.error(f"Could not find member with ID {payload.user_id}")
                return
                
            emoji = str(payload.emoji)
            
            # Check which role to assign
            role_name = YEAR_ROLES.get(emoji) or INTEREST_ROLES.get(emoji)
            if not role_name:
                return
            
            # Find and assign the role
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                try:
                    await member.add_roles(role)
                    logging.info(f"Assigned role {role_name} to {member}")
                except discord.Forbidden:
                    logging.error(f"Failed to assign role {role_name} to {member} - Missing permissions")
                except Exception as e:
                    logging.error(f"Error assigning role {role_name} to {member}: {e}")
            else:
                logging.error(f"Could not find role {role_name}")
        except Exception as e:
            logging.error(f"Error in on_raw_reaction_add: {e}", exc_info=True)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle role removal when a reaction is removed."""
        try:
            # Ignore bot's own reactions
            if payload.user_id == self.bot.user.id:
                return
            
            # Check if this is a role message
            if payload.message_id not in role_message_ids:
                return
            
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                logging.error(f"Could not find guild with ID {payload.guild_id}")
                return
                
            member = guild.get_member(payload.user_id)
            if not member:
                logging.error(f"Could not find member with ID {payload.user_id}")
                return
                
            emoji = str(payload.emoji)
            
            # Check which role to remove
            role_name = YEAR_ROLES.get(emoji) or INTEREST_ROLES.get(emoji)
            if not role_name:
                return
            
            # Find and remove the role
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                try:
                    await member.remove_roles(role)
                    logging.info(f"Removed role {role_name} from {member}")
                except discord.Forbidden:
                    logging.error(f"Failed to remove role {role_name} from {member} - Missing permissions")
                except Exception as e:
                    logging.error(f"Error removing role {role_name} from {member}: {e}")
            else:
                logging.error(f"Could not find role {role_name}")
        except Exception as e:
            logging.error(f"Error in on_raw_reaction_remove: {e}", exc_info=True)

async def setup(bot: commands.Bot):
    """
    Add the RoleManagement cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(RoleManagement(bot))