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
                title=f"Welcome to {member.guild.name}! 🎉",
                description=f"Hey {member.mention}, we're glad to have you here!",
                color=discord.Color.green()
            )
            
            # Add more information to the embed
            embed.add_field(
                name="Getting Started",
                value="Please make sure to check out the following channels:\n"
                      "📜 <#rules> - Server rules and guidelines\n"
                      "🎯 <#get-started> - How to get started in our community",
                inline=False
            )
            
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            embed.set_footer(text=f"Member #{len(member.guild.members)}")
            
            # Send the welcome message
            await arrivals_channel.send(embed=embed)
        else:
            logging.warning("Could not find #arrivals channel to send welcome message")
    
    @app_commands.command(name="guide", description="Receive a DM with our server's onboarding guide")
    async def guide(self, interaction: discord.Interaction):
        """Send a DM to the user with an onboarding guide."""
        try:
            # Create an embed for the guide
            embed = discord.Embed(
                title="🌟 Welcome to Our Server! - Getting Started Guide",
                description="Here's everything you need to know to get started in our community!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="👥 Getting Roles",
                value="1. Head to <#role-assignment>\n"
                      "2. Click on the reactions or buttons for the roles you want\n"
                      "3. You can mix and match roles to your liking!",
                inline=False
            )
            
            embed.add_field(
                name="👋 Introduce Yourself",
                value="We'd love to meet you! Visit <#introductions> and tell us:\n"
                      "• What brought you here\n"
                      "• What you're interested in\n"
                      "• Anything else you'd like to share!",
                inline=False
            )
            
            embed.add_field(
                name="💡 Tips",
                value="• Read <#rules> to avoid any issues\n"
                      "• Check <#announcements> regularly\n"
                      "• Don't hesitate to ask for help in <#help>",
                inline=False
            )
            
            # Send the DM
            await interaction.user.send(embed=embed)
            
            # Respond to the interaction
            await interaction.response.send_message("📬 Check your DMs for the guide!", ephemeral=True)
            
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
                title=f"Welcome to {interaction.guild.name}! 🎉",
                description=f"Hey {interaction.user.mention}, we're glad to have you here!",
                color=discord.Color.green()
            )
            
            # Add more information to the embed
            embed.add_field(
                name="Getting Started",
                value="Please make sure to check out the following channels:\n"
                      "📜 <#rules> - Server rules and guidelines\n"
                      "🎯 <#get-started> - How to get started in our community",
                inline=False
            )
            
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.set_footer(text=f"Member #{len(interaction.guild.members)}")
            
            # Send the welcome message
            await arrivals_channel.send(
                content="**[TEST MESSAGE]** This is how a welcome message would appear:",
                embed=embed
            )
            
            # Confirm to the command user
            await interaction.response.send_message(
                "✅ Test welcome message sent to #arrivals channel!",
                ephemeral=True
            )
            
        except Exception as e:
            logging.error(f"Error sending test welcome message: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while sending the test welcome message.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """
    Add the Welcome cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(Welcome(bot))