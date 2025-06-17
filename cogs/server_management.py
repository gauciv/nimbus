"""
Server management cog for the Nimbus Discord bot.
Handles server setup, channel management, and administrative commands.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.permissions import is_core_team

class ServerManagement(commands.Cog):
    """Commands for server setup and management."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the server management cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
    
    @app_commands.command(name="setup_core_team", description="Create the Core Team role and assign it to a member")
    @app_commands.describe(
        member="The member to add to Core Team"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_core_team(self, interaction: discord.Interaction, member: discord.Member = None):
        """Create the Core Team role with special permissions."""
        try:
            # Check if Core Team role already exists
            core_team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
            
            if not core_team_role:
                # Create the Core Team role with special permissions
                core_team_role = await interaction.guild.create_role(
                    name="Core Team",
                    color=discord.Color.gold(),
                    hoist=True,  # Display role members separately in the member list
                    mentionable=True,
                    permissions=discord.Permissions(
                        manage_messages=True,
                        mention_everyone=True,
                        manage_channels=True,
                        manage_roles=True
                    ),
                    reason="Core Team role creation"
                )
                await interaction.response.send_message(
                    "✅ Created Core Team role with administrative permissions!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "ℹ️ Core Team role already exists!",
                    ephemeral=True
                )
            
            # If a member was specified, add them to Core Team
            if member:
                if core_team_role in member.roles:
                    await interaction.followup.send(
                        f"{member.mention} is already a Core Team member!",
                        ephemeral=True
                    )
                else:
                    await member.add_roles(core_team_role)
                    await interaction.followup.send(
                        f"✅ Added {member.mention} to Core Team!",
                        ephemeral=True
                    )
                    
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles!",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Error setting up Core Team: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while setting up the Core Team role.",
                ephemeral=True
            )
    
    @app_commands.command(name="manage_core_team", description="Add or remove a member from Core Team")
    @app_commands.describe(
        action="Whether to add or remove the member",
        member="The member to add/remove from Core Team"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add to Core Team", value="add"),
        app_commands.Choice(name="Remove from Core Team", value="remove")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def manage_core_team(
        self,
        interaction: discord.Interaction,
        action: str,
        member: discord.Member
    ):
        """Add or remove a member from the Core Team."""
        try:
            # Get the Core Team role
            core_team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
            
            if not core_team_role:
                await interaction.response.send_message(
                    "❌ Core Team role doesn't exist! Use `/setup_core_team` first.",
                    ephemeral=True
                )
                return
            
            if action == "add":
                if core_team_role in member.roles:
                    await interaction.response.send_message(
                        f"{member.mention} is already a Core Team member!",
                        ephemeral=True
                    )
                else:
                    await member.add_roles(core_team_role)
                    await interaction.response.send_message(
                        f"✅ Added {member.mention} to Core Team!",
                        ephemeral=True
                    )
            else:  # action == "remove"
                if core_team_role not in member.roles:
                    await interaction.response.send_message(
                        f"{member.mention} is not a Core Team member!",
                        ephemeral=True
                    )
                else:
                    await member.remove_roles(core_team_role)
                    await interaction.response.send_message(
                        f"✅ Removed {member.mention} from Core Team!",
                        ephemeral=True
                    )
                    
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles!",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Error managing Core Team: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while managing Core Team membership.",
                ephemeral=True
            )
    
    @app_commands.command(name="check_channels", description="Check and list required channel setup for the bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def check_channels(self, interaction: discord.Interaction):
        """Check if all required channels exist and list their purposes."""
        required_channels = {
            "announcements": {
                "description": "For event announcements posted via /event command",
                "permissions": ["Send Messages", "Embed Links", "Mention Everyone"]
            },
            "arrivals": {
                "description": "For welcoming new members with information about the server",
                "permissions": ["Send Messages", "Embed Links"]
            },
            "aws-tips": {
                "description": "Receives daily AWS Cloud Tips automatically",
                "permissions": ["Send Messages", "Embed Links"]
            },
            "rules": {
                "description": "Server rules referenced in welcome messages",
                "permissions": ["Send Messages", "Embed Links"]
            },
            "get-started": {
                "description": "Getting started guide referenced in welcome messages",
                "permissions": ["Send Messages", "Embed Links"]
            }
        }

        embed = discord.Embed(
            title="🔍 Channel Setup Check",
            description="Here's the status of all required channels for the bot:",
            color=discord.Color.blue()
        )

        for channel_name, info in required_channels.items():
            channel = discord.utils.get(interaction.guild.channels, name=channel_name)
            status = "✅ Exists" if channel else "❌ Missing"
            
            embed.add_field(
                name=f"#{channel_name}",
                value=(
                    f"**Status:** {status}\n"
                    f"**Purpose:** {info['description']}\n"
                    f"**Required Permissions:** {', '.join(info['permissions'])}"
                ),
                inline=False
            )

        missing_channels = [
            name for name in required_channels.keys()
            if not discord.utils.get(interaction.guild.channels, name=name)
        ]

        if missing_channels:
            embed.add_field(
                name="📋 Setup Required",
                value=(
                    "The following channels need to be created:\n" +
                    "\n".join(f"• #{channel}" for channel in missing_channels) +
                    "\n\nMake sure to set appropriate permissions for each channel."
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="✅ All Set!",
                value="All required channels are set up correctly.",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="setup_channels", description="Create and configure all required channels")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_channels(self, interaction: discord.Interaction):
        """Create and configure all required channels."""
        try:
            required_channels = {
                "announcements": {
                    "description": "For event announcements posted via /event command",
                    "permissions": ["send_messages", "embed_links", "mention_everyone"],
                    "category": "TEXT CHANNELS"
                },
                "arrivals": {
                    "description": "For welcoming new members with information about the server",
                    "permissions": ["send_messages", "embed_links"],
                    "category": "TEXT CHANNELS"
                },
                "aws-tips": {
                    "description": "Receives daily AWS Cloud Tips automatically",
                    "permissions": ["send_messages", "embed_links"],
                    "category": "TEXT CHANNELS"
                },
                "rules": {
                    "description": "Server rules referenced in welcome messages",
                    "permissions": ["send_messages", "embed_links"],
                    "category": "INFORMATION"
                },
                "get-started": {
                    "description": "Getting started guide referenced in welcome messages",
                    "permissions": ["send_messages", "embed_links"],
                    "category": "INFORMATION"
                },
                "role-assignment": {
                    "description": "For managing role selections",
                    "permissions": ["send_messages", "embed_links", "add_reactions"],
                    "category": "INFORMATION"
                },
                "introductions": {
                    "description": "For new members to introduce themselves",
                    "permissions": ["send_messages", "embed_links"],
                    "category": "COMMUNITY"
                },
                "help": {
                    "description": "For assistance and support",
                    "permissions": ["send_messages", "embed_links"],
                    "category": "SUPPORT"
                }
            }

            # Send initial response
            await interaction.response.send_message("🔨 Setting up channels...", ephemeral=True)

            # Track progress
            created_channels = []
            existing_channels = []
            failed_channels = []

            for channel_name, info in required_channels.items():
                try:
                    # Check if channel exists
                    existing_channel = discord.utils.get(interaction.guild.channels, name=channel_name)
                    
                    if not existing_channel:
                        # Get or create category
                        category = discord.utils.get(interaction.guild.categories, name=info["category"])
                        if not category:
                            category = await interaction.guild.create_category(info["category"])

                        # Set up permissions for Core Team
                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(
                                read_messages=True,
                                send_messages=False
                            ),
                            interaction.guild.me: discord.PermissionOverwrite(**{
                                perm: True for perm in info["permissions"]
                            })
                        }
                        # Add Core Team role permissions if it exists
                        team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
                        if team_role:
                            overwrites[team_role] = discord.PermissionOverwrite(
                                read_messages=True,
                                send_messages=True,
                                manage_messages=True
                            )

                        channel = await interaction.guild.create_text_channel(
                            name=channel_name,
                            category=category,
                            topic=info["description"],
                            overwrites=overwrites
                        )
                        
                        created_channels.append(channel_name)
                        
                        # Send initial message based on channel type
                        if channel_name == "rules":
                            await channel.send("📜 Server Rules will be posted here.")
                        elif channel_name == "get-started":
                            await channel.send("🎯 Getting Started guide will be posted here.")
                        elif channel_name == "aws-tips":
                            await channel.send("☁️ Daily AWS tips will be posted here automatically!")
                        elif channel_name == "role-assignment":
                            await channel.send("🎭 Role assignment will be set up here. Use `/setup_roles` to configure.")
                    else:
                        existing_channels.append(channel_name)
                
                except Exception as e:
                    logging.error(f"Error creating channel {channel_name}: {e}")
                    failed_channels.append(channel_name)

            # Create status embed
            embed = discord.Embed(
                title="📋 Channel Setup Results",
                color=discord.Color.blue()
            )

            if created_channels:
                embed.add_field(
                    name="✅ Created Channels",
                    value="\n".join(f"• #{channel}" for channel in created_channels),
                    inline=False
                )

            if existing_channels:
                embed.add_field(
                    name="ℹ️ Already Existing",
                    value="\n".join(f"• #{channel}" for channel in existing_channels),
                    inline=False
                )

            if failed_channels:
                embed.add_field(
                    name="❌ Failed to Create",
                    value="\n".join(f"• #{channel}" for channel in failed_channels),
                    inline=False
                )

            embed.set_footer(text="Use /check_channels to verify the setup")

            # Update the response
            await interaction.edit_original_response(content=None, embed=embed)

        except Exception as e:
            logging.error(f"Error in setup_channels: {e}")
            await interaction.edit_original_response(
                content="❌ An error occurred while setting up channels. Check the bot's permissions."
            )
    
    @app_commands.command(name="setup", description="Set up the server (channels and roles)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """Set up all necessary components for the server."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # First, create Core Team role
            core_team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
            if not core_team_role:
                try:
                    core_team_role = await interaction.guild.create_role(
                        name="Core Team",
                        color=discord.Color.gold(),
                        hoist=True,
                        mentionable=True,
                        permissions=discord.Permissions(
                            manage_messages=True,
                            mention_everyone=True,
                            manage_channels=True,
                            manage_roles=True
                        ),
                        reason="Core Team role creation"
                    )
                    await interaction.user.add_roles(core_team_role)
                    await interaction.followup.send("✅ Created Core Team role and added you to it!", ephemeral=True)
                except discord.Forbidden:
                    await interaction.followup.send("❌ I don't have permission to create roles!", ephemeral=True)
                    return
                except Exception as e:
                    logging.error(f"Error creating Core Team role: {e}")
                    await interaction.followup.send("❌ Failed to create Core Team role!", ephemeral=True)
                    return

            # Set up channels
            channels_to_create = {
                "announcements": {"category": "TEXT CHANNELS"},
                "arrivals": {"category": "TEXT CHANNELS"},
                "aws-tips": {"category": "TEXT CHANNELS"},
                "rules": {"category": "INFORMATION"},
                "get-started": {"category": "INFORMATION"},
                "role-assignment": {"category": "INFORMATION"},
                "introductions": {"category": "COMMUNITY"},
                "help": {"category": "SUPPORT"}
            }

            created = []
            existing = []
            failed = []

            for channel_name, info in channels_to_create.items():
                try:
                    if not discord.utils.get(interaction.guild.channels, name=channel_name):
                        # Get or create category
                        category = discord.utils.get(interaction.guild.categories, name=info["category"])
                        if not category:
                            category = await interaction.guild.create_category(info["category"])

                        # Create channel
                        overwrites = {
                            interaction.guild.default_role: discord.PermissionOverwrite(
                                read_messages=True,
                                send_messages=False
                            ),
                            interaction.guild.me: discord.PermissionOverwrite(
                                read_messages=True,
                                send_messages=True,
                                manage_messages=True
                            )
                        }
                        # Add Core Team role permissions if it exists
                        team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
                        if team_role:
                            overwrites[team_role] = discord.PermissionOverwrite(
                                read_messages=True,
                                send_messages=True,
                                manage_messages=True
                            )

                        await interaction.guild.create_text_channel(
                            name=channel_name,
                            category=category,
                            overwrites=overwrites
                        )
                        created.append(channel_name)
                    else:
                        existing.append(channel_name)
                except Exception as e:
                    logging.error(f"Error creating channel {channel_name}: {e}")
                    failed.append(channel_name)

            # Send setup report
            embed = discord.Embed(
                title="Server Setup Results",
                color=discord.Color.blue()
            )

            if created:
                embed.add_field(
                    name="✅ Created Channels",
                    value="\n".join(f"• #{name}" for name in created),
                    inline=False
                )
            if existing:
                embed.add_field(
                    name="ℹ️ Existing Channels",
                    value="\n".join(f"• #{name}" for name in existing),
                    inline=False
                )
            if failed:
                embed.add_field(
                    name="❌ Failed to Create",
                    value="\n".join(f"• #{name}" for name in failed),
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logging.error(f"Error in setup: {e}")
            await interaction.followup.send(
                "❌ An error occurred during setup. Check the bot's permissions.",
                ephemeral=True
            )
    
    @app_commands.command(name="announce", description="Post an announcement in the announcements channel (Core Team only)")
    @app_commands.describe(
        message="The announcement message to post"
    )
    @is_core_team()
    async def announce(self, interaction: discord.Interaction, message: str):
        """Post an announcement in the #announcements channel."""
        try:
            # Find the announcements channel
            announcements_channel = discord.utils.get(interaction.guild.channels, name='announcements')
            if not announcements_channel:
                await interaction.response.send_message(
                    "❌ Could not find the #announcements channel.",
                    ephemeral=True
                )
                return

            # Create an embed for the announcement
            embed = discord.Embed(
                title="📢 Announcement",
                description=message,
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )

            # Add who made the announcement
            embed.add_field(
                name="Posted by",
                value=interaction.user.mention,
                inline=False
            )

            # Send the announcement
            try:
                await announcements_channel.send(
                    content="@everyone New announcement!",
                    embed=embed
                )
                
                # Confirm to the command user
                await interaction.response.send_message(
                    "✅ Announcement posted successfully!",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ I don't have permission to send messages in the announcements channel.",
                    ephemeral=True
                )
                
        except Exception as e:
            logging.error(f"Error posting announcement: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while posting the announcement.",
                ephemeral=True
            )
    
    @app_commands.command(name="topic", description="Start a discussion topic in the main chat")
    @app_commands.describe(
        question="The discussion topic or question to post"
    )
    @is_core_team()
    async def topic(self, interaction: discord.Interaction, question: str):
        """Post a discussion topic in the main chat channel."""
        try:
            # Defer the response since we'll be doing multiple operations
            await interaction.response.defer(ephemeral=True)
            
            # Create an embed for the discussion topic
            embed = discord.Embed(
                title="💭 Let's Discuss!",
                description=question,
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add who started the topic
            embed.add_field(
                name="Started by",
                value=interaction.user.mention,
                inline=False
            )
            
            # Add footer with tip
            embed.set_footer(text="Share your thoughts and experiences!")
            
            # Send the topic
            try:
                await interaction.channel.send(
                    content="@here A new discussion topic has been posted! 🗣️",
                    embed=embed
                )
                
                # Confirm to the command user
                await interaction.followup.send(
                    "✅ Discussion topic posted successfully!",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ I don't have permission to send messages in this channel.",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.followup.send(
                    "❌ Failed to send the topic message. Check my permissions.",
                    ephemeral=True
                )
                raise e
                
        except Exception as e:
            logging.error(f"Error posting discussion topic: {e}")
            try:
                await interaction.followup.send(
                    "❌ An error occurred while posting the discussion topic.",
                    ephemeral=True
                )
            except:
                # If we can't send a followup, the interaction might have already been responded to
                if not interaction.response.is_done():
                    await interaction.response.send_message(
                        "❌ An error occurred while posting the discussion topic.",
                        ephemeral=True
                    )

async def setup(bot: commands.Bot):
    """
    Add the ServerManagement cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(ServerManagement(bot))