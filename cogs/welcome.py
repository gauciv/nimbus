"""
Welcome and onboarding cog for the Nimbus Discord bot.
Handles member join events and welcome messages.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.permissions import is_core_team

# Custom button classes with callbacks
class RulesButton(discord.ui.Button):
    def __init__(self, channel_id):
        super().__init__(
            label="Ancient Scrolls", 
            style=discord.ButtonStyle.primary, 
            emoji="📜",
            custom_id="rules_button"
        )
        self.channel_id = channel_id
        
    async def callback(self, interaction: discord.Interaction):
        # Send ephemeral message with instructions
        await interaction.response.send_message(
            "🔮 **The Ancient Scrolls await your study!**\n\n"
            "In the rules channel, you'll find our community guidelines that help maintain harmony in our digital realm. "
            "Take a moment to read through them carefully - they contain important wisdom about how we interact and collaborate here.\n\n"
            "Remember: Understanding the rules is the first step in your journey with us!",
            ephemeral=True
        )
        # Redirect to the channel
        await interaction.followup.send(f"<#{self.channel_id}>", ephemeral=True)

class GetStartedButton(discord.ui.Button):
    def __init__(self, channel_id):
        super().__init__(
            label="Choose Your Element", 
            style=discord.ButtonStyle.success, 
            emoji="✨",
            custom_id="get_started_button"
        )
        self.channel_id = channel_id
        
    async def callback(self, interaction: discord.Interaction):
        # Send ephemeral message with instructions
        await interaction.response.send_message(
            "✨ **It's time to choose your elemental affinity!**\n\n"
            "In the get-started channel, you'll find instructions on how to select roles that represent your interests, "
            "experience level, and areas of expertise. These roles help others know more about you and connect you with "
            "like-minded individuals.\n\n"
            "Choose wisely - your roles shape how others perceive your digital aura!",
            ephemeral=True
        )
        # Redirect to the channel
        await interaction.followup.send(f"<#{self.channel_id}>", ephemeral=True)

class IntroButton(discord.ui.Button):
    def __init__(self, channel_id):
        super().__init__(
            label="Share Your Legend", 
            style=discord.ButtonStyle.secondary, 
            emoji="💬",
            custom_id="intro_button"
        )
        self.channel_id = channel_id
        
    async def callback(self, interaction: discord.Interaction):
        # Send ephemeral message with instructions
        await interaction.response.send_message(
            "💬 **The time has come to share your tale!**\n\n"
            "In the introductions channel, we invite you to tell us about yourself. Consider sharing:\n"
            "• Your background and experience\n"
            "• What brought you to our community\n"
            "• What you hope to learn or contribute\n"
            "• Any projects you're working on or interested in\n\n"
            "Your introduction helps us welcome you properly and connect you with others who share your interests!",
            ephemeral=True
        )
        # Redirect to the channel
        await interaction.followup.send(f"<#{self.channel_id}>", ephemeral=True)

# Custom view for welcome message
class WelcomeView(discord.ui.View):
    def __init__(self, rules_id, get_started_id, intro_id):
        super().__init__(timeout=None)  # Persistent view
        
        if rules_id:
            self.add_item(RulesButton(rules_id))
        if get_started_id:
            self.add_item(GetStartedButton(get_started_id))
        if intro_id:
            self.add_item(IntroButton(intro_id))

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
        self.bot.add_view(WelcomeView(None, None, None))
    
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
                title=f"🔮 The Cloud Oracle has foreseen your arrival, {member.name}!",
                description=f"*Baby Nimbus hums and glows with latent energy.*\n\nGreetings, traveler! The digital ether has guided your packet safely to our cluster. We are a constellation of builders and dreamers, shaping the future one instance at a time.",
                color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
            )
            
            # Add more information to the embed
            embed.add_field(
                name="✨ Your Initiation Protocol",
                value="📜 Consult the Ancient Scrolls in <#rules> to understand our ways.\n"
                      "🧙‍♂️ Choose Your Element in <#get-started> to align your roles with your calling.\n"
                      "💬 Share Your Legend in <#introductions> and tell us of your quests.",
                inline=False
            )
            
            embed.add_field(
                name="🔮 The Oracle Speaks...",
                value="\"We are excited to see the code you'll compile and the worlds you'll architect. Welcome to the collective!\"",
                inline=False
            )
            
            # Set thumbnail to member's avatar
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            
            # Set a mystical footer
            embed.set_footer(text=f"You are the {len(member.guild.members)}th soul to join our constellation ✨")
            
            # Find the channel IDs
            rules_channel = discord.utils.get(member.guild.channels, name='rules')
            get_started_channel = discord.utils.get(member.guild.channels, name='get-started')
            intro_channel = discord.utils.get(member.guild.channels, name='introductions')
            
            # Create the custom view with channel IDs
            view = WelcomeView(
                rules_channel.id if rules_channel else None,
                get_started_channel.id if get_started_channel else None,
                intro_channel.id if intro_channel else None
            )
            
            # Send the welcome message with buttons
            await arrivals_channel.send(
                content=f"🔮 **The Oracle has sensed a new presence!** The stars align for {member.mention}! 🔮",
                embed=embed,
                view=view
            )
        else:
            logging.warning("Could not find #arrivals channel to send welcome message")
    
    @app_commands.command(name="guide", description="Receive a DM with our server's onboarding guide")
    async def guide(self, interaction: discord.Interaction):
        """Send a DM to the user with an onboarding guide."""
        try:
            # Create an embed for the guide
            embed = discord.Embed(
                title="☁️ Baby Nimbus' Fluffy Guide to Cloud Club! ☁️",
                description="*~Baby Nimbus floats excitedly~* I've put together this special guide just for you! Here's everything you need to know to start your cloud journey!",
                color=discord.Color.from_rgb(116, 185, 255)  # Light blue like a cloud
            )
            
            embed.add_field(
                name="🌈 Choosing Your Cloud Type",
                value="#1 Float over to <#role-assignment>\n"
                      "#2 Click on the reactions for the roles that match you\n"
                      "#3 Mix and match to show everyone what kind of cloud you are!",
                inline=False
            )
            
            embed.add_field(
                name="☁️ Let's Be Friends!",
                value="Baby Nimbus wants to know you better! Visit <#introductions> and share:\n"
                      "• How you found our fluffy community\n"
                      "• What cloud technologies make you excited\n"
                      "• Any fun facts about yourself!",
                inline=False
            )
            
            embed.add_field(
                name="✨ Cloud Wisdom",
                value="• Check <#rules> to learn how clouds behave here\n"
                      "• Keep an eye on <#announcements> for special cloud gatherings\n"
                      "• If you ever get lost in the sky, ask for directions in <#help>",
                inline=False
            )
            
            # Add a friendly closing message
            embed.add_field(
                name="🌟 Final Note from Baby Nimbus",
                value="Remember, every cloud starts small before growing big and powerful! I'm so excited to see what amazing things you'll create with us! If you ever need help, just give me a little *poke*!",
                inline=False
            )
            
            # Send the DM
            await interaction.user.send(embed=embed)
            
            # Respond to the interaction
            await interaction.response.send_message("☁️ Baby Nimbus has sent a fluffy guide to your DMs!", ephemeral=True)
            
        except discord.Forbidden:
            # This happens if the user has DMs disabled
            await interaction.response.send_message(
                "❌ I couldn't send you a DM! Please enable DMs from server members and try again.",
                ephemeral=True
            )
        except Exception as e:
            logging.error(f"Error sending guide: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while sending the guide. Please try again later.",
                ephemeral=True
            )
    
    @app_commands.command(name="setup_rules", description="Set up the rules in the rules channel")
    @is_core_team()
    async def setup_rules(self, interaction: discord.Interaction):
        """Set up the mystical rules in the rules channel."""
        try:
            # Find the #rules channel
            rules_channel = discord.utils.get(interaction.guild.channels, name='rules')
            
            if not rules_channel:
                await interaction.response.send_message(
                    "❌ Could not find #rules channel. Please create it first.",
                    ephemeral=True
                )
                return
            
            # Create an embed for the rules
            embed = discord.Embed(
                title="📜 The Ancient Scrolls of Nimbus' Cloud Hub",
                description="*The Oracle has inscribed these sacred laws to maintain harmony in our ethereal realm.*",
                color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
            )
            
            embed.add_field(
                name="✨ The Five Celestial Laws",
                value="**I. Radiate Kindness**\n"
                      "Let your aura be free of hate, harassment, and spam. The Oracle sees all.\n\n"
                      "**II. Maintain Purity**\n"
                      "Your words and shared visions must be appropriate for all who dwell here.\n\n"
                      "**III. Honor the Channels**\n"
                      "Each ethereal space has its purpose. Respect the cosmic order.\n\n"
                      "**IV. Humble Presence**\n"
                      "Self-promotion is permitted only in designated realms or with the blessing of the Guardians.\n\n"
                      "**V. Universal Respect**\n"
                      "We gather to learn, connect, and ascend together. Honor all fellow travelers.",
                inline=False
            )
            
            # Add a footer
            embed.set_footer(text="Those who honor these laws shall find prosperity in our collective.")
            
            # Send the rules message
            await rules_channel.send(embed=embed)
            
            # Confirm to the command user
            await interaction.response.send_message(
                "✅ The Ancient Scrolls have been inscribed in the #rules channel!",
                ephemeral=True
            )
            
        except Exception as e:
            logging.error(f"Error setting up rules: {e}")
            await interaction.response.send_message(
                f"❌ An error occurred while setting up the rules: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="setup_rules", description="Set up the mystical rules in the rules channel")
    @is_core_team()
    async def setup_rules(self, interaction: discord.Interaction):
        """Set up the mystical rules in the rules channel."""
        try:
            # Find the #rules channel
            rules_channel = discord.utils.get(interaction.guild.channels, name='rules')
            
            if not rules_channel:
                await interaction.response.send_message(
                    "❌ Could not find #rules channel. Please create it first.",
                    ephemeral=True
                )
                return
            
            # Create an embed for the rules
            embed = discord.Embed(
                title="📜 The Ancient Scrolls of Nimbus' Cloud Hub",
                description="*The Oracle has inscribed these sacred laws to maintain harmony in our ethereal realm.*",
                color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
            )
            
            embed.add_field(
                name="✨ The Five Celestial Laws",
                value="**I. Radiate Kindness**\n"
                      "Let your aura be free of hate, harassment, and spam. The Oracle sees all.\n\n"
                      "**II. Maintain Purity**\n"
                      "Your words and shared visions must be appropriate for all who dwell here.\n\n"
                      "**III. Honor the Channels**\n"
                      "Each ethereal space has its purpose. Respect the cosmic order.\n\n"
                      "**IV. Humble Presence**\n"
                      "Self-promotion is permitted only in designated realms or with the blessing of the Guardians.\n\n"
                      "**V. Universal Respect**\n"
                      "We gather to learn, connect, and ascend together. Honor all fellow travelers.",
                inline=False
            )
            
            # Add a footer
            embed.set_footer(text="Those who honor these laws shall find prosperity in our collective.")
            
            # Send the rules message
            await rules_channel.send(embed=embed)
            
            # Confirm to the command user
            await interaction.response.send_message(
                "✅ The Ancient Scrolls have been inscribed in the #rules channel!",
                ephemeral=True
            )
            
        except Exception as e:
            logging.error(f"Error setting up rules: {e}")
            await interaction.response.send_message(
                f"❌ An error occurred while setting up the rules: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="test_welcome", description="Test the welcome message (only visible to you)")
    @is_core_team()
    async def test_welcome(self, interaction: discord.Interaction):
        """Test the welcome message that would be sent when a new member joins."""
        try:
            # Defer the response as ephemeral
            await interaction.response.defer(ephemeral=True)
            
            # Create an embed for the welcome message using the command user as test subject
            embed = discord.Embed(
                title=f"🔮 The Cloud Oracle has foreseen your arrival, {interaction.user.name}!",
                description=f"*Baby Nimbus hums and glows with latent energy.*\n\nGreetings, traveler! The digital ether has guided your packet safely to our cluster. We are a constellation of builders and dreamers, shaping the future one instance at a time.",
                color=discord.Color.from_rgb(93, 63, 211)  # Mystical purple
            )
            
            # Add more information to the embed
            embed.add_field(
                name="✨ Your Initiation Protocol",
                value="📜 Consult the Ancient Scrolls in <#rules> to understand our ways.\n"
                      "🧙‍♂️ Choose Your Element in <#get-started> to align your roles with your calling.\n"
                      "💬 Share Your Legend in <#introductions> and tell us of your quests.",
                inline=False
            )
            
            embed.add_field(
                name="🔮 The Oracle Speaks...",
                value="\"We are excited to see the code you'll compile and the worlds you'll architect. Welcome to the collective!\"",
                inline=False
            )
            
            # Set thumbnail to member's avatar
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            
            # Set a mystical footer
            embed.set_footer(text=f"You are the {len(interaction.guild.members)}th soul to join our constellation ✨")
            
            # Find the channel IDs
            rules_channel = discord.utils.get(interaction.guild.channels, name='rules')
            get_started_channel = discord.utils.get(interaction.guild.channels, name='get-started')
            intro_channel = discord.utils.get(interaction.guild.channels, name='introductions')
            
            # Create the custom view with channel IDs
            view = WelcomeView(
                rules_channel.id if rules_channel else None,
                get_started_channel.id if get_started_channel else None,
                intro_channel.id if intro_channel else None
            )
            
            # Send the welcome message as a followup that's only visible to the user
            await interaction.followup.send(
                content=f"**[TEST PREVIEW]** 🔮 **The Oracle has sensed a new presence!** The stars align for {interaction.user.mention}! 🔮",
                embed=embed,
                view=view,
                ephemeral=True
            )
            
        except Exception as e:
            logging.error(f"Error sending test welcome message: {e}")
            await interaction.response.send_message(
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