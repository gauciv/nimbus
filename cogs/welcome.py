"""
Welcome and onboarding cog for the Nimbus Discord bot.
Handles member join events and welcome messages.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.permissions import is_core_team
from utils.config import load_json_data

def load_config():
    """Load server configuration using the centralized config utility."""
    return load_json_data('data/server_config.json', {"channels": {}})

# Custom button classes with callbacks
# Simple button to redirect to get-started
class SimpleGetStartedButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Get Started", 
            style=discord.ButtonStyle.primary, 
            emoji="✨",
            custom_id="simple_get_started_button"
        )
        
    async def callback(self, interaction: discord.Interaction):
        # Load channel ID from config
        config = load_config()
        channel_id = config["channels"].get("get_started")
        
        if channel_id:
            await interaction.response.send_message(f"Welcome! Redirecting you to <#{channel_id}>...", ephemeral=True)
            # This will directly take the user to the channel
            channel = interaction.guild.get_channel(int(channel_id))
            if channel:
                await channel.send(f"{interaction.user.mention}", delete_after=0.1)
        else:
            await interaction.response.send_message("The get-started channel hasn't been configured yet. Please contact an administrator.", ephemeral=True)

# Role selection button class
class RoleButton(discord.ui.Button):
    def __init__(self, emoji, role_name):
        super().__init__(
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            custom_id=f"role_{role_name.replace(' ', '_').lower()}"
        )
        self.role_name = role_name
        self.emoji = emoji
        
    async def callback(self, interaction: discord.Interaction):
        # Find the role
        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        
        if not role:
            await interaction.response.send_message(
                f"❌ Role '{self.role_name}' not found. Please contact an administrator.",
                ephemeral=True
            )
            return
            
        # Toggle the role
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f"✨ You have unequipped the **{self.role_name}** role.",
                ephemeral=True
            )
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✨ You have been granted the **{self.role_name}** role!",
                ephemeral=True
            )

# Custom view for welcome message
class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistent view
        self.add_item(SimpleGetStartedButton())

# Role selection views
class StatusRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton("🎓", "Student"))
        self.add_item(RoleButton("💼", "Professional (Sage)"))
        self.add_item(RoleButton("👨‍🎓", "Alumni (Ascended)"))

class CohortRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton("1️⃣", "First Year"))
        self.add_item(RoleButton("2️⃣", "Second Year"))
        self.add_item(RoleButton("3️⃣", "Third Year"))
        self.add_item(RoleButton("4️⃣", "Fourth Year"))

class InterestRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton("🕸️", "Web Developer (Web Weaver)"))
        self.add_item(RoleButton("🔮", "Data Scientist (Data Sage)"))
        self.add_item(RoleButton("🏗️", "Cloud Architect (System Crafter)"))
        self.add_item(RoleButton("🛡️", "Security Engineer (Digital Guardian)"))
        self.add_item(RoleButton("🤖", "AI/ML Engineer (Tech Mystic)"))

class Welcome(commands.Cog):
    """Commands and listeners for welcoming new members."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the welcome cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        
        # Register the persistent view
        self.bot.add_view(WelcomeView())

    async def send_welcome_dm(self, member: discord.Member):
        """Send a personalized welcome DM to a new member."""
        try:
            # Create an embed for the welcome DM
            embed = discord.Embed(
                title="✨ Welcome to the AWS Cloud Club!",
                description=(
                    f"Greetings {member.name}, and welcome to our mystical realm!\n\n"
                    "*The Oracle senses great potential within you...*"
                ),
                color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
            )
            
            # Add getting started section
            embed.add_field(
                name="🌟 Your First Steps",
                value=(
                    "Here's how to begin your journey:\n"
                    "**1.** Check the rules to understand our ways\n"
                    "**2.** Choose your roles to unlock relevant channels\n"
                    "**3.** Introduce yourself in the arrivals channel\n"
                    "**4.** Join the conversations in general chat"
                ),
                inline=False
            )
            
            # Add useful commands section
            embed.add_field(
                name="🔮 Mystical Commands",
                value=(
                    "*Use these enchantments to navigate our realm:*\n"
                    "`/about` - Learn about our fellowship\n"
                    "`/join` - View detailed membership information\n"
                    "`/aws <service>` - Learn about AWS services\n"
                    "`/docs <service>` - Access AWS documentation"
                ),
                inline=False
            )
            
            # Add help section
            embed.add_field(
                name="📚 Need Guidance?",
                value=(
                    "• Ask questions in any channel\n"
                    "• Core team members have special roles\n"
                    "• Check pinned messages for resources\n"
                    "• The Oracle (bot) is here to help!"
                ),
                inline=False
            )
            
            # Set footer
            embed.set_footer(text="Your presence strengthens our constellation ✨")
            
            # Send the welcome DM
            await member.send(embed=embed)
            logging.info(f"Welcome DM sent to {member.name}#{member.discriminator}")
            
        except discord.Forbidden:
            logging.warning(f"Could not send welcome DM to {member.name}#{member.discriminator} (DMs closed)")
        except Exception as e:
            logging.error(f"Error sending welcome DM: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Event triggered when a new member joins the server.
        
        Args:
            member: The member who joined
        """
        # Send welcome DM
        await self.send_welcome_dm(member)
        
        # Find the #arrivals channel
        arrivals_channel = discord.utils.get(member.guild.channels, name='arrivals')
        
        if arrivals_channel:
            # Create an embed for the welcome message
            embed = discord.Embed(
                title=f"🔮 The Oracle has sensed a new presence!",
                description=f"*Baby Nimbus hums and glows with latent energy.*\n\nGreetings, traveler! The digital ether has guided your packet safely to our cluster. We are a constellation of builders and dreamers, shaping the future one instance at a time.",
                color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
            )
            
            # Add the Oracle's message
            embed.add_field(
                name="🔮 The Oracle Speaks...",
                value="\"We are excited to see the code you'll compile and the worlds you'll architect. Welcome to the collective!\"",
                inline=False
            )
            
            # Set thumbnail to member's avatar
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            
            # Set footer with member count
            guild_member_count = len(member.guild.members)
            suffix = "th" if 10 <= guild_member_count % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(guild_member_count % 10, "th")
            embed.set_footer(text=f"You are the {guild_member_count}{suffix} soul to join our constellation ✨")
            
            # Create view with get started button
            view = WelcomeView()
            
            # Send the welcome message
            await arrivals_channel.send(
                content=f"🔮 The stars align for {member.mention}!",
                embed=embed,
                view=view
            )
        else:
            logging.warning("Could not find #arrivals channel to send welcome message")

    @app_commands.command(name="test_welcome", description="Test the welcome message (only visible to you)")
    @is_core_team()
    async def test_welcome(self, interaction: discord.Interaction):
        """Test the welcome message that would be sent when a new member joins."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Create the same embed as the real welcome message
            embed = discord.Embed(
                title=f"🔮 The Oracle has sensed a new presence!",
                description=f"*Baby Nimbus hums and glows with latent energy.*\n\nGreetings, traveler! The digital ether has guided your packet safely to our cluster. We are a constellation of builders and dreamers, shaping the future one instance at a time.",
                color=discord.Color.from_rgb(93, 63, 211)
            )
            
            embed.add_field(
                name="🔮 The Oracle Speaks...",
                value="\"We are excited to see the code you'll compile and the worlds you'll architect. Welcome to the collective!\"",
                inline=False
            )
            
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            
            guild_member_count = len(interaction.guild.members)
            suffix = "th" if 10 <= guild_member_count % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(guild_member_count % 10, "th")
            embed.set_footer(text=f"You are the {guild_member_count}{suffix} soul to join our constellation ✨")
            
            # Create view with get started button
            view = WelcomeView()
            
            # Send as test message
            await interaction.followup.send(
                content=f"**[TEST PREVIEW]** 🔮 The stars align for {interaction.user.mention}!",
                embed=embed,
                view=view,
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Error sending test welcome message: {e}")
            await interaction.followup.send(
                f"❌ An error occurred while sending the test welcome message: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name="test_welcome_dm", description="Test the welcome DM (sends you a test DM)")
    @is_core_team()
    async def test_welcome_dm(self, interaction: discord.Interaction):
        """Test the welcome DM that would be sent when a new member joins."""
        try:
            await interaction.response.defer(ephemeral=True)
            await self.send_welcome_dm(interaction.user)
            await interaction.followup.send("✅ Test welcome DM sent!", ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error sending test welcome DM: {e}")
            await interaction.followup.send(
                "❌ Failed to send test welcome DM. Make sure your DMs are open.",
                ephemeral=True
            )

    @app_commands.command(name="setup_get_started", description="Set up the getting started guide")
    @is_core_team()
    async def setup_get_started(self, interaction: discord.Interaction):
        """Set up the getting started guide in the get-started channel."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Load channel IDs from config
            config = load_config()
            channels = config.get("channels", {})
            
            # Dictionary to store channels and their names
            required_channels = {
                "get-started": None,
                "rules": None,
                "role-assignment": None,
                "announcements": None,
                "general-chat": None
            }
            
            # Try to get all required channels
            missing_channels = []
            for channel_name in required_channels:
                channel_id = channels.get(channel_name)
                if not channel_id:
                    missing_channels.append(channel_name)
                    continue
                    
                try:
                    channel = interaction.guild.get_channel(int(channel_id))
                    if channel is None:
                        missing_channels.append(channel_name)
                        continue
                    required_channels[channel_name] = channel
                except ValueError:
                    missing_channels.append(channel_name)
                    logging.error(f"Invalid channel ID for {channel_name}: {channel_id}")
            
            if missing_channels:
                await interaction.followup.send(
                    f"❌ The following channels are not properly configured in server_config.json:\n"
                    f"• " + "\n• ".join(missing_channels),
                    ephemeral=True
                )
                return
            
            try:
                # Create an embed for the getting started guide
                embed = discord.Embed(
                    title="✨ Your Journey Begins Here",
                    description="*The Oracle's energy flows through these sacred halls, guiding new travelers on their path.*\n\n"
                              "Follow these steps to begin your journey in our digital realm:",
                    color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
                )
                
                embed.add_field(
                    name="📜 1. The Ancient Scrolls",
                    value=f"First, venture to {required_channels['rules'].mention} to understand our ways and customs.",
                    inline=False
                )
                
                embed.add_field(
                    name="✨ 2. Choose Your Path",
                    value=f"Next, visit {required_channels['role-assignment'].mention} to select roles that align with your interests and expertise.",
                    inline=False
                )
                
                embed.add_field(
                    name="📢 3. Stay Informed",
                    value=f"Keep watch in {required_channels['announcements'].mention} for important news and upcoming events.",
                    inline=False
                )
                
                embed.add_field(
                    name="💬 4. Join the Conversation",
                    value=f"Finally, introduce yourself in {required_channels['general-chat'].mention} and connect with fellow travelers.",
                    inline=False
                )
                
                embed.add_field(
                    name="🌟 Additional Notes",
                    value="• Feel free to explore other channels as you settle in\n"
                          "• Don't hesitate to ask questions if you need guidance\n"
                          "• Engage with the community and share your knowledge",
                    inline=False
                )
                
                # Set footer
                embed.set_footer(text="Your presence strengthens our constellation ✨")
                
                # Clear the channel
                await required_channels['get-started'].purge()
                
                # Send the guide
                await required_channels['get-started'].send(embed=embed)
                
                # Confirm to the command user
                await interaction.followup.send(
                    "✅ The getting started guide has been set up!",
                    ephemeral=True
                )
                
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ I don't have permission to manage messages in the get-started channel.",
                    ephemeral=True
                )
            except Exception as e:
                logging.error(f"Error creating/sending get-started guide: {e}")
                await interaction.followup.send(
                    "❌ An error occurred while creating or sending the guide.",
                    ephemeral=True
                )
                
        except Exception as e:
            logging.error(f"Error in setup_get_started: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An unexpected error occurred. Please check the bot logs.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ An unexpected error occurred. Please check the bot logs.",
                    ephemeral=True
                )

async def setup(bot: commands.Bot):
    """
    Add the Welcome cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(Welcome(bot))