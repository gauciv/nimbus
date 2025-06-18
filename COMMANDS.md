# Nimbus Discord Bot Commands

This document provides a comprehensive list of all commands available in the Nimbus Discord Bot.

## General Commands

| Command | Description | Permissions |
|---------|-------------|------------|
| `/aws <service_name>` | Get information about an AWS service | Everyone |
| `/docs <service_name>` | Get documentation links for an AWS service | Everyone |
| `/services` | View the AWS services catalog | Everyone |

## Admin Commands

| Command | Description | Permissions |
|---------|-------------|------------|
| `/setup_roles` | Set up the mystical role selection system | Admin |
| `/setup_get_started` | Set up the getting started guide | Core Team |
| `/setup_services` | Create a dedicated channel for AWS services catalog | Admin |
| `/refresh_services` | Refresh the AWS services catalog | Admin |
| `/test_welcome` | Test the welcome message | Core Team |

## Event Commands

Events can be scheduled and managed by Core Team members. The bot will automatically send reminders and clean up past events.

## Role System

The bot provides two ways to assign roles:
1. Reaction-based system: Users can react to messages to get roles
2. Button-based system: Users can click buttons to get roles

## AWS Tips

The bot automatically posts daily AWS tips in the `#aws-tips` channel. These tips cover various AWS topics with a mystical theme.

## Customization

Most aspects of the bot can be customized by editing the JSON files in the `data` directory:

- `aws_services.json`: Information about AWS services
- `aws_tips.json`: Daily AWS tips content
- `server_config.json`: Server-specific configuration
- `role_config.json`: Role system configuration

## Troubleshooting

If a command isn't working:
1. Check that the bot has the necessary permissions
2. Verify that the command is being used correctly
3. Check the logs for error messages
4. Ensure all configuration files are properly formatted