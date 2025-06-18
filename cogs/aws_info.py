"""
AWS information cog for the Nimbus Discord bot.
Provides mystical commands for AWS service information and documentation.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import random
from datetime import datetime
import json
import os
from discord.ext import tasks
from typing import Dict, Any, List, Tuple
from utils.config import load_json_data, save_json_data

# File paths for AWS data
AWS_SERVICES_FILE = 'data/aws_services.json'
AWS_TIPS_FILE = 'data/aws_tips.json'
AWS_DOCS_FILE = 'data/aws_docs.json'
AWS_TIP_STATE_FILE = 'data/aws_tip_state.json'

class AWSInfo(commands.Cog):
    """Mystical commands for AWS service information and documentation."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the AWS info cog with mystical elements.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.tips_channel_name = "aws-tips"
        self.aws_services = self._load_aws_services()
        self.aws_tips = self._load_aws_tips()
        self.aws_docs = self._load_aws_docs()
        self.tip_state = self._load_tip_state()
        self.all_tips = self._flatten_tips()
        self.daily_tip.start()
    
    def _load_aws_services(self) -> Dict[str, Any]:
        """
        Load AWS services from the mystical scrolls.
        
        Returns:
            Dict containing AWS service data
        """
        try:
            return load_json_data(AWS_SERVICES_FILE, {})
        except Exception as e:
            logging.error(f"Error loading AWS services: {e}")
            return {}
    
    def _load_aws_tips(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Load AWS tips from the ancient tomes.
        
        Returns:
            Dict containing AWS tips by category
        """
        try:
            return load_json_data(AWS_TIPS_FILE, {})
        except Exception as e:
            logging.error(f"Error loading AWS tips: {e}")
            return {}
    
    def _load_aws_docs(self) -> Dict[str, str]:
        """
        Load AWS documentation links from the mystical archives.
        
        Returns:
            Dict containing AWS documentation links
        """
        try:
            return load_json_data(AWS_DOCS_FILE, {})
        except Exception as e:
            logging.error(f"Error loading AWS documentation links: {e}")
            return {}
            
    def _load_tip_state(self) -> Dict[str, Any]:
        """
        Load the current tip state from the mystical archives.
        
        Returns:
            Dict containing tip state information
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        default_state = {"current_index": 0, "last_updated": today}
        
        try:
            state = load_json_data(AWS_TIP_STATE_FILE, default_state)
            
            # Validate the date format
            try:
                datetime.strptime(state["last_updated"], "%Y-%m-%d")
            except (ValueError, KeyError):
                # If date is invalid, reset it to today
                state["last_updated"] = today
                
            return state
        except Exception as e:
            logging.error(f"Error loading tip state: {e}")
            return default_state
            
    def _save_tip_state(self) -> bool:
        """
        Save the current tip state to the mystical archives.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return save_json_data(AWS_TIP_STATE_FILE, self.tip_state)
        except Exception as e:
            logging.error(f"Error saving tip state: {e}")
            return False
            
    def _flatten_tips(self) -> List[Tuple[str, Dict[str, str]]]:
        """
        Flatten all tips into a single list with their categories.
        
        Returns:
            List of (category, tip) tuples
        """
        all_tips = []
        for category, tips in self.aws_tips.items():
            for tip in tips:
                all_tips.append((category, tip))
        return all_tips
    
    def cog_unload(self):
        """Release the magical energies when the cog is unloaded."""
        self.daily_tip.cancel()
    
    def get_next_tip(self) -> Tuple[str, Dict[str, str]]:
        """
        Consult the Oracle for the next tip in the monthly cycle.
        Only advances to the next tip if the date has changed.
        
        Returns:
            tuple: (category, tip)
        """
        total_tips = len(self.all_tips)
        if total_tips == 0:
            return "General", {"title": "No tips available", "description": "The Oracle's wisdom is currently veiled.", "learn_more": "https://aws.amazon.com"}
        
        # Get the current index and last updated date from the state
        current_index = self.tip_state.get("current_index", 0)
        last_updated = self.tip_state.get("last_updated", "")
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Only advance the index if it's a new day
        if today != last_updated:
            # Get the tip at the current index
            tip_tuple = self.all_tips[current_index]
            
            # Increment the index for next time, wrapping around if we reach the end
            next_index = (current_index + 1) % total_tips
            
            # Update the state
            self.tip_state["current_index"] = next_index
            self.tip_state["last_updated"] = today
            self._save_tip_state()
            
            return tip_tuple
        else:
            # If it's the same day, return the current tip without advancing
            # We need to use the previous index since current_index has already been incremented
            prev_index = (current_index - 1) if current_index > 0 else (total_tips - 1)
            return self.all_tips[prev_index]
    
    @tasks.loop(hours=24)
    async def daily_tip(self):
        """Channel the Oracle's daily wisdom to the designated ethereal plane."""
        try:
            # Find the tips channel in all guilds
            for guild in self.bot.guilds:
                channel = discord.utils.get(guild.channels, name=self.tips_channel_name)
                
                if channel:
                    # Consult the Oracle for the next wisdom in the cycle
                    category, tip = self.get_next_tip()
                    
                    # Create the mystical tip embed
                    embed = discord.Embed(
                        title=f"✨ Oracle's Cloud Wisdom: {tip['title']}",
                        description=tip['description'],
                        color=discord.Color.purple()  # Mystical purple
                    )
                    
                    # Add category and learn more link
                    embed.add_field(
                        name="🌌 Arcane Domain",
                        value=f"{category}",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="📜 Ancient Scrolls",
                        value=f"[Consult the sacred texts]({tip['learn_more']})",
                        inline=True
                    )
                    
                    # Set thumbnail - mystical crystal ball
                    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
                    
                    # Add mystical footer with tip number
                    total_tips = len(self.all_tips)
                    current_index = self.tip_state.get("current_index", 0)
                    # Calculate the displayed tip index based on whether we advanced today
                    today = datetime.utcnow().strftime("%Y-%m-%d")
                    last_updated = self.tip_state.get("last_updated", "")
                    
                    if today == last_updated:
                        # If we updated today, the displayed tip is the previous index
                        displayed_tip = (current_index - 1) if current_index > 0 else (total_tips - 1)
                    else:
                        # If we haven't updated yet today, the displayed tip is the current index
                        displayed_tip = current_index
                        
                    embed.set_footer(text=f"✨ Wisdom {displayed_tip + 1} of {total_tips} • The Oracle reveals new wisdom with each celestial cycle ✨")
                    
                    await channel.send(embed=embed)
                    logging.info(f"The Oracle has shared wisdom #{displayed_tip + 1} of {total_tips} with {guild.name} on {today}")
        
        except Exception as e:
            logging.error(f"The Oracle's vision was clouded: {e}")
    
    @daily_tip.before_loop
    async def before_daily_tip(self):
        """Align with the cosmic forces before starting the wisdom cycle."""
        await self.bot.wait_until_ready()
        
        # Calculate time until next run (9:00 AM UTC)
        now = datetime.utcnow()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run = next_run.replace(day=now.day + 1)
        
        await discord.utils.sleep_until(next_run)
    
    @app_commands.command(name="aws", description="✨ Consult the Oracle about AWS mystical services")
    @app_commands.describe(
        service_name="The true name of the AWS service (e.g., s3, ec2, lambda, rds)"
    )
    async def aws(self, interaction: discord.Interaction, service_name: str):
        """Reveal the mystical nature of an AWS service."""
        try:
            # Convert to lowercase to make the command case-insensitive
            service_name = service_name.lower()
            
            # Check if the service exists in our mystical tome
            if service_name not in self.aws_services:
                # Seek similar names in the cosmic patterns
                suggestions = []
                for service in self.aws_services.keys():
                    if service_name in service or service in service_name:
                        suggestions.append(service)
                
                suggestion_text = ""
                if suggestions:
                    suggestion_text = f"\n\nPerhaps you seek:\n" + "\n".join(f"• {self.aws_services[s]['mystical_name']} (`{s}`)" for s in suggestions)
                
                await interaction.response.send_message(
                    f"🌌 The name '{service_name}' is not inscribed in our mystical tomes.{suggestion_text}\n\n"
                    "Known services in the AWS constellation:\n" +
                    "\n".join(f"• {self.aws_services[s]['mystical_name']} (`{s}`)" for s in sorted(self.aws_services.keys())),
                    ephemeral=True
                )
                return
            
            # Retrieve the service's mystical properties
            service = self.aws_services[service_name]
            
            # Create an enchanted embed with the service information
            embed = discord.Embed(
                title=f"{service['icon']} {service['mystical_name']}",
                description=f"*{service['name']}*\n\n{service['description']}",
                color=discord.Color.purple()  # Mystical purple
            )
            
            # Add mystical use cases
            embed.add_field(
                name="🔮 Mystical Applications",
                value=service['use_cases'],
                inline=False
            )
            
            # Add arcane learning resources
            # Handle special cases for service URLs
            service_url = service_name
            if service_name == "step-functions":
                service_url = "step-functions"
            elif service_name == "cloudfront":
                service_url = "cloudfront"
            elif service_name == "route53":
                service_url = "route-53"
            elif service_name == "apigateway":
                service_url = "api-gateway"
            
            embed.add_field(
                name="📚 Ancient Scrolls",
                value=(
                    f"• [Sacred Documentation](https://docs.aws.amazon.com/{service_name})\n"
                    f"• [Service Overview](https://aws.amazon.com/{service_url}/)\n"
                    f"• [Initiation Rituals](https://aws.amazon.com/{service_url}/getting-started/)\n"
                    f"• [Mystical Questions](https://aws.amazon.com/{service_url}/faqs/)"
                ),
                inline=False
            )
            
            # Set thumbnail to AWS logo with mystical aura
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
            
            # Add mystical footer
            embed.set_footer(text="✨ The Oracle awaits your questions about other mystical AWS services ✨")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logging.error(f"The Oracle's vision was clouded: {e}")
            await interaction.response.send_message(
                "🌑 A shadow has fallen across the Oracle's vision. Please seek wisdom again later.",
                ephemeral=True
            )
    
    @app_commands.command(name="docs", description="📜 Uncover the sacred AWS documentation scrolls")
    @app_commands.describe(
        service_name="The true name of the AWS service (e.g., s3, lambda, ec2)"
    )
    async def docs(self, interaction: discord.Interaction, service_name: str):
        """Reveal the location of sacred documentation for an AWS service."""
        try:
            # Convert to lowercase to make the command case-insensitive
            service_name = service_name.lower()
            
            # Check if we have a direct path to the sacred texts
            if service_name in self.aws_docs:
                # Get the service's mystical properties
                service_info = self.aws_services.get(service_name, {})
                service_mystical_name = service_info.get('mystical_name', service_name.upper())
                service_full_name = service_info.get('name', service_name.upper())
                
                # Create an enchanted embed with the documentation link
                embed = discord.Embed(
                    title=f"📜 Sacred Texts of {service_mystical_name}",
                    description=f"*{service_full_name}*\n\nThe Oracle reveals the path to ancient knowledge:",
                    color=discord.Color.purple()  # Mystical purple
                )
                
                # Add the main documentation link
                embed.add_field(
                    name="📖 Primary Scrolls",
                    value=f"[Journey to the sacred repository]({self.aws_docs[service_name]})",
                    inline=False
                )
                
                # Add mystical quick links
                embed.add_field(
                    name="⚡ Pathways of Knowledge",
                    value=(
                        f"• [Initiation Rituals]({self.aws_docs[service_name]}latest/dg/getting-started.html)\n"
                        f"• [Sage's Compendium]({self.aws_docs[service_name]}latest/dg/)\n"
                        f"• [Invocation Reference]({self.aws_docs[service_name]}latest/api/)\n"
                        f"• [Command Incantations]({self.aws_docs[service_name]}cli/)"
                    ),
                    inline=False
                )
                
                # Add mystical resources
                embed.add_field(
                    name="🔍 Supplementary Grimoires",
                    value=(
                        f"• [Training of the Adepts](https://aws.amazon.com/training/)\n"
                        f"• [Practical Enchantments](https://workshops.aws/)\n"
                        f"• [Arcane Solutions](https://aws.amazon.com/solutions/)"
                    ),
                    inline=False
                )
                
                # Set thumbnail to AWS logo with mystical aura
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
                
                # Add mystical footer
                embed.set_footer(text="✨ Use /aws to unveil the mystical nature of this service ✨")
                
                await interaction.response.send_message(embed=embed)
                
            else:
                # Seek similar names in the cosmic patterns
                suggestions = []
                for service in self.aws_docs.keys():
                    if service_name in service or service in service_name:
                        suggestions.append(service)
                
                suggestion_text = ""
                if suggestions:
                    suggestion_text = "\n\nPerhaps you seek:\n" + "\n".join(f"• `{s}`" for s in suggestions)
                
                # If no direct match, show available services
                await interaction.response.send_message(
                    f"🌌 The Oracle cannot locate scrolls for '{service_name}'.{suggestion_text}\n\n"
                    "Known scrolls in the mystical archives:\n" +
                    "\n".join(f"• `{s}`" for s in sorted(self.aws_docs.keys())),
                    ephemeral=True
                )
                
        except Exception as e:
            logging.error(f"Error revealing sacred texts: {e}")
            await interaction.response.send_message(
                "🌑 The mystical archives are currently veiled in shadow. Please seek wisdom again later.",
                ephemeral=True
            )

    @app_commands.command(name="setup_services", description="🌌 Create a dedicated channel for AWS services catalog")
    @app_commands.default_permissions(administrator=True)
    async def setup_services(self, interaction: discord.Interaction):
        """Create a dedicated channel for AWS services and populate it with service information."""
        try:
            # Check if user has admin permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "🌑 Only those with administrative powers may invoke this ritual.",
                    ephemeral=True
                )
                return
                
            await interaction.response.defer(ephemeral=True)
            
            # Create the channel if it doesn't exist
            guild = interaction.guild
            existing_channel = discord.utils.get(guild.channels, name="aws-services")
            
            if existing_channel:
                # Clear existing channel
                await existing_channel.purge(limit=100)
                channel = existing_channel
                channel_id = str(existing_channel.id)
            else:
                # Create new channel
                channel = await guild.create_text_channel(
                    name="aws-services",
                    topic="Catalog of AWS services with mystical descriptions",
                    reason="Created by Nimbus bot for AWS services catalog"
                )
                channel_id = str(channel.id)
                
                # Update server config with the new channel ID
                config = load_json_data("data/server_config.json", {})
                if "channels" not in config:
                    config["channels"] = {}
                config["channels"]["aws-services"] = channel_id
                save_json_data("data/server_config.json", config)
            
            # Create categories for services
            categories = {
                "Compute": ["ec2", "lambda", "ecs", "eks", "elasticbeanstalk", "fargate"],
                "Storage": ["s3", "efs"],
                "Database": ["rds", "dynamodb", "aurora", "elasticache"],
                "Networking": ["vpc", "route53", "cloudfront", "directconnect", "transit-gateway"],
                "Security": ["iam", "kms", "secretsmanager", "cognito", "guardduty", "waf", "cloudtrail"],
                "Monitoring": ["cloudwatch"],
                "Messaging": ["sns", "sqs", "eventbridge"],
                "Development": ["codepipeline", "codebuild", "codecommit", "codedeploy"],
                "Analytics": ["athena", "glue", "kinesis", "sagemaker", "redshift"],
                "Infrastructure": ["cloudformation"],
                "Containers": ["eks", "ecs", "fargate", "ecr"],
                "Serverless": ["lambda", "apigateway", "step-functions", "eventbridge"]
            }
            
            # Send introduction message
            intro_embed = discord.Embed(
                title="✨ AWS Services Catalog",
                description="Welcome to the mystical catalog of AWS services. Here you will find all the enchanted tools available in the AWS constellation, organized by their arcane domains.",
                color=discord.Color.purple()
            )
            intro_embed.add_field(
                name="🔮 How to Use",
                value="Browse the categories below to discover AWS services. Use the `/aws <service>` command to learn more about a specific service.",
                inline=False
            )
            intro_embed.set_footer(text="✨ The Oracle's knowledge is vast and ever-expanding ✨")
            await channel.send(embed=intro_embed)
            
            # Create an embed for each category
            for category, service_keys in categories.items():
                # Filter to only include services we have data for
                available_services = [s for s in service_keys if s in self.aws_services]
                if not available_services:
                    continue
                    
                embed = discord.Embed(
                    title=f"✨ {category} Services",
                    color=discord.Color.purple()
                )
                
                for service_key in sorted(available_services):
                    service = self.aws_services[service_key]
                    embed.add_field(
                        name=f"{service['icon']} {service['mystical_name']}",
                        value=f"*{service['name']}*\nInvoke with: `/aws {service_key}`",
                        inline=True
                    )
                
                embed.set_footer(text=f"✨ Use /aws <service> to learn more about a specific service ✨")
                await channel.send(embed=embed)
            
            # Send confirmation to admin
            await interaction.followup.send(
                f"✨ The AWS services catalog has been inscribed in <#{channel_id}>. The mystical knowledge is now available to all seekers.",
                ephemeral=True
            )
                
        except Exception as e:
            logging.error(f"Error setting up services channel: {e}")
            await interaction.followup.send(
                "🌑 The cosmic forces are disturbed. The Oracle could not complete the ritual.",
                ephemeral=True
            )
    
    @app_commands.command(name="refresh_services", description="🌌 Refresh the AWS services catalog")
    @app_commands.default_permissions(administrator=True)
    async def refresh_services(self, interaction: discord.Interaction):
        """Refresh the AWS services channel with updated information."""
        try:
            # Check if user has admin permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "🌑 Only those with administrative powers may invoke this ritual.",
                    ephemeral=True
                )
                return
                
            # Redirect to setup_services which will handle the refresh
            await self.setup_services(interaction)
                
        except Exception as e:
            logging.error(f"Error refreshing services channel: {e}")
            await interaction.response.send_message(
                "🌑 The cosmic forces are disturbed. The Oracle cannot refresh the catalog at this time.",
                ephemeral=True
            )
    
    @app_commands.command(name="services", description="🌌 View the AWS services catalog")
    async def services(self, interaction: discord.Interaction):
        """Direct users to the AWS services channel."""
        try:
            # Get the services channel ID from config
            config = load_json_data("data/server_config.json", {})
            channel_id = config.get("channels", {}).get("aws-services", "")
            
            if channel_id:
                await interaction.response.send_message(
                    f"✨ The catalog of mystical AWS services awaits you in <#{channel_id}>. Journey there to explore the Oracle's knowledge.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "🌑 The services catalog has not yet been established. Ask an administrator to invoke the `/setup_services` ritual.",
                    ephemeral=True
                )
                
        except Exception as e:
            logging.error(f"Error directing to services channel: {e}")
            await interaction.response.send_message(
                "🌑 The cosmic forces are disturbed. The Oracle cannot guide you at this time.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """
    Add the mystical AWSInfo cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(AWSInfo(bot))