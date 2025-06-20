"""
Channel setup utilities for Ask Nimbus functionality
"""
import discord
from discord.ext import commands

async def setup_ask_nimbus_channel(guild, channel_name="ask-nimbus"):
    """Set up the ask-nimbus channel with proper permissions and welcome message"""
    
    # Check if channel already exists
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if existing_channel:
        return existing_channel
    
    # Create the channel
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            send_messages=True,
            read_messages=True,
            add_reactions=True
        ),
        guild.me: discord.PermissionOverwrite(
            send_messages=True,
            read_messages=True,
            manage_messages=True
        )
    }
    
    channel = await guild.create_text_channel(
        name=channel_name,
        topic="🤖 Ask Nimbus anything about AWS! Get intelligent answers about cloud services, architecture, pricing, and more.",
        overwrites=overwrites
    )
    
    # Send welcome message
    welcome_embed = discord.Embed(
        title="🤖 Welcome to Ask Nimbus!",
        description="*Your intelligent AWS assistant is ready to help...*",
        color=discord.Color.purple()
    )
    
    welcome_embed.add_field(
        name="💡 What I Can Help With",
        value="• Compare AWS services\n• Explain pricing and costs\n• Architecture recommendations\n• Learning paths for beginners\n• Certification guidance\n• Best practices and patterns",
        inline=False
    )
    
    welcome_embed.add_field(
        name="🎯 How to Ask",
        value="Just type your question naturally! Examples:\n• 'What's the difference between S3 and EFS?'\n• 'How much does Lambda cost?'\n• 'Best architecture for a web app?'\n• 'How do I start learning AWS?'",
        inline=False
    )
    
    welcome_embed.add_field(
        name="✨ Smart Features",
        value="• Context-aware responses\n• Conversation memory\n• Service recommendations\n• Learning path suggestions",
        inline=False
    )
    
    welcome_embed.set_footer(text="Powered by Nimbus Oracle • Ask away!")
    
    await channel.send(embed=welcome_embed)
    
    return channel