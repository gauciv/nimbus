import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import re
import logging
import json
import os
from typing import List, Dict

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Role configuration
YEAR_ROLES = {
    "1️⃣": "First Year",
    "2️⃣": "Second Year",
    "3️⃣": "Third Year",
    "4️⃣": "Fourth Year",
    "🎓": "Graduate"
}

INTEREST_ROLES = {
    "🌐": "Web Dev",
    "📊": "Data Science",
    "🤖": "AI/ML",
    "📱": "Mobile Dev",
    "🔒": "Cybersecurity"
}

# File to store role message IDs
ROLE_MESSAGE_FILE = 'role_messages.json'

# Load role message IDs from file
role_message_ids = set()
try:
    if os.path.exists(ROLE_MESSAGE_FILE):
        with open(ROLE_MESSAGE_FILE, 'r') as f:
            role_message_ids = set(json.load(f))
except Exception as e:
    logging.error(f"Error loading role messages: {e}")

def save_role_messages():
    """Save role message IDs to file."""
    try:
        with open(ROLE_MESSAGE_FILE, 'w') as f:
            json.dump(list(role_message_ids), f)
    except Exception as e:
        logging.error(f"Error saving role messages: {e}")

# Load configuration
try:
    with open('config.json') as f:
        config = json.load(f)
except FileNotFoundError:
    logging.error("config.json not found!")
    exit(1)
except json.JSONDecodeError:
    logging.error("config.json is not a valid JSON file!")
    exit(1)

def is_core_team():
    """Check if the user has the Core Team role."""
    async def predicate(interaction: discord.Interaction) -> bool:
        core_team_role = discord.utils.get(interaction.guild.roles, name="Core Team")
        if not core_team_role:
            await interaction.response.send_message(
                "❌ Core Team role not found in the server.",
                ephemeral=True
            )
            return False
        return core_team_role in interaction.user.roles
    return app_commands.check(predicate)

# File to store events
EVENTS_FILE = 'events.json'

class Event:
    def __init__(self, title: str, date: str, time: str, organizer_id: int, message_id: int):
        self.title = title
        self.date = date
        self.time = time
        self.organizer_id = organizer_id
        self.message_id = message_id
        
    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'date': self.date,
            'time': self.time,
            'organizer_id': self.organizer_id,
            'message_id': self.message_id
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Event':
        return Event(
            data['title'],
            data['date'],
            data['time'],
            data['organizer_id'],
            data['message_id']
        )
    
    def get_datetime(self) -> datetime:
        """Convert event date and time to datetime object."""
        date_str = f"{self.date} {self.time}"
        try:
            # Try 12-hour format first
            return datetime.strptime(date_str, "%d/%m/%Y %I:%M %p")
        except ValueError:
            # Try 24-hour format
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M")

class EventManager:
    def __init__(self):
        self.events: List[Event] = []
        self.load_events()
    
    def load_events(self):
        """Load events from file."""
        try:
            if os.path.exists(EVENTS_FILE):
                with open(EVENTS_FILE, 'r') as f:
                    data = json.load(f)
                    self.events = [Event.from_dict(event_data) for event_data in data]
                    logging.info(f"Loaded {len(self.events)} events from storage")
        except Exception as e:
            logging.error(f"Error loading events: {e}")
            self.events = []
    
    def save_events(self):
        """Save events to file."""
        try:
            with open(EVENTS_FILE, 'w') as f:
                json.dump([event.to_dict() for event in self.events], f)
        except Exception as e:
            logging.error(f"Error saving events: {e}")
    
    def add_event(self, event: Event):
        """Add a new event and save to file."""
        self.events.append(event)
        self.save_events()
    
    def get_upcoming_events(self) -> List[Event]:
        """Get all upcoming events sorted by date."""
        now = datetime.now()
        upcoming = [
            event for event in self.events
            if event.get_datetime() > now
        ]
        return sorted(upcoming, key=lambda e: e.get_datetime())
    
    def cleanup_past_events(self):
        """Remove events that have already occurred."""
        now = datetime.now()
        original_count = len(self.events)
        self.events = [event for event in self.events if event.get_datetime() > now]
        if len(self.events) < original_count:
            self.save_events()

# Initialize event manager
event_manager = EventManager()

# Create bot instance with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix='!', intents=intents)

def create_role_embed() -> discord.Embed:
    """Create the role selection embed."""
    embed = discord.Embed(
        title="Role Selection",
        description="React with the emojis below to get your roles!",
        color=discord.Color.blue()
    )
    
    # Year level section
    year_description = "\n".join([f"{emoji} - {role}" for emoji, role in YEAR_ROLES.items()])
    embed.add_field(
        name="📚 Year Level",
        value=year_description,
        inline=False
    )
    
    # Interests section
    interests_description = "\n".join([f"{emoji} - {role}" for emoji, role in INTEREST_ROLES.items()])
    embed.add_field(
        name="🎯 Primary Interests",
        value=interests_description,
        inline=False
    )
    
    embed.set_footer(text="Click on a reaction to add/remove the role!")
    return embed

async def ensure_roles_exist(guild: discord.Guild) -> bool:
    """Ensure all configured roles exist in the guild."""
    try:
        # Combine all role names
        all_roles = {**YEAR_ROLES, **INTEREST_ROLES}
        existing_roles = {role.name for role in guild.roles}
        
        # Create missing roles
        for role_name in all_roles.values():
            if role_name not in existing_roles:
                await guild.create_role(
                    name=role_name,
                    mentionable=True,
                    reason="Created by role selection system"
                )
                logging.info(f"Created role: {role_name}")
        
        return True
    except discord.Forbidden:
        logging.error("Bot doesn't have permission to create roles")
        return False
    except Exception as e:
        logging.error(f"Error ensuring roles exist: {e}")
        return False

@bot.event
async def on_ready():
    """Event triggered when the bot is ready and connected to Discord."""
    logging.info(f'Bot is online! Logged in as {bot.user.name} (ID: {bot.user.id})')
    
    # Clean up past events on startup
    event_manager.cleanup_past_events()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logging.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")
    
    logging.info('------')

