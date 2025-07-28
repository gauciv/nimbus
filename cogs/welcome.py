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
            member_count = member.guild.member_count
            embed = discord.Embed(
                description=public_message,
                color=DragonPersonality.COLORS['success']
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(
                name="📊 Cloud Kingdom Census",
                value=f"We now have **{member_count}** cloud dwellers! \n\n> *tries to count on claws but gets confused*",
                inline=False
            )
            embed.set_footer(text=DragonPersonality.get_success_footer())
            
            await arrivals_channel.send(embed=embed)
        
        # Private DM
        try:
            dm_message = self._get_private_welcome(member)
            embed = discord.Embed(
                description=dm_message,
                color=DragonPersonality.COLORS['primary']
            )
            embed.add_field(
                name="📋 **SUPER IMPORTANT REGULATIONS** (that I definitely didn't forget):",
                value="• 📖 Peruse our rules (they're probably... definitely important!)\n• 🎭 Select your roles to show your... your... SOPHISTICATION!\n• 🤝 Be nice to fellow cloud dwellers (obviously)\n• 🙋‍♂️ Ask questions! I know EVERYTHING! Well... most things... some things...",
                inline=False
            )
            embed.add_field(
                name="☁️ **P.S.**",
                value="If you need AWS help, I've got that covered too! *puffs out chest proudly*",
                inline=False
            )
            embed.set_footer(text="I'm totally a mature and responsible greeter dragon! 🐉")
            
            await member.send(embed=embed)
        except discord.Forbidden:
            # Can't send DM, that's okay
            pass
    
    def _get_public_welcome(self, member):
        """Get a random public welcome message."""
        return DragonPersonality.get_welcome_public().format(mention=member.mention, count=member.guild.member_count)
    
    def _get_private_welcome(self, member):
        """Get a random private welcome message."""
        return DragonPersonality.get_welcome_private().format(name=member.display_name)
    
    @app_commands.command(name="test-welcome", description="🧪 Test the welcome system")
    @admin_only()
    async def test_welcome(self, interaction: discord.Interaction):
        """Test the welcome system with the command user."""
        await interaction.response.send_message("🐉 *adjusts tiny dragon glasses* Testing my VERY professional greeting system...", ephemeral=True)
        await self._welcome_member(interaction.user)
        await interaction.edit_original_response(content="✅ Welcome test completed! *puffs out chest proudly* I totally nailed that! Check the arrivals channel and your DMs.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))