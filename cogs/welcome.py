"""
Welcome and onboarding cog for the Nimbus Discord bot.
Handles member join events and welcome messages.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import json
from pathlib import Path
from utils.permissions import is_core_team

def load_config():
    config_path = Path(__file__).parent.parent / 'data' / 'server_config.json'
    try:
        with open(config_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"channels": {}}

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
        self.add_item(RoleButton("💼", "Professional"))
        self.add_item(RoleButton("🌟", "Alumni"))

class CohortRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton("✨", "First Year Novice"))
        self.add_item(RoleButton("✨✨", "Second Year Apprentice"))
        self.add_item(RoleButton("✨✨✨", "Third Year Adept"))
        self.add_item(RoleButton("✨✨✨✨", "Fourth Year Master"))

class InterestRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton("🕸️", "Web Weaver"))
        self.add_item(RoleButton("🔮", "Data Diviner"))
        self.add_item(RoleButton("🏗️", "System Architect"))
        self.add_item(RoleButton("🛡️", "Security Sentinel"))
        self.add_item(RoleButton("🤖", "AI Apprentice"))

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

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Event triggered when a new member joins the server.
        
        Args:
            member: The member who joined
        """
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

async def setup(bot: commands.Bot):
    """
    Add the Welcome cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(Welcome(bot))