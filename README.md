# Nimbus Discord Bot v2

A comprehensive Discord bot for AWS Cloud Club communities with a mystical theme.

## Features

- **Server Management**: Setup and configure your Discord server
- **Role Management**: Mystical role assignment system
- **Event Scheduling**: Create and manage community events
- **AWS Information**: Access AWS service information and documentation
- **Welcome System**: Customized welcome messages and onboarding
- **Daily AWS Tips**: Automated daily AWS tips with mystical flair

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Discord Server with admin permissions

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nimbus-v2.git
   cd nimbus-v2
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `config.json` file in the root directory:
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

### Initial Setup Commands

Once the bot is running, use these commands to set up your server:

1. `/setup_roles` - Set up the mystical role selection system
2. `/setup_get_started` - Create a getting started guide
3. `/setup_services` - Create an AWS services catalog

## Configuration Files

- `config.json` - Main bot configuration
- `data/server_config.json` - Server-specific configuration
- `data/role_config.json` - Role system configuration
- `data/aws_services.json` - AWS services information
- `data/aws_tips.json` - Daily AWS tips content
- `data/events.json` - Scheduled events

## Troubleshooting

- Check the `data/bot_debug.log` file for general errors
- Check the `data/oracle_visions.log` file for mystical error messages
- Ensure the bot has proper permissions in your Discord server
- Verify that all JSON configuration files are valid

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.