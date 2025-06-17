# Nimbus Discord Bot v2

A comprehensive Discord bot designed for AWS Cloud Club communities, providing tools for server management, role assignment, event scheduling, AWS information, and community engagement.

## Features

- **Server Management**
  - Automated channel setup
  - Role creation and management
  - Core team administration

- **Member Onboarding**
  - Welcome messages for new members
  - Self-service role assignment
  - Onboarding guides and resources

- **Event Management**
  - Event creation and scheduling
  - Attendance tracking
  - Upcoming events calendar

- **AWS Education**
  - AWS service information
  - Documentation links
  - Daily AWS tips

- **Community Engagement**
  - Announcements
  - Discussion topics
  - Resource sharing

## Installation

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/nimbus-v2.git
   cd nimbus-v2
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Create a configuration file
   ```bash
   cp config.example.json config.json
   ```

4. Edit the configuration file with your Discord bot token
   ```json
   {
     "token": "YOUR_BOT_TOKEN_HERE",
     "guild_id": "YOUR_GUILD_ID_HERE"
   }
   ```

5. Run the bot
   ```bash
   python run_bot.py
   ```

## Project Structure

```
nimbus-v2/
├── bot.py                 # Main bot file
├── run_bot.py             # Debug wrapper for bot startup
├── requirements.txt       # Dependencies
├── config.json            # Bot configuration (create from example)
├── config.example.json    # Example configuration
├── cogs/                  # Command modules
│   ├── __init__.py        # Package definition
│   ├── aws_info.py        # AWS information commands
│   ├── events.py          # Event management commands
│   ├── info.py            # Club information commands
│   ├── role_management.py # Role management commands
│   ├── server_management.py # Server setup commands
│   └── welcome.py         # Welcome and onboarding commands
├── utils/                 # Utility modules
│   ├── __init__.py        # Package definition
│   ├── config.py          # Configuration utilities
│   ├── events.py          # Event management utilities
│   ├── permissions.py     # Permission checking utilities
│   └── roles.py           # Role management utilities
└── data/                  # Data storage
    ├── bot_debug.log      # Debug logs
    ├── events.json        # Event data
    └── role_messages.json # Role message IDs
```

## Commands

### Server Setup
- `/setup` - Set up the server (channels and roles)
- `/setup_channels` - Create and configure all required channels
- `/check_channels` - Check and list required channel setup
- `/setup_core_team` - Create the Core Team role and assign it to a member
- `/manage_core_team` - Add or remove a member from Core Team

### Role Management
- `/setup_roles` - Set up the role selection message

### Member Onboarding
- `/guide` - Receive a DM with the server's onboarding guide
- `/test_welcome` - Test the welcome message without adding a new member

### Event Management
- `/event create` - Create a new event announcement
- `/event schedule` - View all upcoming events

### AWS Information
- `/aws` - Learn about AWS services
- `/docs` - Get official AWS documentation link for a service

### Community Engagement
- `/announce` - Post an announcement in the announcements channel
- `/topic` - Start a discussion topic in the main chat
- `/about` - Learn about the AWS Cloud Club and its officers
- `/links` - Get important AWS Cloud Club links and resources

## Development

### Adding New Commands

To add new commands, create a new cog or extend an existing one:

```python
from discord.ext import commands
from discord import app_commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="mycommand", description="My new command")
    async def my_command(self, interaction):
        await interaction.response.send_message("Hello!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

Then add your cog to the `COGS` list in `bot.py`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.