@bot.event
async def on_member_join(member):
    """Event triggered when a new member joins the server."""
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

@bot.tree.command(name="guide", description="Receive a DM with our server's onboarding guide")
async def guide(interaction: discord.Interaction):
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

@bot.tree.command(name="setup_roles", description="Set up the role selection message (Admin only)")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup_roles(interaction: discord.Interaction):
    """Create the role selection message."""
    try:
        # Check bot permissions first
        permissions = interaction.channel.permissions_for(interaction.guild.me)
        missing_perms = []
        
        if not permissions.manage_roles:
            missing_perms.append("Manage Roles")
        if not permissions.send_messages:
            missing_perms.append("Send Messages")
        if not permissions.add_reactions:
            missing_perms.append("Add Reactions")
        
        if missing_perms:
            await interaction.response.send_message(
                f"❌ I'm missing the following permissions:\n" + 
                "\n".join(f"• {perm}" for perm in missing_perms),
                ephemeral=True
            )
            return
        
        logging.info(f"Setting up roles in channel {interaction.channel.name}")
        
        # First ensure all roles exist
        if not await ensure_roles_exist(interaction.guild):
            await interaction.response.send_message(
                "❌ Failed to set up roles. Please check the bot's permissions.",
                ephemeral=True
            )
            return
        
        # Create and send the embed
        embed = create_role_embed()
        await interaction.response.send_message("Setting up role selection...", ephemeral=True)
        
        try:
            # Send the role message
            role_message = await interaction.channel.send(embed=embed)
            role_message_ids.add(role_message.id)
            
            # Save the role message ID
            save_role_messages()
            
            # Add reactions
            for emoji in [*YEAR_ROLES.keys(), *INTEREST_ROLES.keys()]:
                try:
                    await role_message.add_reaction(emoji)
                except discord.HTTPException as e:
                    logging.error(f"Failed to add reaction {emoji}: {e}")
            
            logging.info(f"Successfully set up role message (ID: {role_message.id})")
            await interaction.edit_original_response(content="✅ Role selection has been set up!")
            
        except discord.Forbidden:
            logging.error("Failed to send role message or add reactions")
            await interaction.edit_original_response(
                content="❌ Failed to set up roles. Please check the bot's permissions."
            )
        
    except discord.Forbidden as e:
        logging.error(f"Permission error setting up roles: {e}")
        await interaction.response.send_message(
            "❌ I don't have permission to set up roles. I need:\n"
            "• Manage Roles permission\n"
            "• Send Messages permission\n"
            "• Add Reactions permission",
            ephemeral=True
        )
    except Exception as e:
        logging.error(f"Error setting up roles: {str(e)}", exc_info=True)
        await interaction.response.send_message(
            "❌ An error occurred while setting up roles.",
            ephemeral=True
        )

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Handle role assignment when a reaction is added."""
    try:
        # Ignore bot's own reactions
        if payload.user_id == bot.user.id:
            return
        
        # Check if this is a role message
        if payload.message_id not in role_message_ids:
            return
        
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            logging.error(f"Could not find guild with ID {payload.guild_id}")
            return
            
        member = guild.get_member(payload.user_id)
        if not member:
            logging.error(f"Could not find member with ID {payload.user_id}")
            return
            
        emoji = str(payload.emoji)
        
        # Check which role to assign
        role_name = YEAR_ROLES.get(emoji) or INTEREST_ROLES.get(emoji)
        if not role_name:
            return
        
        # Find and assign the role
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            try:
                await member.add_roles(role)
                logging.info(f"Assigned role {role_name} to {member}")
            except discord.Forbidden:
                logging.error(f"Failed to assign role {role_name} to {member} - Missing permissions")
            except Exception as e:
                logging.error(f"Error assigning role {role_name} to {member}: {e}")
        else:
            logging.error(f"Could not find role {role_name}")
    except Exception as e:
        logging.error(f"Error in on_raw_reaction_add: {e}", exc_info=True)

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Handle role removal when a reaction is removed."""
    try:
        # Ignore bot's own reactions
        if payload.user_id == bot.user.id:
            return
        
        # Check if this is a role message
        if payload.message_id not in role_message_ids:
            return
        
        guild = bot.get_guild(payload.guild_id)
        if not guild:
            logging.error(f"Could not find guild with ID {payload.guild_id}")
            return
            
        member = guild.get_member(payload.user_id)
        if not member:
            logging.error(f"Could not find member with ID {payload.user_id}")
            return
            
        emoji = str(payload.emoji)
        
        # Check which role to remove
        role_name = YEAR_ROLES.get(emoji) or INTEREST_ROLES.get(emoji)
        if not role_name:
            return
        
        # Find and remove the role
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            try:
                await member.remove_roles(role)
                logging.info(f"Removed role {role_name} from {member}")
            except discord.Forbidden:
                logging.error(f"Failed to remove role {role_name} from {member} - Missing permissions")
            except Exception as e:
                logging.error(f"Error removing role {role_name} from {member}: {e}")
        else:
            logging.error(f"Could not find role {role_name}")
    except Exception as e:
        logging.error(f"Error in on_raw_reaction_remove: {e}", exc_info=True)

