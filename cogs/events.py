"""
Event management cog for the Nimbus Discord bot.
Handles event creation, scheduling, and display.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import re
from datetime import datetime
from utils.events import Event, EventManager
from utils.permissions import is_core_team

class EventCommands(commands.GroupCog, name="event"):
    """Event management commands group."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the event commands cog.
        
        Args:
            bot: The Discord bot instance
        """
        super().__init__()
        self.bot = bot
        self.event_manager = EventManager()

    @app_commands.command(name="create", description="Create a new event announcement")
    @app_commands.describe(
        title="The title of the event",
        date="The date of the event (DD/MM/YYYY)",
        time="The time of the event (HH:MM AM/PM)"
    )
    @is_core_team()
    async def create(
        self,
        interaction: discord.Interaction,
        title: str,
        date: str,
        time: str
    ):
        """Create a new event announcement."""
        try:
            # Validate date format
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', date):
                await interaction.response.send_message(
                    "❌ Invalid date format. Please use DD/MM/YYYY (e.g., 25/06/2025)",
                    ephemeral=True
                )
                return

            # Validate time format
            if not re.match(r'^\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)$', time):
                await interaction.response.send_message(
                    "❌ Invalid time format. Please use HH:MM AM/PM (e.g., 2:30 PM)",
                    ephemeral=True
                )
                return

            # Validate that the date is not in the past
            try:
                event_datetime = datetime.strptime(f"{date} {time}", "%d/%m/%Y %I:%M %p")
                if event_datetime < datetime.now():
                    await interaction.response.send_message(
                        "❌ Event date cannot be in the past!",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid date or time format.",
                    ephemeral=True
                )
                return

            # Find the announcements channel
            announcements_channel = discord.utils.get(interaction.guild.channels, name='announcements')
            if not announcements_channel:
                await interaction.response.send_message(
                    "❌ Could not find the #announcements channel.",
                    ephemeral=True
                )
                return

            # Create the event embed
            embed = discord.Embed(
                title=f"📅 New Event: {title}",
                description="A new event has been scheduled!",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            # Add event details
            embed.add_field(
                name="📆 Date",
                value=date,
                inline=True
            )
            embed.add_field(
                name="⏰ Time",
                value=time,
                inline=True
            )
            
            # Add organizer info
            embed.add_field(
                name="👤 Organized by",
                value=interaction.user.mention,
                inline=False
            )

            # Add footer with instructions
            embed.set_footer(text="React with 👍 if you plan to attend!")

            # Send the announcement
            event_message = await announcements_channel.send(
                content="@everyone New event announcement!",
                embed=embed
            )
            
            # Add attendance reaction
            await event_message.add_reaction("👍")

            # Store the event
            new_event = Event(title, date, time, interaction.user.id, event_message.id)
            self.event_manager.add_event(new_event)

            # Send confirmation to the command user
            await interaction.response.send_message(
                "✅ Event has been announced in #announcements!",
                ephemeral=True
            )

        except Exception as e:
            logging.error(f"Error creating event: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while creating the event.",
                ephemeral=True
            )

    @app_commands.command(name="schedule", description="View all upcoming events")
    async def schedule(self, interaction: discord.Interaction):
        """Display all upcoming events."""
        try:
            upcoming_events = self.event_manager.get_upcoming_events()
            
            if not upcoming_events:
                await interaction.response.send_message(
                    "📅 There are no upcoming events scheduled at this time.",
                    ephemeral=True
                )
                return
            
            # Create an embed for the schedule
            embed = discord.Embed(
                title="📅 Upcoming Events",
                description="Here are all upcoming events:",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # Add each event to the embed
            for i, event in enumerate(upcoming_events, 1):
                event_datetime = event.get_datetime()
                time_until = event_datetime - datetime.now()
                days_until = time_until.days
                
                # Format the time until string
                if days_until > 0:
                    time_str = f"(in {days_until} days)"
                else:
                    hours_until = time_until.seconds // 3600
                    if hours_until > 0:
                        time_str = f"(in {hours_until} hours)"
                    else:
                        minutes_until = (time_until.seconds % 3600) // 60
                        time_str = f"(in {minutes_until} minutes)"
                
                # Get the organizer
                organizer = interaction.guild.get_member(event.organizer_id)
                organizer_name = organizer.display_name if organizer else "Unknown"
                
                embed.add_field(
                    name=f"Event #{i}: {event.title}",
                    value=(
                        f"📆 Date: {event.date}\n"
                        f"⏰ Time: {event.time}\n"
                        f"👤 Organizer: {organizer_name}\n"
                        f"⏳ {time_str}"
                    ),
                    inline=False
                )
            
            embed.set_footer(text="Use /event create to create a new event (Core Team only)")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logging.error(f"Error displaying schedule: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while fetching the schedule.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """
    Add the EventCommands cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(EventCommands(bot))