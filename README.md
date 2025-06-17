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

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `config.json` file with your bot token:
   ```json
   {
     "token": "YOUR_BOT_TOKEN_HERE",
     "guild_id": "YOUR_GUILD_ID_HERE"
   }
   ```
4. Run the bot:
   ```
   python run_bot.py
   ```

## Project Structure

```
nimbus-v2/
├── bot.py                 # Main bot file
├── run_bot.py             # Debug wrapper for bot startup
├── requirements.txt       # Dependencies
├── config.json            # Bot configuration
├── cogs/                  # Command modules
│   ├── aws_info.py        # AWS information commands
│   ├── events.py          # Event management commands
│   ├── info.py            # Club information commands
│   ├── role_management.py # Role management commands
│   ├── server_management.py # Server setup commands
│   └── welcome.py         # Welcome and onboarding commands
├── utils/                 # Utility modules
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.