@bot.tree.command(name="about", description="Learn about the AWS Cloud Club and its officers")
async def about(interaction: discord.Interaction):
    """Display information about the AWS Cloud Club and its officers."""
    try:
        embed = discord.Embed(
            title="🌟 AWS Cloud Club",
            description=(
                "Welcome to AWS Cloud Club! We're a community of students passionate "
                "about cloud computing and Amazon Web Services technology."
            ),
            color=discord.Color.from_rgb(255, 153, 0)  # AWS Orange
        )

        # Mission Statement
        embed.add_field(
            name="📜 Our Mission",
            value=(
                "To foster learning and collaboration in cloud computing through:\n"
                "• Hands-on AWS projects\n"
                "• Technical workshops\n"
                "• Industry speaker sessions\n"
                "• Certification study groups"
            ),
            inline=False
        )

        # Current Officers
        embed.add_field(
            name="👥 Club Officers",
            value=(
                "**President**\n"
                "Sarah Chen - *AWS Solutions Architect Associate*\n\n"
                "**Vice President**\n"
                "Michael Rodriguez - *AWS Cloud Practitioner*\n\n"
                "**Technical Lead**\n"
                "Alex Kumar - *AWS Developer Associate*\n\n"
                "**Events Coordinator**\n"
                "Emma Thompson - *AWS Cloud Practitioner*"
            ),
            inline=False
        )

        # Activities and Events
        embed.add_field(
            name="🎯 What We Do",
            value=(
                "• Weekly technical workshops\n"
                "• Monthly cloud projects\n"
                "• AWS certification prep\n"
                "• Networking events\n"
                "• Industry tours"
            ),
            inline=False
        )

        # Contact Information
        embed.add_field(
            name="📫 Get in Touch",
            value=(
                "• Join our Discord community\n"
                "• Email: awscloudclub@university.edu\n"
                "• Instagram: @awscloudclub"
            ),
            inline=False
        )

        # Set footer with meeting info
        embed.set_footer(text="Regular meetings every Thursday at 5:00 PM in Tech Center Room 401")
        
        # AWS Logo (you can replace this URL with your club's actual logo)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        logging.error(f"Error in about command: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while fetching club information.",
            ephemeral=True
        )

