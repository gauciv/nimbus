"""
Event management cog for the Nimbus Discord bot.
Handles event creation, scheduling, and display.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import re
import asyncio
from datetime import datetime, timedelta
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
        self._task = None  # Store the background task for cleanup

    @app_commands.command(name="create", description="🌟 Inscribe a new gathering in the chronicles of our realm")
    @app_commands.describe(
        title="The title of your gathering",
        date="The appointed date (DD/MM/YYYY)",
        time="The appointed hour (HH:MM AM/PM)",
        description="The mystical purpose of this gathering (optional)"
    )
    @is_core_team()
    async def create(
        self,
        interaction: discord.Interaction,
        title: str,
        date: str,
        time: str,
        description: str = ""
    ):
        """Create a new event announcement with mystical flair."""
        # First, provide helpful examples to the command invoker
        example_embed = discord.Embed(
            title="✨ Event Creation Guidelines",
            description="Here's how to properly format your event details:",
            color=discord.Color.purple()
        )
        example_embed.add_field(
            name="📖 Example",
            value=(
                "**Title:** AWS Lambda Deep Dive Workshop\n"
                "**Date:** 25/06/2025\n"
                "**Time:** 2:30 PM\n"
                "**Description:** Learn the mystical arts of serverless computing with AWS Lambda"
            ),
            inline=False
        )
        example_embed.add_field(
            name="📝 Format Requirements",
            value=(
                "• Date must be in DD/MM/YYYY format\n"
                "• Time must be in HH:MM AM/PM format (12-hour)\n"
                "• Title should be clear and descriptive"
            ),
            inline=False
        )
        await interaction.response.send_message(embed=example_embed, ephemeral=True)

        try:
            # Validate date format
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', date):
                await interaction.followup.send(
                    "🌙 The stars whisper that your date format needs adjustment. Please use DD/MM/YYYY (e.g., 25/06/2025)",
                    ephemeral=True
                )
                return

            # Validate time format
            if not re.match(r'^\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)$', time):
                await interaction.followup.send(
                    "⏳ The sands of time flow in HH:MM AM/PM format (e.g., 2:30 PM). Please adjust your timing accordingly.",
                    ephemeral=True
                )
                return

            # Validate that the date is not in the past
            try:
                event_datetime = datetime.strptime(f"{date} {time}", "%d/%m/%Y %I:%M %p")
                if event_datetime < datetime.now():
                    await interaction.followup.send(
                        "🌟 Even our mystical powers cannot schedule events in the past. Please choose a future date.",
                        ephemeral=True
                    )
                    return
            except ValueError:
                await interaction.followup.send(
                    "🌌 The cosmic forces cannot interpret your date and time. Please check the format and try again.",
                    ephemeral=True
                )
                return

            # Find the announcements channel
            announcements_channel = discord.utils.get(interaction.guild.channels, name='announcements')
            if not announcements_channel:
                await interaction.followup.send(
                    "🌠 The announcements channel seems to be lost in the void. Please ensure it exists.",
                    ephemeral=True
                )
                return

            # Create the event embed with mystical elements
            embed = discord.Embed(
                title=f"✨ New Gathering: {title}",
                description="The stars align for another momentous occasion!",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )

            embed.add_field(
                name="📆 Written in the Stars",
                value=date,
                inline=True
            )
            embed.add_field(
                name="⏰ When the Hour Strikes",
                value=time,
                inline=True
            )
            
            # Add description if provided
            if description:
                embed.add_field(
                    name="📜 Mystical Purpose",
                    value=description,
                    inline=False
                )
            
            embed.add_field(
                name="🔮 Sage of the Gathering",
                value=interaction.user.mention,
                inline=False
            )

            embed.set_footer(text="✨ Mark your presence with 👍 if you plan to join this gathering!")

            # Send the announcement
            event_message = await announcements_channel.send(
                content="@everyone A new gathering has been ordained!",
                embed=embed
            )
            
            # Add attendance reaction
            await event_message.add_reaction("👍")

            # Store the event
            new_event = Event(title, date, time, interaction.user.id, event_message.id, description)
            self.event_manager.add_event(new_event)

            # Send confirmation to the command user
            await interaction.followup.send(
                "✨ Your gathering has been inscribed in the chronicles! Check #announcements to see it.",
                ephemeral=True
            )

        except Exception as e:
            logging.error(f"Error creating event: {e}")
            await interaction.followup.send(
                "🌑 The cosmic forces are disturbed. Your event could not be created.",
                ephemeral=True
            )

    @app_commands.command(name="list", description="✨ Reveal the mystical gatherings for the Council of Elders (list events for Core Team)")
    @is_core_team()
    async def list_events(self, interaction: discord.Interaction):
        """List all events with their numbers for Core Team members."""
        try:
            upcoming_events = self.event_manager.get_upcoming_events()
            
            if not upcoming_events:
                await interaction.response.send_message(
                    "🌌 The cosmic calendar shows no gatherings to manage. (No upcoming events)",
                    ephemeral=True
                )
                return
                
            # Create an embed for the event list
            embed = discord.Embed(
                title="🔮 Mystical Gatherings Registry (Event Management)",
                description="The Oracle reveals the gatherings you may manage:",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            
            # Add each event to the embed with its number
            for i, event in enumerate(upcoming_events, 1):
                event_datetime = event.get_datetime()
                time_until = event_datetime - datetime.now()
                
                embed.add_field(
                    name=f"Gathering #{i}: {event.title}",
                    value=(
                        f"📆 Date: {event.date}\n"
                        f"⏰ Time: {event.time}\n"
                        f"🔢 Event Number: {i} (use this to cancel)\n"
                        f"📜 Description: {event.description or 'None provided'}"
                    ),
                    inline=False
                )
            
            embed.set_footer(text="✨ Use /event cancel <event_number> <reason> to unravel a gathering from the cosmic tapestry")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error listing events: {e}")
            await interaction.response.send_message(
                "🌑 The cosmic forces prevent the Oracle from revealing the gatherings registry. (Error listing events)",
                ephemeral=True
            )
    
    @app_commands.command(name="cancel", description="✨ Unravel a mystical gathering from the cosmic tapestry (cancel an event)")
    @app_commands.describe(
        event_number="The numerical sigil of the gathering to unravel (event number from /event list)",
        reason="The arcane explanation for this unraveling (reason for cancellation)"
    )
    @is_core_team()
    async def cancel(
        self,
        interaction: discord.Interaction,
        event_number: int,
        reason: str
    ):
        """Cancel an event with a reason."""
        try:
            # Get upcoming events
            upcoming_events = self.event_manager.get_upcoming_events()
            
            if not upcoming_events:
                await interaction.response.send_message(
                    "🌌 The cosmic calendar shows no gatherings to unravel. (No events to cancel)",
                    ephemeral=True
                )
                return
                
            # Check if event number is valid
            if event_number < 1 or event_number > len(upcoming_events):
                await interaction.response.send_message(
                    f"🌑 The numerical sigil {event_number} does not correspond to any known gathering. (Invalid event number)",
                    ephemeral=True
                )
                return
                
            # Get the event to cancel
            event_to_cancel = upcoming_events[event_number - 1]
            
            # Find the announcements channel
            announcements_channel = discord.utils.get(interaction.guild.channels, name='announcements')
            if not announcements_channel:
                await interaction.response.send_message(
                    "🌑 The sacred chamber of proclamations cannot be found in this realm. (Missing #announcements channel)",
                    ephemeral=True
                )
                return
                
            # Create cancellation embed
            embed = discord.Embed(
                title=f"🌙 Gathering Unraveled (Event Cancelled): {event_to_cancel.title}",
                description=f"A mystical gathering has been removed from the cosmic tapestry.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📆 Written in the Stars (Date)",
                value=event_to_cancel.date,
                inline=True
            )
            
            embed.add_field(
                name="⏰ When the Hour Would Have Struck (Time)",
                value=event_to_cancel.time,
                inline=True
            )
            
            embed.add_field(
                name="🔮 Arcane Reasoning (Cancellation Reason)",
                value=reason,
                inline=False
            )
            
            embed.add_field(
                name="✨ Decree Issued By (Cancelled By)",
                value=interaction.user.mention,
                inline=False
            )
            
            # Send cancellation announcement
            await announcements_channel.send(
                content="@everyone A gathering has been unraveled from the cosmic tapestry! (Event cancelled)",
                embed=embed
            )
            
            # Try to edit or reply to the original event message
            try:
                original_message = await announcements_channel.fetch_message(event_to_cancel.message_id)
                if original_message:
                    original_embed = original_message.embeds[0]
                    original_embed.title = f"🌙 CANCELLED: {original_embed.title}"
                    original_embed.color = discord.Color.red()
                    original_embed.add_field(
                        name="🔮 Cancellation Reason",
                        value=reason,
                        inline=False
                    )
                    await original_message.edit(embed=original_embed)
            except:
                # If we can't edit the original message, just continue
                pass
                
            # Remove the event
            self.event_manager.remove_event(event_to_cancel)
            
            # Confirm to the command user
            await interaction.response.send_message(
                f"✨ The gathering '{event_to_cancel.title}' has been unraveled from the cosmic tapestry. (Event cancelled successfully)",
                ephemeral=True
            )
            
        except Exception as e:
            logging.error(f"Error cancelling event: {e}")
            await interaction.response.send_message(
                "🌑 The cosmic forces resist your attempt to unravel this gathering. (Error cancelling event)",
                ephemeral=True
            )
    
    @app_commands.command(name="schedule", description="✨ Consult the cosmic calendar of mystical gatherings (view upcoming events)")
    async def schedule(self, interaction: discord.Interaction):
        """Display all upcoming events with mystical flair."""
        try:
            upcoming_events = self.event_manager.get_upcoming_events()
            
            if not upcoming_events:
                await interaction.response.send_message(
                    "🌌 The stars have yet to align for future gatherings. The cosmic calendar remains empty. (No upcoming events)",
                    ephemeral=True
                )
                return
            
            # Create an embed for the schedule
            embed = discord.Embed(
                title="✨ Cosmic Calendar (Upcoming Events)",
                description="The Oracle reveals the mystical gatherings written in the stars:",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            
            # Add each event to the embed
            for i, event in enumerate(upcoming_events, 1):
                event_datetime = event.get_datetime()
                time_until = event_datetime - datetime.now()
                days_until = time_until.days
                
                # Format the time until string with mystical flair
                if days_until > 0:
                    time_str = f"(in {days_until} celestial rotations)"
                else:
                    hours_until = time_until.seconds // 3600
                    if hours_until > 0:
                        time_str = f"(in {hours_until} cosmic hours)"
                    else:
                        minutes_until = (time_until.seconds % 3600) // 60
                        time_str = f"(in {minutes_until} arcane minutes)"
                
                # Get the organizer
                organizer = interaction.guild.get_member(event.organizer_id)
                organizer_name = organizer.display_name if organizer else "Unknown Sage"
                
                # Prepare event details with mystical terms and explanations
                event_details = (
                    f"📆 Written in the Stars (Date): {event.date}\n"
                    f"⏰ When the Hour Strikes (Time): {event.time}\n"
                    f"🔮 Sage of the Gathering (Organizer): {organizer_name}\n"
                    f"⏳ Cosmic Countdown {time_str}"
                )
                
                # Add description if available
                if hasattr(event, 'description') and event.description:
                    event_details += f"\n\n📜 Mystical Purpose (Description): {event.description}"
                
                embed.add_field(
                    name=f"Gathering #{i}: {event.title}",
                    value=event_details,
                    inline=False
                )
            
            # Add footer with instructions for Core Team members
            is_core_team = discord.utils.get(interaction.guild.roles, name="Core Team") in interaction.user.roles
            if is_core_team:
                embed.set_footer(text="✨ Use /event create to inscribe a new gathering or /event cancel to unravel an existing one (Core Team only)")
            else:
                embed.set_footer(text="✨ Use /event create to inscribe a new gathering in the cosmic calendar (Core Team only)")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logging.error(f"Error displaying schedule: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while fetching the schedule.",
                ephemeral=True
            )

    async def check_upcoming_events(self):
        """Background task to check for upcoming events and send reminders."""
        await self.bot.wait_until_ready()  # Ensure bot is ready before starting
        while not self.bot.is_closed():
            try:
                current_time = datetime.now()
                events = self.event_manager.get_all_events()
                
                for event in events:
                    event_datetime = datetime.strptime(f"{event.date} {event.time}", "%d/%m/%Y %I:%M %p")
                    time_until_event = event_datetime - current_time
                    
                    # Remind 24 hours before the event
                    if timedelta(hours=23, minutes=55) <= time_until_event <= timedelta(hours=24, minutes=5):
                        channel = discord.utils.get(self.bot.get_all_channels(), name='announcements')
                        if channel:
                            reminder_embed = discord.Embed(
                                title="🌟 Event Reminder",
                                description=f"The stars remind us of tomorrow's gathering!",
                                color=discord.Color.purple()
                            )
                            reminder_embed.add_field(
                                name="✨ Event",
                                value=event.title,
                                inline=False
                            )
                            reminder_embed.add_field(
                                name="📆 When",
                                value=f"{event.date} at {event.time}",
                                inline=True
                            )
                            
                            # Add description if available
                            if hasattr(event, 'description') and event.description:
                                reminder_embed.add_field(
                                    name="📜 Mystical Purpose",
                                    value=event.description,
                                    inline=False
                                )
                            
                            await channel.send(
                                content="@everyone A mystical gathering approaches!",
                                embed=reminder_embed
                            )
                    
                    # Remove past events
                    if current_time > event_datetime:
                        self.event_manager.remove_event(event)
                
            except Exception as e:
                logging.error(f"Error in event reminder system: {e}")
            
            # Check every 15 minutes
            await asyncio.sleep(900)

    async def cog_load(self) -> None:
        """Start the event reminder system when the cog loads."""
        self._task = asyncio.create_task(self.check_upcoming_events())

    async def cog_unload(self) -> None:
        """Cleanup when the cog is unloaded."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

async def setup(bot: commands.Bot):
    """
    Add the EventCommands cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(EventCommands(bot))