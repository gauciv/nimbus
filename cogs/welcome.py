"""
Welcome and onboarding cog for the Nimbus Discord bot.
Handles member join events and welcome messages.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.permissions import is_core_team

class Welcome(commands.Cog):
    """Commands and listeners for welcoming new members."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the welcome cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
    
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
            
            # Create a view with a timeout (required for URL buttons)
            view = discord.ui.View(timeout=180)  # 3 minute timeout
            
            # Find the channel IDs
            rules_channel = discord.utils.get(member.guild.channels, name='rules')
            get_started_channel = discord.utils.get(member.guild.channels, name='get-started')
            intro_channel = discord.utils.get(member.guild.channels, name='introductions')
            
            # Add buttons if channels exist
            if rules_channel:
                view.add_item(discord.ui.Button(
                    label="Ancient Scrolls", 
                    style=discord.ButtonStyle.primary, 
                    emoji="📜",
                    url=f"https://discord.com/channels/{member.guild.id}/{rules_channel.id}"
                ))
            
            if get_started_channel:
                view.add_item(discord.ui.Button(
                    label="Choose Your Element", 
                    style=discord.ButtonStyle.success, 
                    emoji="✨",
                    url=f"https://discord.com/channels/{member.guild.id}/{get_started_channel.id}"
                ))
            
            if intro_channel:
                view.add_item(discord.ui.Button(
                    label="Share Your Legend", 
                    style=discord.ButtonStyle.secondary, 
                    emoji="💬",
                    url=f"https://discord.com/channels/{member.guild.id}/{intro_channel.id}"
                ))
            
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
    
    @app_commands.command(name="test_welcome", description="Test the welcome message without adding a new member")
    @is_core_team()
    async def test_welcome(self, interaction: discord.Interaction):
        """Test the welcome message that would be sent when a new member joins."""
        try:
            # Find the #arrivals channel
            arrivals_channel = discord.utils.get(interaction.guild.channels, name='arrivals')
            
            if not arrivals_channel:
                await interaction.response.send_message(
                    "❌ Could not find #arrivals channel. Please create it first.",
                    ephemeral=True
                )
                return
                
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
            
            # Create a view with a timeout (required for URL buttons)
            view = discord.ui.View(timeout=180)  # 3 minute timeout
            
            # Find the channel IDs
            rules_channel = discord.utils.get(interaction.guild.channels, name='rules')
            get_started_channel = discord.utils.get(interaction.guild.channels, name='get-started')
            intro_channel = discord.utils.get(interaction.guild.channels, name='introductions')
            
            # Add buttons if channels exist
            if rules_channel:
                view.add_item(discord.ui.Button(
                    label="Ancient Scrolls", 
                    style=discord.ButtonStyle.primary, 
                    emoji="📜",
                    url=f"https://discord.com/channels/{interaction.guild.id}/{rules_channel.id}"
                ))
            
            if get_started_channel:
                view.add_item(discord.ui.Button(
                    label="Choose Your Element", 
                    style=discord.ButtonStyle.success, 
                    emoji="✨",
                    url=f"https://discord.com/channels/{interaction.guild.id}/{get_started_channel.id}"
                ))
            
            if intro_channel:
                view.add_item(discord.ui.Button(
                    label="Share Your Legend", 
                    style=discord.ButtonStyle.secondary, 
                    emoji="💬",
                    url=f"https://discord.com/channels/{interaction.guild.id}/{intro_channel.id}"
                ))
            
            # Send the welcome message with buttons
            await arrivals_channel.send(
                content=f"**[TEST MESSAGE]** 🔮 **The Oracle has sensed a new presence!** The stars align for {interaction.user.mention}! 🔮",
                embed=embed,
                view=view
            )
            
            # Confirm to the command user
            await interaction.response.send_message(
                "✅ Test welcome message sent to #arrivals channel!",
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