class EventCommands(app_commands.Group):
    """Event management commands group."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(name="event", description="Event management commands")
        self.bot = bot

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
            event_manager.add_event(new_event)

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
            upcoming_events = event_manager.get_upcoming_events()
            
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
            
            embed.set_footer(text="Use /event to create a new event (Core Team only)")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logging.error(f"Error displaying schedule: {e}")
            await interaction.response.send_message(
                "❌ An error occurred while fetching the schedule.",
                ephemeral=True
            )

@bot.tree.command(name="links", description="Get important AWS Cloud Club links and resources")
async def links(interaction: discord.Interaction):
    """Display important links and resources."""
    try:
        embed = discord.Embed(
            title="🔗 AWS Cloud Club Resources",
            description="All the important links you need to get started!",
            color=discord.Color.from_rgb(255, 153, 0)  # AWS Orange
        )

        # Social Media Links
        embed.add_field(
            name="📱 Social Media",
            value=(
                "• [LinkedIn Group](https://linkedin.com/groups/aws-cloud-club)\n"
                "• [Twitter](https://twitter.com/awscloudclub)\n"
                "• [Instagram](https://instagram.com/awscloudclub)\n"
                "• [YouTube Channel](https://youtube.com/awscloudclub)"
            ),
            inline=False
        )

        # Code & Project Resources
        embed.add_field(
            name="💻 Code & Projects",
            value=(
                "• [GitHub Organization](https://github.com/aws-cloud-club)\n"
                "• [Project Showcase](https://aws-cloud-club.github.io/projects)\n"
                "• [Club Wiki](https://github.com/aws-cloud-club/wiki)"
            ),
            inline=False
        )

        # AWS Learning Resources
        embed.add_field(
            name="📚 AWS Resources",
            value=(
                "• [AWS Skill Builder](https://explore.skillbuilder.aws)\n"
                "• [AWS Documentation](https://docs.aws.amazon.com)\n"
                "• [AWS Solutions Architecture](https://aws.amazon.com/architecture)\n"
                "• [AWS Free Tier](https://aws.amazon.com/free)"
            ),
            inline=False
        )

        # Certification Resources
        embed.add_field(
            name="📜 AWS Certification",
            value=(
                "• [Certification Portal](https://aws.amazon.com/certification)\n"
                "• [Exam Prep](https://aws.amazon.com/certification/certification-prep)\n"
                "• [Practice Exams](https://explore.skillbuilder.aws/learn/course/external/view/elearning/9449/aws-certification-official-practice-question-sets-english)"
            ),
            inline=False
        )

        # Club Resources
        embed.add_field(
            name="🎓 Club Resources",
            value=(
                "• [Meeting Calendar](https://calendar.google.com/calendar/aws-cloud-club)\n"
                "• [Workshop Materials](https://drive.google.com/drive/folders/aws-club-workshops)\n"
                "• [Past Presentations](https://slides.aws-cloud-club.org)"
            ),
            inline=False
        )

        # Contact Information
        embed.add_field(
            name="📫 Contact Us",
            value=(
                "• Email: contact@aws-cloud-club.org\n"
                "• Discord: discord.gg/aws-cloud-club\n"
                "• Office: Tech Center Room 401"
            ),
            inline=False
        )

        # Set a footer with update information
        embed.set_footer(text="Links last updated: June 2025 | Contact an officer if you find any broken links")
        
        # Set the AWS logo as thumbnail
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logging.error(f"Error displaying links: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while fetching the links.",
            ephemeral=True
        )

# AWS Services dictionary with beginner-friendly explanations
AWS_SERVICES = {
    # Storage Services
    "s3": {
        "name": "Simple Storage Service (S3)",
        "description": "A storage service that lets you store unlimited files in the cloud. Think of it as a massive, reliable hard drive in the cloud that you can access from anywhere.",
        "use_cases": "• Website hosting\n• Backup and storage\n• Data lakes\n• App asset storage",
        "icon": "🗄️"
    },
    "efs": {
        "name": "Elastic File System (EFS)",
        "description": "A fully managed file system for use with AWS cloud services and on-premises resources. It's like a network drive that can grow and shrink automatically.",
        "use_cases": "• Shared file storage\n• Container storage\n• Content management\n• Development tools",
        "icon": "📁"
    },
    "fsx": {
        "name": "FSx",
        "description": "Fully managed file storage built on Windows Server and Lustre. Perfect for Windows-based applications and high-performance computing.",
        "use_cases": "• Windows file shares\n• HPC workloads\n• Business applications\n• Media processing",
        "icon": "💾"
    },
    "glacier": {
        "name": "S3 Glacier",
        "description": "Low-cost storage service for data archiving and long-term backup. Like a secure vault for data you don't need to access frequently.",
        "use_cases": "• Data archival\n• Backup retention\n• Digital preservation\n• Compliance storage",
        "icon": "❄️"
    },
    "storage-gateway": {
        "name": "Storage Gateway",
        "description": "Hybrid cloud storage service that gives you on-premises access to virtually unlimited cloud storage.",
        "use_cases": "• Hybrid storage\n• Backup and archive\n• Disaster recovery\n• Cloud migration",
        "icon": "🔄"
    },

    # Compute Services
    "ec2": {
        "name": "Elastic Compute Cloud (EC2)",
        "description": "Virtual servers in the cloud. It's like renting a computer that runs in AWS's data centers. You can choose how powerful you want it to be and only pay for what you use.",
        "use_cases": "• Web servers\n• Application hosting\n• Game servers\n• Development environments",
        "icon": "💻"
    },
    "lambda": {
        "name": "AWS Lambda",
        "description": "Run code without managing servers. You just upload your code and Lambda runs it automatically when needed. You only pay for the time your code actually runs.",
        "use_cases": "• Automated tasks\n• Real-time file processing\n• Backend APIs\n• Scheduled jobs",
        "icon": "⚡"
    },
    "elastic-beanstalk": {
        "name": "Elastic Beanstalk",
        "description": "Easy-to-use service for deploying and scaling web applications. Upload your code and Beanstalk automatically handles deployment, scaling, and monitoring.",
        "use_cases": "• Web applications\n• Developer tools\n• Application hosting\n• Auto-scaling apps",
        "icon": "🌱"
    },
    "ecs": {
        "name": "Elastic Container Service (ECS)",
        "description": "Fully managed container orchestration service. Run, stop, and manage Docker containers on a cluster of virtual machines.",
        "use_cases": "• Microservices\n• Batch processing\n• Application scaling\n• Container workloads",
        "icon": "🐳"
    },
    "eks": {
        "name": "Elastic Kubernetes Service (EKS)",
        "description": "Managed Kubernetes service to run containerized applications. Makes it easy to use Kubernetes without installing and managing your own clusters.",
        "use_cases": "• Container orchestration\n• Microservices\n• Cloud-native apps\n• Hybrid deployments",
        "icon": "⚓"
    },
    "fargate": {
        "name": "AWS Fargate",
        "description": "Serverless compute engine for containers. Run containers without managing servers or clusters.",
        "use_cases": "• Containerized apps\n• Microservices\n• Batch processing\n• Application isolation",
        "icon": "🚀"
    },
    "batch": {
        "name": "AWS Batch",
        "description": "Run batch computing workloads on AWS. Perfect for running many computational tasks in parallel.",
        "use_cases": "• Scientific modeling\n• Financial analysis\n• Video processing\n• Big data analytics",
        "icon": "📊"
    },

    # Database Services
    "rds": {
        "name": "Relational Database Service (RDS)",
        "description": "Managed database service that makes it easy to set up and operate databases in the cloud. AWS handles the tedious database administration tasks for you.",
        "use_cases": "• Web application databases\n• Mobile app backends\n• E-commerce systems\n• User data storage",
        "icon": "🗃️"
    },
    "dynamodb": {
        "name": "DynamoDB",
        "description": "A fast and flexible NoSQL database service. Perfect for applications that need consistent, single-digit millisecond response times at any scale.",
        "use_cases": "• Gaming leaderboards\n• Session management\n• Real-time big data\n• Mobile app data",
        "icon": "⚡"
    },
    "aurora": {
        "name": "Amazon Aurora",
        "description": "MySQL and PostgreSQL-compatible relational database built for the cloud. Up to 5x performance of MySQL and 3x of PostgreSQL.",
        "use_cases": "• Enterprise applications\n• SaaS applications\n• Gaming applications\n• Web services",
        "icon": "✨"
    },
    "elasticache": {
        "name": "ElastiCache",
        "description": "In-memory caching service supporting Redis and Memcached. Speed up applications by retrieving data from fast, managed, in-memory caches.",
        "use_cases": "• Session management\n• Gaming leaderboards\n• Real-time analytics\n• Caching",
        "icon": "⚡"
    },
    "redshift": {
        "name": "Redshift",
        "description": "Fast, fully managed data warehouse that makes it simple and cost-effective to analyze all your data using standard SQL.",
        "use_cases": "• Business intelligence\n• Big data analytics\n• Log analysis\n• Data warehousing",
        "icon": "📊"
    },
    "documentdb": {
        "name": "DocumentDB",
        "description": "MongoDB-compatible database service designed for modern application development with automatic scaling.",
        "use_cases": "• Content management\n• User profiles\n• Catalogs\n• Mobile apps",
        "icon": "📄"
    },
    "neptune": {
        "name": "Neptune",
        "description": "Fully managed graph database service. Build and run applications that work with highly connected datasets.",
        "use_cases": "• Social networks\n• Fraud detection\n• Recommendation engines\n• Knowledge graphs",
        "icon": "🌊"
    },
    "timestream": {
        "name": "Timestream",
        "description": "Fast, scalable, and serverless time series database service for IoT and operational applications.",
        "use_cases": "• IoT applications\n• DevOps monitoring\n• Industrial telemetry\n• Real-time analytics",
        "icon": "⏱️"
    },

    # Machine Learning Services
    "sagemaker": {
        "name": "SageMaker",
        "description": "Fully managed service to build, train, and deploy machine learning models. Makes it easier for developers to use machine learning.",
        "use_cases": "• Predictive analytics\n• Image recognition\n• Natural language processing\n• Fraud detection",
        "icon": "🤖"
    },
    "comprehend": {
        "name": "Comprehend",
        "description": "Natural language processing service that finds meaning and insights in text.",
        "use_cases": "• Sentiment analysis\n• Text analysis\n• Content moderation\n• Document classification",
        "icon": "📝"
    },
    "rekognition": {
        "name": "Rekognition",
        "description": "Add image and video analysis to your applications. Automatically identify objects, people, text, scenes, and activities.",
        "use_cases": "• Face detection\n• Content moderation\n• Media indexing\n• Security monitoring",
        "icon": "👁️"
    },
    "lex": {
        "name": "Lex",
        "description": "Build conversational interfaces into applications using voice and text. The same technology that powers Alexa.",
        "use_cases": "• Chatbots\n• Virtual assistants\n• Info bots\n• Application bots",
        "icon": "🗣️"
    },
    "polly": {
        "name": "Polly",
        "description": "Turn text into lifelike speech. Create applications that talk with dozens of voices in multiple languages.",
        "use_cases": "• Audiobooks\n• E-learning\n• Accessibility\n• Gaming",
        "icon": "🔊"
    },
    "textract": {
        "name": "Textract",
        "description": "Automatically extract text and data from scanned documents. Goes beyond simple optical character recognition (OCR).",
        "use_cases": "• Document processing\n• Form extraction\n• Receipt analysis\n• Contract analysis",
        "icon": "📑"
    },
    "forecast": {
        "name": "Forecast",
        "description": "Use machine learning to deliver highly accurate forecasts. Perfect for business planning and resource allocation.",
        "use_cases": "• Demand forecasting\n• Financial planning\n• Resource planning\n• Inventory management",
        "icon": "📈"
    },

    # Analytics Services
    "athena": {
        "name": "Athena",
        "description": "Query data in S3 using standard SQL. No servers to manage, pay only for the queries you run.",
        "use_cases": "• Log analysis\n• Business reports\n• Data exploration\n• Ad-hoc queries",
        "icon": "🔍"
    },
    "emr": {
        "name": "EMR (Elastic MapReduce)",
        "description": "Cloud big data platform for processing vast amounts of data using open-source tools such as Apache Spark, Hive, and Presto.",
        "use_cases": "• Big data processing\n• Log analysis\n• Data transformations\n• Scientific analysis",
        "icon": "📊"
    },
    "kinesis": {
        "name": "Kinesis",
        "description": "Easily collect, process, and analyze real-time streaming data. Process hundreds of terabytes of data per hour.",
        "use_cases": "• Log streaming\n• Click streams\n• IoT device data\n• Social media feeds",
        "icon": "📡"
    },
    "opensearch": {
        "name": "OpenSearch Service",
        "description": "Search, visualize, and analyze up to petabytes of text and unstructured data. Previously known as Elasticsearch Service.",
        "use_cases": "• Full-text search\n• Log analytics\n• Application monitoring\n• Security analytics",
        "icon": "🔎"
    },
    "quicksight": {
        "name": "QuickSight",
        "description": "Business intelligence service that makes it easy to build visualizations and perform ad-hoc analysis.",
        "use_cases": "• Business analytics\n• Data visualization\n• Dashboards\n• Reports",
        "icon": "📊"
    },
    "glue": {
        "name": "Glue",
        "description": "Fully managed extract, transform, and load (ETL) service that makes it easy to prepare and load data for analysis.",
        "use_cases": "• Data integration\n• Data migration\n• Data preparation\n• ETL workflows",
        "icon": "🔄"
    },

    # Security Services
    "iam": {
        "name": "Identity and Access Management (IAM)",
        "description": "Manage access to AWS services and resources securely. You can create and manage AWS users and groups, and grant or deny their access to resources.",
        "use_cases": "• User management\n• Access control\n• Security policies\n• Permission management",
        "icon": "🔐"
    },
    "cognito": {
        "name": "Cognito",
        "description": "Add user sign-up, sign-in, and access control to web and mobile apps. Scale to millions of users.",
        "use_cases": "• User authentication\n• Social sign-in\n• User management\n• Sync user data",
        "icon": "👤"
    },
    "kms": {
        "name": "Key Management Service (KMS)",
        "description": "Create and manage cryptographic keys and control their use across AWS services and applications.",
        "use_cases": "• Data encryption\n• Key management\n• Digital signing\n• Secure communication",
        "icon": "🔑"
    },
    "shield": {
        "name": "Shield",
        "description": "Managed Distributed Denial of Service (DDoS) protection service that safeguards applications running on AWS.",
        "use_cases": "• DDoS protection\n• Network security\n• Application protection\n• Website security",
        "icon": "🛡️"
    },
    "waf": {
        "name": "Web Application Firewall (WAF)",
        "description": "Protect your web applications from common web exploits that could affect application availability or security.",
        "use_cases": "• Security rules\n• Attack prevention\n• Traffic filtering\n• Access control",
        "icon": "🔒"
    },
    "guardduty": {
        "name": "GuardDuty",
        "description": "Intelligent threat detection service that continuously monitors for malicious activity and unauthorized behavior.",
        "use_cases": "• Threat detection\n• Security monitoring\n• Account protection\n• Network monitoring",
        "icon": "👮"
    },
    "macie": {
        "name": "Macie",
        "description": "Security service that uses machine learning to automatically discover, classify, and protect sensitive data in AWS.",
        "use_cases": "• Data security\n• Privacy compliance\n• Data classification\n• PII detection",
        "icon": "🔍"
    },

    # Networking Services
    "vpc": {
        "name": "Virtual Private Cloud (VPC)",
        "description": "Provision a logically isolated section of the AWS Cloud where you can launch AWS resources in a virtual network.",
        "use_cases": "• Network isolation\n• Security groups\n• Network ACLs\n• Private networks",
        "icon": "🌐"
    },
    "cloudfront": {
        "name": "CloudFront",
        "description": "Content delivery network (CDN) that delivers data, videos, applications, and APIs securely with low latency and high transfer speeds.",
        "use_cases": "• Content delivery\n• Video streaming\n• Software distribution\n• API acceleration",
        "icon": "🌍"
    },
    "route53": {
        "name": "Route 53",
        "description": "Highly available and scalable cloud Domain Name System (DNS) web service.",
        "use_cases": "• Domain registration\n• DNS routing\n• Health checking\n• Traffic management",
        "icon": "🎯"
    },
    "direct-connect": {
        "name": "Direct Connect",
        "description": "Cloud service solution that makes it easy to establish a dedicated network connection from your premises to AWS.",
        "use_cases": "• Hybrid networking\n• Large data transfer\n• Real-time data\n• Consistent network",
        "icon": "🔌"
    },
    "api-gateway": {
        "name": "API Gateway",
        "description": "Create, publish, maintain, monitor, and secure APIs at any scale. The front door for applications to access data or functionality.",
        "use_cases": "• API creation\n• API management\n• Request routing\n• API security",
        "icon": "🚪"
    },

    # Developer Tools
    "codecommit": {
        "name": "CodeCommit",
        "description": "Fully managed source control service that hosts secure Git-based repositories.",
        "use_cases": "• Code hosting\n• Version control\n• Collaboration\n• Code review",
        "icon": "📚"
    },
    "ec2": {
        "name": "Elastic Compute Cloud (EC2)",
        "description": "Virtual servers in the cloud. It's like renting a computer that runs in AWS's data centers. You can choose how powerful you want it to be and only pay for what you use.",
        "use_cases": "• Web servers\n• Application hosting\n• Game servers\n• Development environments",
        "icon": "💻"
    },
    "lambda": {
        "name": "AWS Lambda",
        "description": "Run code without managing servers. You just upload your code and Lambda runs it automatically when needed. You only pay for the time your code actually runs.",
        "use_cases": "• Automated tasks\n• Real-time file processing\n• Backend APIs\n• Scheduled jobs",
        "icon": "⚡"
    },
    "rds": {
        "name": "Relational Database Service (RDS)",
        "description": "Managed database service that makes it easy to set up and operate databases in the cloud. AWS handles the tedious database administration tasks for you.",
        "use_cases": "• Web application databases\n• Mobile app backends\n• E-commerce systems\n• User data storage",
        "icon": "🗃️"
    },
    "dynamodb": {
        "name": "DynamoDB",
        "description": "A fast and flexible NoSQL database service. Perfect for applications that need consistent, single-digit millisecond response times at any scale.",
        "use_cases": "• Gaming leaderboards\n• Session management\n• Real-time big data\n• Mobile app data",
        "icon": "⚡"
    },
    "cloudfront": {
        "name": "CloudFront",
        "description": "Content delivery network (CDN) that delivers data, videos, applications, and APIs securely with low latency and high transfer speeds.",
        "use_cases": "• Website acceleration\n• Video streaming\n• Software distribution\n• API acceleration",
        "icon": "🌐"
    },
    "sns": {
        "name": "Simple Notification Service (SNS)",
        "description": "Fully managed messaging service for both application-to-application (A2A) and application-to-person (A2P) communication.",
        "use_cases": "• Push notifications\n• Email notifications\n• Alert systems\n• Application alerts",
        "icon": "📨"
    },
    "sqs": {
        "name": "Simple Queue Service (SQS)",
        "description": "Fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications.",
        "use_cases": "• Task queues\n• Work distribution\n• Message processing\n• Decoupling systems",
        "icon": "📬"
    },
    "cloudwatch": {
        "name": "CloudWatch",
        "description": "Monitoring service for AWS cloud resources and applications. It collects and tracks metrics, monitors log files, and sets alarms.",
        "use_cases": "• Resource monitoring\n• Application monitoring\n• Log analysis\n• Automated actions",
        "icon": "📊"
    },
    "iam": {
        "name": "Identity and Access Management (IAM)",
        "description": "Manage access to AWS services and resources securely. You can create and manage AWS users and groups, and grant or deny their access to resources.",
        "use_cases": "• User management\n• Access control\n• Security policies\n• Permission management",
        "icon": "🔐"
    },
    "codebuild": {
        "name": "CodeBuild",
        "description": "Fully managed build service that compiles source code, runs tests, and produces software packages that are ready to deploy.",
        "use_cases": "• Continuous integration\n• Build automation\n• Test automation\n• Package creation",
        "icon": "🏗️"
    },
    "codedeploy": {
        "name": "CodeDeploy",
        "description": "Deployment service that automates application deployments to various compute services.",
        "use_cases": "• Application deployment\n• Blue-green deployment\n• Roll back updates\n• Automated deployment",
        "icon": "🚀"
    },
    "codepipeline": {
        "name": "CodePipeline",
        "description": "Continuous delivery service that helps you automate your release pipelines for fast and reliable application updates.",
        "use_cases": "• Release automation\n• Continuous delivery\n• Pipeline management\n• Release orchestration",
        "icon": "🔄"
    },
    "cloud9": {
        "name": "Cloud9",
        "description": "Cloud-based integrated development environment (IDE) that lets you write, run, and debug your code with just a browser.",
        "use_cases": "• Code editing\n• Debugging\n• Collaboration\n• Remote development",
        "icon": "💻"
    },

    # Application Integration
    "sns": {
        "name": "Simple Notification Service (SNS)",
        "description": "Fully managed messaging service for both application-to-application (A2A) and application-to-person (A2P) communication.",
        "use_cases": "• Push notifications\n• Email notifications\n• Alert systems\n• Application alerts",
        "icon": "📨"
    },
    "sqs": {
        "name": "Simple Queue Service (SQS)",
        "description": "Fully managed message queuing service that enables you to decouple and scale microservices, distributed systems, and serverless applications.",
        "use_cases": "• Message queues\n• Work distribution\n• Task decoupling\n• Workload management",
        "icon": "📬"
    },
    "eventbridge": {
        "name": "EventBridge",
        "description": "Serverless event bus that makes it easy to connect applications together using data from your own applications, SaaS applications, and AWS services.",
        "use_cases": "• Event routing\n• Application integration\n• Workflow automation\n• SaaS integration",
        "icon": "🌉"
    },
    "step-functions": {
        "name": "Step Functions",
        "description": "Visual workflow service that helps you coordinate distributed applications and microservices using visual workflows.",
        "use_cases": "• Workflow automation\n• Process orchestration\n• Task coordination\n• Error handling",
        "icon": "📋"
    },
    "mq": {
        "name": "MQ",
        "description": "Managed message broker service for Apache ActiveMQ and RabbitMQ that makes it easy to set up and operate message brokers in the cloud.",
        "use_cases": "• Message brokers\n• Application integration\n• Legacy systems\n• Enterprise messaging",
        "icon": "📮"
    },

    # Management Tools
    "cloudwatch": {
        "name": "CloudWatch",
        "description": "Monitoring service for AWS cloud resources and applications. Collect and track metrics, collect and monitor log files, and set alarms.",
        "use_cases": "• Resource monitoring\n• Application monitoring\n• Log analysis\n• Performance tracking",
        "icon": "📊"
    },
    "cloudformation": {
        "name": "CloudFormation",
        "description": "Create and manage a collection of related AWS resources using templates. Infrastructure as code.",
        "use_cases": "• Infrastructure as code\n• Resource management\n• Stack deployment\n• Environment replication",
        "icon": "📝"
    },
    "config": {
        "name": "Config",
        "description": "Assess, audit, and evaluate the configurations of your AWS resources. Track changes and maintain security compliance.",
        "use_cases": "• Resource tracking\n• Compliance auditing\n• Security analysis\n• Change management",
        "icon": "⚙️"
    },
    "systems-manager": {
        "name": "Systems Manager",
        "description": "Operations hub for your AWS applications and resources. Provides a unified user interface to track and resolve operational issues.",
        "use_cases": "• Resource management\n• Operation automation\n• Application management\n• Patch management",
        "icon": "🎛️"
    },
    "organizations": {
        "name": "Organizations",
        "description": "Policy-based management for multiple AWS accounts. Helps you centrally govern your environment as you grow and scale.",
        "use_cases": "• Account management\n• Policy enforcement\n• Billing consolidation\n• Security policies",
        "icon": "🏢"
    },

    # IoT Services
    "iot-core": {
        "name": "IoT Core",
        "description": "Managed cloud platform that lets connected devices easily and securely interact with cloud applications and other devices.",
        "use_cases": "• Device connectivity\n• Data processing\n• Device management\n• Security rules",
        "icon": "🔌"
    },
    "greengrass": {
        "name": "Greengrass",
        "description": "Bring local compute, messaging, data management, sync, and ML inference capabilities to edge devices.",
        "use_cases": "• Edge computing\n• Local processing\n• Offline operation\n• Device management",
        "icon": "🌱"
    },
    "freertos": {
        "name": "FreeRTOS",
        "description": "Operating system for microcontrollers that makes small, low-power edge devices easy to program, deploy, secure, connect, and manage.",
        "use_cases": "• IoT devices\n• Embedded systems\n• Real-time processing\n• Edge computing",
        "icon": "💡"
    },

    # Game Development
    "gamelift": {
        "name": "GameLift",
        "description": "Managed service for deploying, operating, and scaling dedicated game servers for session-based multiplayer games.",
        "use_cases": "• Game servers\n• Multiplayer hosting\n• Match making\n• Server scaling",
        "icon": "🎮"
    },
    "lumberyard": {
        "name": "Lumberyard",
        "description": "Free cross-platform 3D game engine integrated with AWS and Twitch features for building high-quality games.",
        "use_cases": "• Game development\n• 3D rendering\n• Game networking\n• Cloud integration",
        "icon": "🎲"
    }
}

@bot.tree.command(name="aws", description="Learn about AWS services")
@app_commands.describe(
    service_name="The name of the AWS service (e.g., s3, ec2, lambda, rds)"
)
async def aws(interaction: discord.Interaction, service_name: str):
    """Provide information about an AWS service."""
    try:
        # Convert to lowercase to make the command case-insensitive
        service_name = service_name.lower()
        
        # Check if the service exists in our dictionary
        if service_name not in AWS_SERVICES:
            # Get close matches for typos
            suggestions = []
            for service in AWS_SERVICES.keys():
                if service_name in service or service in service_name:
                    suggestions.append(service)
            
            suggestion_text = ""
            if suggestions:
                suggestion_text = f"\n\nDid you mean:\n" + "\n".join(f"• {AWS_SERVICES[s]['name']} (`{s}`)" for s in suggestions)
            
            await interaction.response.send_message(
                f"❌ Service '{service_name}' not found in the database.{suggestion_text}\n\n"
                "Available services:\n" +
                "\n".join(f"• {AWS_SERVICES[s]['name']} (`{s}`)" for s in sorted(AWS_SERVICES.keys())),
                ephemeral=True
            )
            return
        
        # Get the service info
        service = AWS_SERVICES[service_name]
        
        # Create an embed with the service information
        embed = discord.Embed(
            title=f"{service['icon']} {service['name']}",
            description=service['description'],
            color=discord.Color.from_rgb(255, 153, 0)  # AWS Orange
        )
        
        # Add use cases
        embed.add_field(
            name="📋 Common Use Cases",
            value=service['use_cases'],
            inline=False
        )
        
        # Add learning resources
        embed.add_field(
            name="📚 Learn More",
            value=(
                f"• [Official Documentation](https://docs.aws.amazon.com/{service_name})\n"
                f"• [Getting Started Guide](https://aws.amazon.com/{service_name}/getting-started)\n"
                f"• [FAQ](https://aws.amazon.com/{service_name}/faqs)"
            ),
            inline=False
        )
        
        # Set thumbnail to AWS logo
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
        
        # Add footer with tip
        embed.set_footer(text="💡 Tip: Use /aws with any service name to learn more about other AWS services!")
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        logging.error(f"Error displaying AWS service info: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while fetching the service information.",
            ephemeral=True
        )

# AWS Documentation Links
AWS_DOCS = {
    # Compute
    "ec2": "https://docs.aws.amazon.com/ec2/",
    "lambda": "https://docs.aws.amazon.com/lambda/",
    "ecs": "https://docs.aws.amazon.com/ecs/",
    "eks": "https://docs.aws.amazon.com/eks/",
    "elastic-beanstalk": "https://docs.aws.amazon.com/elastic-beanstalk/",
    "fargate": "https://docs.aws.amazon.com/fargate/",
    
    # Storage
    "s3": "https://docs.aws.amazon.com/s3/",
    "efs": "https://docs.aws.amazon.com/efs/",
    "fsx": "https://docs.aws.amazon.com/fsx/",
    "storage-gateway": "https://docs.aws.amazon.com/storage-gateway/",
    
    # Database
    "rds": "https://docs.aws.amazon.com/rds/",
    "dynamodb": "https://docs.aws.amazon.com/dynamodb/",
    "aurora": "https://docs.aws.amazon.com/aurora/",
    "elasticache": "https://docs.aws.amazon.com/elasticache/",
    "redshift": "https://docs.aws.amazon.com/redshift/",
    "documentdb": "https://docs.aws.amazon.com/documentdb/",
    
    # Networking
    "vpc": "https://docs.aws.amazon.com/vpc/",
    "cloudfront": "https://docs.aws.amazon.com/cloudfront/",
    "route53": "https://docs.aws.amazon.com/route53/",
    "api-gateway": "https://docs.aws.amazon.com/api-gateway/",
    
    # Security
    "iam": "https://docs.aws.amazon.com/iam/",
    "cognito": "https://docs.aws.amazon.com/cognito/",
    "kms": "https://docs.aws.amazon.com/kms/",
    "waf": "https://docs.aws.amazon.com/waf/",
    
    # Analytics
    "athena": "https://docs.aws.amazon.com/athena/",
    "emr": "https://docs.aws.amazon.com/emr/",
    "kinesis": "https://docs.aws.amazon.com/kinesis/",
    "quicksight": "https://docs.aws.amazon.com/quicksight/",
    
    # Machine Learning
    "sagemaker": "https://docs.aws.amazon.com/sagemaker/",
    "comprehend": "https://docs.aws.amazon.com/comprehend/",
    "rekognition": "https://docs.aws.amazon.com/rekognition/",
    "polly": "https://docs.aws.amazon.com/polly/",
    
    # Integration
    "sns": "https://docs.aws.amazon.com/sns/",
    "sqs": "https://docs.aws.amazon.com/sqs/",
    "eventbridge": "https://docs.aws.amazon.com/eventbridge/",
    "step-functions": "https://docs.aws.amazon.com/step-functions/",
    
    # Developer Tools
    "codecommit": "https://docs.aws.amazon.com/codecommit/",
    "codebuild": "https://docs.aws.amazon.com/codebuild/",
    "codedeploy": "https://docs.aws.amazon.com/codedeploy/",
    "codepipeline": "https://docs.aws.amazon.com/codepipeline/",
    
    # Monitoring
    "cloudwatch": "https://docs.aws.amazon.com/cloudwatch/",
    "cloudformation": "https://docs.aws.amazon.com/cloudformation/",
    "systems-manager": "https://docs.aws.amazon.com/systems-manager/"
}

@bot.tree.command(name="docs", description="Get official AWS documentation link for a service")
@app_commands.describe(
    service_name="The name of the AWS service (e.g., s3, lambda, ec2)"
)
async def docs(interaction: discord.Interaction, service_name: str):
    """Provide documentation link for an AWS service."""
    try:
        # Convert to lowercase to make the command case-insensitive
        service_name = service_name.lower()
        
        # Check if we have a direct documentation link
        if service_name in AWS_DOCS:
            # Get the service info from our AWS_SERVICES dictionary
            service_info = AWS_SERVICES.get(service_name, {})
            service_full_name = service_info.get('name', service_name.upper())
            
            # Create an embed with the documentation link
            embed = discord.Embed(
                title=f"📚 {service_full_name} Documentation",
                description="Here's the official AWS documentation for this service:",
                color=discord.Color.from_rgb(255, 153, 0)  # AWS Orange
            )
            
            # Add the main documentation link
            embed.add_field(
                name="📖 Main Documentation",
                value=f"[Click here to view documentation]({AWS_DOCS[service_name]})",
                inline=False
            )
            
            # Add quick links section
            embed.add_field(
                name="⚡ Quick Links",
                value=(
                    f"• [Getting Started]({AWS_DOCS[service_name]}latest/dg/getting-started.html)\n"
                    f"• [Developer Guide]({AWS_DOCS[service_name]}latest/dg/)\n"
                    f"• [API Reference]({AWS_DOCS[service_name]}latest/api/)\n"
                    f"• [CLI Reference]({AWS_DOCS[service_name]}cli/)"
                ),
                inline=False
            )
            
            # Add related resources
            embed.add_field(
                name="🔍 Additional Resources",
                value=(
                    f"• [AWS Training](https://aws.amazon.com/training/)\n"
                    f"• [AWS Workshops](https://workshops.aws/)\n"
                    f"• [AWS Solutions](https://aws.amazon.com/solutions/)"
                ),
                inline=False
            )
            
            # Set thumbnail to AWS logo
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
            
            # Add footer
            embed.set_footer(text="Use /aws to learn more about this service's features and use cases")
            
            await interaction.response.send_message(embed=embed)
            
        else:
            # Try to find similar service names for suggestions
            suggestions = []
            for service in AWS_DOCS.keys():
                if service_name in service or service in service_name:
                    suggestions.append(service)
            
            suggestion_text = ""
            if suggestions:
                suggestion_text = "\n\nDid you mean:\n" + "\n".join(f"• `{s}`" for s in suggestions)
            
            # If no direct match, show available services
            await interaction.response.send_message(
                f"❌ Documentation link not found for '{service_name}'.{suggestion_text}\n\n"
                "Available services:\n" +
                "\n".join(f"• `{s}`" for s in sorted(AWS_DOCS.keys())),
                ephemeral=True
            )
            
    except Exception as e:
        logging.error(f"Error fetching documentation link: {e}")
        await interaction.response.send_message(
            "❌ An error occurred while fetching the documentation link.",
            ephemeral=True
        )

# Run the bot
try:
    bot.run(config['token'])
except KeyError:
    logging.error("Token not found in config.json!")
    exit(1)
except discord.LoginFailure:
    logging.error("Failed to login. Please check if your token is correct!")
    exit(1)
except Exception as e:
    logging.error(f"Error running bot: {e}")
    exit(1)
