"""
Server management cog for the Nimbus Discord bot.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from pathlib import Path
import json
from utils.config import load_json_data, save_json_data
from utils.permission_levels import admin_only, core_team_only

class ServerManagement(commands.Cog):
    """Commands for server setup and management."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the server management cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
    


    @app_commands.command(name="manage_core_team", description="Add or remove a member from Core Team")
    @app_commands.describe(
        action="Whether to add or remove the member",
        member="The member to add/remove from Core Team"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="Add to Core Team", value="add"),
        app_commands.Choice(name="Remove from Core Team", value="remove")
    ])
    @admin_only()
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
    

    @app_commands.command(name="setup_channels", description="Create and configure all required channels")
    @admin_only()
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
                            embed = discord.Embed(
                                title="✨ Your Journey Begins Here",
                                description="Welcome, seeker of knowledge! Follow these mystical pathways to fully align yourself with our digital constellation.",
                                color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
                            )
                            
                            config_path = Path(__file__).parent.parent / 'data' / 'server_config.json'
                            with open(config_path) as f:
                                config = json.load(f)
                            
                            rules_id = config["channels"]["rules"]
                            role_id = config["channels"]["role-assignment"]
                            announcements_id = config["channels"]["announcements"]
                            general_id = config["channels"]["general-chat"]
                            
                            embed.add_field(
                                name="📜 Step 1: Ancient Scrolls",
                                value=f"First, venture to <#{rules_id}> to understand our sacred laws.",
                                inline=False
                            )
                            
                            embed.add_field(
                                name="� Step 2: Choose Your Path",
                                value=f"Journey to <#{role_id}> to select the roles that align with your skills and interests.",
                                inline=False
                            )
                            
                            embed.add_field(
                                name="📢 Step 3: Hear the Echo",
                                value=f"Listen to the voices of our elders in <#{announcements_id}> to stay informed of our gatherings and revelations.",
                                inline=False
                            )
                            
                            embed.add_field(
                                name="💭 Step 4: Join the Chorus",
                                value=f"Finally, make your voice heard in <#{general_id}>. Share your thoughts, ask questions, and connect with fellow travelers.",
                                inline=False
                            )
                            
                            embed.set_footer(text="May your code be bug-free and your deployments swift! ⚡")
                            
                            await channel.send(embed=embed)
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
    
    @app_commands.command(name="setup", description="Complete server setup for the bot")
    @admin_only()
    async def setup(self, interaction: discord.Interaction):
        """Dynamic server setup that finds existing channels and sets up content."""
        await interaction.response.defer(ephemeral=True)
        
        results = {
            "core_team": {"status": "❌", "message": ""},
            "get_started": {"status": "❌", "message": ""},
            "role_assignment": {"status": "❌", "message": ""},
            "rules_setup": {"status": "❌", "message": ""},
            "config_update": {"status": "❌", "message": ""},
            "recommendations": []
        }
        
        try:
            # 1. Core Team Role Setup
            core_team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
            if not core_team_role:
                results["core_team"]["status"] = "⚠️"
                results["core_team"]["message"] = "Core Team role not found"
                results["recommendations"].append("Create a 'Core Team' role manually with manage permissions")
            else:
                results["core_team"]["status"] = "✅"
                results["core_team"]["message"] = "Core Team role exists"
                if core_team_role not in interaction.user.roles:
                    await interaction.user.add_roles(core_team_role)
                    results["core_team"]["message"] += " (added to you)"
            
            # 2. Find and setup get-started channel
            get_started_keywords = ["get-started", "getting-started", "start", "guide", "welcome"]
            get_started_channel = None
            
            for channel in interaction.guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in get_started_keywords):
                    get_started_channel = channel
                    break
            
            if get_started_channel:
                # Check if guide already exists
                async for message in get_started_channel.history(limit=10):
                    if message.author == interaction.guild.me and "Your Journey Begins Here" in (message.embeds[0].title if message.embeds else ""):
                        results["get_started"]["status"] = "✅"
                        results["get_started"]["message"] = f"Guide exists in #{get_started_channel.name}"
                        break
                else:
                    # Create getting started guide
                    try:
                        embed = discord.Embed(
                            title="✨ Your Journey Begins Here",
                            description="Welcome to the AWS Cloud Club! Follow these steps to get started:",
                            color=discord.Color.purple()
                        )
                        
                        # Find other channels for references
                        rules_ch = discord.utils.find(lambda c: "rule" in c.name.lower(), interaction.guild.text_channels)
                        role_ch = discord.utils.find(lambda c: "role" in c.name.lower(), interaction.guild.text_channels)
                        announce_ch = discord.utils.find(lambda c: "announce" in c.name.lower(), interaction.guild.text_channels)
                        general_ch = discord.utils.find(lambda c: "general" in c.name.lower() or "chat" in c.name.lower(), interaction.guild.text_channels)
                        
                        steps = []
                        if rules_ch:
                            steps.append(f"📜 **Read the Rules** - Check {rules_ch.mention} to understand our community guidelines")
                        if role_ch:
                            steps.append(f"🎭 **Select Your Roles** - Visit {role_ch.mention} to choose roles that match your interests")
                        if announce_ch:
                            steps.append(f"📢 **Stay Updated** - Follow {announce_ch.mention} for important announcements and events")
                        if general_ch:
                            steps.append(f"💬 **Join Conversations** - Start chatting in {general_ch.mention} and introduce yourself")
                        
                        if not steps:
                            steps = [
                                "📜 **Read the Rules** - Familiarize yourself with community guidelines",
                                "🎭 **Select Your Roles** - Choose roles that match your interests",
                                "📢 **Stay Updated** - Follow announcements for events and updates",
                                "💬 **Join Conversations** - Introduce yourself and start participating"
                            ]
                        
                        embed.add_field(
                            name="🚀 Getting Started Steps",
                            value="\n\n".join(steps),
                            inline=False
                        )
                        
                        embed.add_field(
                            name="🔧 Useful Commands",
                            value="• `/aws <service>` - Learn about AWS services\n• `/docs <service>` - Get AWS documentation\n• `/about` - Learn about our club",
                            inline=False
                        )
                        
                        embed.set_footer(text="Welcome to the AWS Cloud Club! 🌟")
                        
                        await get_started_channel.send(embed=embed)
                        results["get_started"]["status"] = "✅"
                        results["get_started"]["message"] = f"Guide created in #{get_started_channel.name}"
                    except Exception as e:
                        results["get_started"]["status"] = "❌"
                        results["get_started"]["message"] = f"Failed to create guide: {str(e)}"
            else:
                results["get_started"]["status"] = "⚠️"
                results["get_started"]["message"] = "No suitable channel found"
                results["recommendations"].append("Create a channel with 'get-started' or 'guide' in the name")
            
            # 3. Find and setup role assignment channel
            role_keywords = ["role", "assign", "select"]
            role_channel = None
            
            for channel in interaction.guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in role_keywords):
                    role_channel = channel
                    break
            
            if role_channel:
                # Check if role system already exists
                async for message in role_channel.history(limit=20):
                    if message.author == interaction.guild.me and "Choose Your Path" in (message.embeds[0].title if message.embeds else ""):
                        results["role_assignment"]["status"] = "✅"
                        results["role_assignment"]["message"] = f"Role system exists in #{role_channel.name}"
                        break
                else:
                    # Setup role system
                    try:
                        from cogs.mystic_roles import STATUS_ROLES, COHORT_ROLES, INTEREST_ROLES
                        
                        # Ensure roles exist
                        all_roles = {**STATUS_ROLES, **COHORT_ROLES, **INTEREST_ROLES}
                        for info in all_roles.values():
                            if not discord.utils.get(interaction.guild.roles, name=info['name']):
                                await interaction.guild.create_role(name=info['name'], mentionable=True)
                        
                        # Create role selection messages
                        categories = {
                            "status": (STATUS_ROLES, "✨ Choose Your Path", "Select your current journey in the AWS Cloud Club"),
                            "cohort": (COHORT_ROLES, "📚 Academic Year", "Select your year of study"),
                            "interests": (INTEREST_ROLES, "🎯 Areas of Interest", "Choose your cloud computing interests")
                        }
                        
                        for category, (roles, title, desc) in categories.items():
                            embed = discord.Embed(title=title, description=desc, color=discord.Color.purple())
                            
                            role_text = "\n\n".join(
                                f"{emoji} **{info['name']}**\n*{info['description']}*"
                                for emoji, info in roles.items()
                            )
                            embed.add_field(name="Available Roles", value=role_text, inline=False)
                            
                            msg = await role_channel.send(embed=embed)
                            for emoji in roles.keys():
                                await msg.add_reaction(emoji)
                        
                        results["role_assignment"]["status"] = "✅"
                        results["role_assignment"]["message"] = f"Role system created in #{role_channel.name}"
                    except Exception as e:
                        results["role_assignment"]["status"] = "❌"
                        results["role_assignment"]["message"] = f"Failed to setup roles: {str(e)}"
            else:
                results["role_assignment"]["status"] = "⚠️"
                results["role_assignment"]["message"] = "No suitable channel found"
                results["recommendations"].append("Create a channel with 'role' or 'assignment' in the name")
            
            # 4. Find and setup rules channel
            rules_keywords = ["rule", "guideline"]
            rules_channel = None
            
            for channel in interaction.guild.text_channels:
                if any(keyword in channel.name.lower() for keyword in rules_keywords):
                    rules_channel = channel
                    break
            
            if rules_channel:
                # Check if rules already exist
                async for message in rules_channel.history(limit=10):
                    if message.author == interaction.guild.me and "Sacred Laws" in (message.embeds[0].title if message.embeds else ""):
                        results["rules_setup"]["status"] = "✅"
                        results["rules_setup"]["message"] = f"Rules exist in #{rules_channel.name}"
                        break
                else:
                    # Create server rules
                    try:
                        embed = discord.Embed(
                            title="📜 The Sacred Laws of Our Digital Realm",
                            description="Welcome, seeker, to the AWS Cloud Club! These ancient laws guide our mystical fellowship and ensure harmony within our constellation.",
                            color=discord.Color.purple()
                        )
                        
                        embed.add_field(
                            name="🌟 The First Law: Honor Thy Fellow Travelers",
                            value="Treat all members with respect and kindness. No harassment, discrimination, or offensive language shall disturb our sacred space.",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="🚫 The Second Law: Banish the Chaos of Spam",
                            value="Avoid excessive posting, repetitive messages, or unsolicited self-promotion. Share your wisdom thoughtfully and meaningfully.",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="🎓 The Third Law: Illuminate the Path for Others",
                            value="Share knowledge, answer questions, and support fellow members in their learning journey. We grow stronger together.",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="🗺️ The Fourth Law: Navigate the Channels Wisely",
                            value="Use appropriate channels for your discussions. Each channel serves a purpose in our organized realm.",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="⚖️ The Fifth Law: Uphold Digital Honor",
                            value="Do not share or request pirated software, illegal content, or copyrighted materials. Maintain the integrity of our community.",
                            inline=False
                        )
                        
                        embed.add_field(
                            name="⚡ Consequences of Transgression",
                            value="Those who violate these sacred laws may face warnings, temporary silencing, or banishment from our realm, depending on the severity.",
                            inline=False
                        )
                        
                        embed.set_footer(text="By joining our mystical fellowship, you pledge to honor these sacred laws. ✨")
                        
                        await rules_channel.send(embed=embed)
                        results["rules_setup"]["status"] = "✅"
                        results["rules_setup"]["message"] = f"Rules created in #{rules_channel.name}"
                    except Exception as e:
                        results["rules_setup"]["status"] = "❌"
                        results["rules_setup"]["message"] = f"Failed to create rules: {str(e)}"
            else:
                results["rules_setup"]["status"] = "⚠️"
                results["rules_setup"]["message"] = "No suitable channel found"
                results["recommendations"].append("Create a channel with 'rules' or 'guidelines' in the name")
            
            # 6. Update configuration with found channels
            try:
                config = load_json_data('data/server_config.json', {"channels": {}})
                channel_mapping = {
                    "get-started": get_started_keywords,
                    "role-assignment": role_keywords,
                    "announcements": ["announce", "news"],
                    "arrivals": ["arrival", "welcome", "join"],
                    "aws-tips": ["aws-tip", "tip", "daily"],
                    "rules": ["rule", "guideline"],
                    "general-chat": ["general", "chat", "main"],
                    "help": ["help", "support"]
                }
                
                found_channels = 0
                for config_name, keywords in channel_mapping.items():
                    for channel in interaction.guild.text_channels:
                        if any(keyword in channel.name.lower() for keyword in keywords):
                            config["channels"][config_name] = str(channel.id)
                            found_channels += 1
                            break
                
                save_json_data('data/server_config.json', config)
                results["config_update"]["status"] = "✅"
                results["config_update"]["message"] = f"Updated config with {found_channels} channels"
            except Exception as e:
                results["config_update"]["status"] = "❌"
                results["config_update"]["message"] = f"Config update failed: {str(e)}"
            
            # 7. Generate report
            embed = discord.Embed(
                title="🔧 Server Setup Report",
                description="Setup completed. Here's what was done:",
                color=discord.Color.green()
            )
            
            for task, result in results.items():
                if task != "recommendations":
                    embed.add_field(
                        name=f"{result['status']} {task.replace('_', ' ').title()}",
                        value=result['message'],
                        inline=False
                    )
            
            if results["recommendations"]:
                embed.add_field(
                    name="💡 Recommendations",
                    value="\n".join(f"• {rec}" for rec in results["recommendations"]),
                    inline=False
                )
            
            embed.set_footer(text="Setup is non-destructive - existing content was preserved")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Setup error: {e}")
            await interaction.followup.send(f"❌ Setup failed: {str(e)}", ephemeral=True)
    @app_commands.command(name="announce", description="✨ Proclaim a mystical decree to all seekers (post an announcement)")
    @app_commands.describe(
        message="The sacred proclamation to share with the realm (announcement message)"
    )
    @core_team_only()
    async def announce(self, interaction: discord.Interaction, message: str):
        """Post a mystical announcement in the #announcements channel."""
        try:
            # Find the announcements channel
            announcements_channel = discord.utils.find(
                lambda c: c.name.endswith('announcements') or c.name == 'announcements',
                interaction.guild.channels
            )
            if not announcements_channel:
                await interaction.response.send_message(
                    "🌑 The sacred chamber of proclamations cannot be found in this realm. (Missing #announcements channel)",
                    ephemeral=True
                )
                return

            # Create an embed for the announcement
            embed = discord.Embed(
                title="📜 Mystical Proclamation (Announcement)",
                description=message,
                color=discord.Color.purple(),
                timestamp=discord.utils.utcnow()
            )

            # Add who made the announcement
            embed.add_field(
                name="Proclaimed by (Posted by)",
                value=interaction.user.mention,
                inline=False
            )

            # Send the announcement
            try:
                await announcements_channel.send(
                    content="@everyone Heed this mystical proclamation from the Council of Elders! ✨",
                    embed=embed
                )
                
                # Confirm to the command user
                await interaction.response.send_message(
                    "✨ Your proclamation has been inscribed in the sacred chronicles! (Announcement posted successfully)",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "🌑 The Oracle lacks the mystical authority to speak in the chamber of proclamations. (Missing permissions)",
                    ephemeral=True
                )
                
        except Exception as e:
            logging.error(f"Error posting announcement: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while posting the announcement.",
                ephemeral=True
            )
    
    @app_commands.command(name="topic", description="✨ Invoke a mystical discussion in the communal gathering (start a topic)")
    @app_commands.describe(
        question="The arcane inquiry to present to the fellowship (discussion topic)"
    )
    @core_team_only()
    async def topic(self, interaction: discord.Interaction, question: str):
        """Post a mystical discussion topic in the main chat channel."""
        try:
            # Defer the response since we'll be doing multiple operations
            await interaction.response.defer(ephemeral=True)
            
            # Create an embed for the discussion topic
            embed = discord.Embed(
                title="🔮 Arcane Inquiry (Discussion Topic)",
                description=question,
                color=discord.Color.purple(),
                timestamp=discord.utils.utcnow()
            )
            
            # Add who started the topic
            embed.add_field(
                name="Invoked by (Started by)",
                value=interaction.user.mention,
                inline=False
            )
            
            # Add footer with tip
            embed.set_footer(text="✨ Share your wisdom and experiences with the fellowship! (Join the discussion)")
            
            # Send the topic
            try:
                await interaction.channel.send(
                    content="@here The Oracle presents a new arcane inquiry for your contemplation! 🌟",
                    embed=embed
                )
                
                # Confirm to the command user
                await interaction.followup.send(
                    "✨ Your mystical inquiry has been presented to the fellowship! (Topic posted successfully)",
                    ephemeral=True
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "🌑 The Oracle lacks the mystical authority to speak in this chamber. (Missing permissions)",
                    ephemeral=True
                )
            except Exception as e:
                await interaction.followup.send(
                    "🌑 The cosmic forces resist your attempt to invoke discussion. (Failed to send message)",
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

    @app_commands.command(
        name="update_channel_config",
        description="Update channel IDs in the configuration for an existing server"
    )
    @admin_only()
    async def update_channel_config(self, interaction: discord.Interaction):
        """Update channel IDs in server_config.json based on existing channels"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Load current config
            config = load_json_data('data/server_config.json', {"channels": {}})
            updated_channels = {}
            missing_channels = []
            
            # Required channel names
            required_channels = {
                "get-started": "Getting Started guide",
                "arrivals": "Welcome messages",
                "aws-tips": "AWS daily tips",
                "announcements": "Server announcements",
                "rules": "Server rules",
                "general-chat": "General discussion",
                "role-assignment": "Role selection",
                "help": "Help and support",
                "aws-services": "AWS services catalog"
            }
            
            # Find each channel and update config (handles emoji prefixes)
            for channel_name, description in required_channels.items():
                channel = discord.utils.find(
                    lambda c: c.name.endswith(channel_name) or c.name == channel_name,
                    interaction.guild.channels
                )
                if channel:
                    updated_channels[channel_name] = str(channel.id)
                else:
                    missing_channels.append(channel_name)
            
            # Update config with new channel IDs
            config["channels"] = updated_channels
            save_json_data('data/server_config.json', config)
            
            # Prepare response message
            response = ["✅ Channel configuration has been updated!"]
            if updated_channels:
                response.append("\n**Updated channels:**")
                for name, id in updated_channels.items():
                    response.append(f"• {name}: <#{id}>")
            
            if missing_channels:
                response.append("\n**Missing channels:**")
                for name in missing_channels:
                    response.append(f"• {name}")
                response.append("\nPlease create these channels and run this command again.")
            
            await interaction.followup.send("\n".join(response), ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error updating channel config: {e}")
            await interaction.followup.send(
                "❌ An error occurred while updating the channel configuration.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """
    Add the ServerManagement cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(ServerManagement(bot))