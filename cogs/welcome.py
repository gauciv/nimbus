"""
Welcome system for new members.
"""
import discord
from discord.ext import commands
from discord import app_commands
from utils.dragon_personality import DragonPersonality
from utils.permissions import admin_only
import random

class Welcome(commands.Cog):
    """Handles welcome messages and onboarding with Nimbus's dragon personality."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle new member arrivals."""
        await self._welcome_member(member)
    
    async def _welcome_member(self, member):
        """Welcome a new member with dragon personality."""
        # Find arrivals channel
        arrivals_channel = discord.utils.find(
            lambda c: 'arrival' in c.name.lower() or 'welcome' in c.name.lower(),
            member.guild.text_channels
        )
        
        if arrivals_channel:
            # Public announcement
            public_message = self._get_public_welcome(member)
            embed = discord.Embed(
                title="☁️ New Cloud Visitor Detected!",
                description=public_message,
                color=DragonPersonality.COLORS['success']
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=DragonPersonality.get_success_footer())
            
            await arrivals_channel.send(embed=embed)
        
        # Private DM
        try:
            dm_message = self._get_private_welcome(member)
            embed = discord.Embed(
                title="🐉 Welcome to My Cloud Kingdom!",
                description=dm_message,
                color=DragonPersonality.COLORS['primary']
            )
            embed.add_field(
                name="🌤️ Important Stuff (that I definitely remember):",
                value="• Read the rules (they're probably important)\n• Pick some roles to show what you're into\n• Don't be mean to other cloud dwellers\n• Ask questions! I love showing off my knowledge",
                inline=False
            )
            embed.set_footer(text="I'm totally a mature and responsible greeter dragon! 🐉")
            
            await member.send(embed=embed)
        except discord.Forbidden:
            # Can't send DM, that's okay
            pass
    
    def _get_public_welcome(self, member):
        """Get a random public welcome message."""
        messages = [
            f"*flaps wings excitedly* Ooh ooh! {member.mention} just landed in our cloud kingdom! I'm definitely the first to notice because I'm very observant and mature!",
            f"*tries to look official* Attention everyone! {member.mention} has arrived and I, as the totally professional greeter dragon, welcome them to our realm!",
            f"*puffs out chest proudly* Behold! {member.mention} has chosen to join our prestigious cloud community! I shall personally ensure they feel... uh... welcomed!",
            f"*adjusts tiny crown* {member.mention} has entered our domain! As the most mature dragon here, I officially declare them... welcomed! *nailed it*",
            f"*clears throat importantly* {member.mention} has arrived! Everyone be nice to them because I'm in charge of making good first impressions!",
            f"*flutters around excitedly then tries to act cool* Oh, {member.mention}? Yeah, I totally saw them coming. Welcome to the cloud zone, I guess."
        ]
        return random.choice(messages)
    
    def _get_private_welcome(self, member):
        """Get a random private welcome message."""
        messages = [
            f"*whispers conspiratorially* Hey {member.display_name}! I'm Nimbus, and I'm basically the most important dragon around here. Don't tell anyone, but I'm still figuring out how to be a good greeter...",
            f"*tries to sound wise* Greetings, {member.display_name}! I am Nimbus, your totally mature and knowledgeable guide to this cloud kingdom. I definitely know all the rules and stuff!",
            f"*fidgets nervously* Um, hi {member.display_name}! I'm supposed to tell you important things but I might have forgotten some... The rules are somewhere, and there are channels for things!",
            f"*straightens up importantly* Welcome, {member.display_name}! I'm Nimbus, the official... unofficial... well, I'm A dragon who helps people! I'm very good at it!",
            f"*flaps wings proudly* {member.display_name}! You picked the BEST server to join because I'm here! I know everything about AWS and clouds and... other important stuff!"
        ]
        return random.choice(messages)
    
    @app_commands.command(name="test-welcome", description="🧪 Test the welcome system")
    @admin_only()
    async def test_welcome(self, interaction: discord.Interaction):
        """Test the welcome system with the command user."""
        await interaction.response.send_message("🐉 Testing welcome system...", ephemeral=True)
        await self._welcome_member(interaction.user)
        await interaction.edit_original_response(content="✅ Welcome test completed! Check the arrivals channel and your DMs.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))