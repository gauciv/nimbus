"""
AWS information cog for the Nimbus Discord bot.
Provides mystical commands for AWS service information and documentation.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import random
from datetime import datetime, timedelta
import json
import os
import shutil
from discord.ext import tasks
from typing import Dict, Any, List, Tuple
import utils.permissions
from utils.config import load_json_data, save_json_data
from utils.oracle import log_vision, OracleVision, get_error_message

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
            log_vision(OracleVision.OMEN, f"The Oracle failed to decipher the AWS services scroll", e)
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
            log_vision(OracleVision.OMEN, f"The Oracle's wisdom could not be retrieved from the ancient tomes", e)
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
            log_vision(OracleVision.OMEN, f"The sacred documentation pathways could not be revealed", e)
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
            log_vision(OracleVision.OMEN, f"The Oracle's memory of past wisdom could not be recovered", e)
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
            log_vision(OracleVision.OMEN, f"The Oracle failed to record its wisdom cycle in the cosmic ledger", e)
            return False
            
    def _flatten_tips(self) -> List[Tuple[str, Dict[str, str]]]:
        """
        Flatten all tips into a single list with their categories.
        
        Returns:
            List of (category, tip) tuples
        """
        all_tips = []
        try:
            for category, tips in self.aws_tips.items():
                if isinstance(tips, list):
                    for tip in tips:
                        if isinstance(tip, dict) and 'title' in tip and 'description' in tip and 'learn_more' in tip:
                            all_tips.append((category, tip))
                        else:
                            log_vision(OracleVision.PORTENT, f"Skipping invalid tip in category {category}: {tip}")
                else:
                    log_vision(OracleVision.PORTENT, f"Invalid tips format for category {category}")
            
            if not all_tips:
                log_vision(OracleVision.OMEN, "No valid tips found in aws_tips.json")
        except Exception as e:
            log_vision(OracleVision.OMEN, "Error flattening tips", e)
            
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
        # Ensure we have the latest tips
        if not self.all_tips:
            self.aws_tips = self._load_aws_tips()
            self.all_tips = self._flatten_tips()
            
        total_tips = len(self.all_tips)
        if total_tips == 0:
            log_vision(OracleVision.PORTENT, "No tips available in the system")
            return "General", {"title": "No tips available", "description": "The Oracle's wisdom is currently veiled.", "learn_more": "https://aws.amazon.com"}
        
        try:
            # Get the current index and last updated date from the state
            current_index = self.tip_state.get("current_index", 0)
            
            # Ensure current_index is valid
            if current_index >= total_tips:
                current_index = 0
                self.tip_state["current_index"] = 0
                log_vision(OracleVision.PORTENT, f"Reset current_index from {current_index} to 0 (total tips: {total_tips})")
                
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
                
                log_vision(OracleVision.MURMUR, f"Advanced tip to index {current_index}, next will be {next_index}")
                return tip_tuple
            else:
                # If it's the same day, return the current tip without advancing
                # We need to use the previous index since current_index has already been incremented
                prev_index = (current_index - 1) if current_index > 0 else (total_tips - 1)
                
                # Ensure prev_index is valid
                if prev_index >= total_tips:
                    prev_index = 0
                    
                log_vision(OracleVision.MURMUR, f"Same day, using previous tip at index {prev_index}")
                return self.all_tips[prev_index]
                
        except Exception as e:
            log_vision(OracleVision.OMEN, "Error getting next tip", e)
            return "General", {"title": "Oracle Error", "description": "The Oracle's vision is clouded. Please seek assistance.", "learn_more": "https://aws.amazon.com"}
    
    @tasks.loop(hours=24)
    async def daily_tip(self):
        """Share a random AWS tip daily."""
        try:
            # Reload tips to ensure we have the latest
            self.aws_tips = self._load_aws_tips()
            self.all_tips = self._flatten_tips()
            
            # Check if we have any tips
            if not self.all_tips:
                log_vision(OracleVision.OMEN, "No tips available for daily tip task")
                return
                
            # Find the tips channel in all guilds
            for guild in self.bot.guilds:
                try:
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
                            
                        # Ensure displayed_tip is valid
                        if displayed_tip >= total_tips:
                            displayed_tip = 0
                            
                        embed.set_footer(text=f"✨ Wisdom {displayed_tip + 1} of {total_tips} • The Oracle reveals new wisdom with each celestial cycle ✨")
                        
                        await channel.send(embed=embed)
                        log_vision(OracleVision.MURMUR, f"The Oracle has shared wisdom #{displayed_tip + 1} of {total_tips} with {guild.name} on {today}")
                except Exception as e:
                    log_vision(OracleVision.OMEN, f"Error sending daily tip to guild {guild.name}", e)
        
        except Exception as e:
            log_vision(OracleVision.OMEN, "The Oracle's vision was clouded during daily tip task", e)
    
    @daily_tip.before_loop
    async def before_daily_tip(self):
        """Wait until a specific time to start the daily tip."""
        await self.bot.wait_until_ready()
        
        # Calculate time until next run (9:00 AM UTC)
        now = datetime.utcnow()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run = next_run.replace(day=now.day + 1)
        
        await discord.utils.sleep_until(next_run)
    
    @app_commands.command(name="aws", description="✨ Learn about AWS services (visible only to you)")
    @app_commands.describe(
        service_name="The name of the AWS service (e.g., s3, ec2, lambda, rds)"
    )
    async def aws_service(self, interaction: discord.Interaction, service_name: str):
        """Get information about an AWS service."""
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
                title=f"{service['icon']} {service['name']} - {service['mystical_name']}",
                description=f"{service['description']}",
                color=discord.Color.purple()  # Mystical purple
            )
            
            # Add mystical use cases
            embed.add_field(
                name="🔮 Mystical Applications (Common Use Cases)",
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
                name="📚 Ancient Scrolls (Learning Resources)",
                value=(
                    f"• [Sacred Documentation (Official Docs)](https://docs.aws.amazon.com/{service_name})\n"
                    f"• [Service Overview (Main Page)](https://aws.amazon.com/{service_url}/)\n"
                    f"• [Initiation Rituals (Getting Started)](https://aws.amazon.com/{service_url}/getting-started/)\n"
                    f"• [Mystical Questions (FAQs)](https://aws.amazon.com/{service_url}/faqs/)"
                ),
                inline=False
            )
            
            # Set thumbnail to AWS logo with mystical aura
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
            
            # Add mystical footer
            embed.set_footer(text="✨ The Oracle awaits your questions about other mystical AWS services ✨")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"The Oracle's vision of service {service_name} was obscured", e)
            await interaction.response.send_message(
                get_error_message("general"),
                ephemeral=True
            )
    
    @app_commands.command(name="docs", description="📜 Uncover the sacred AWS documentation scrolls (visible only to you)")
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
                    title=f"📜 Sacred Texts of {service_mystical_name} (Documentation for {service_name})",
                    description=f"*{service_full_name}*\n\nThe Oracle reveals the path to ancient knowledge (official AWS documentation):",
                    color=discord.Color.purple()  # Mystical purple
                )
                
                # Add the main documentation link
                embed.add_field(
                    name="📖 Primary Scrolls (Main Documentation)",
                    value=f"[Journey to the sacred repository (Open Documentation)]({self.aws_docs[service_name]})",
                    inline=False
                )
                
                # Add mystical quick links
                embed.add_field(
                    name="⚡ Pathways of Knowledge (Quick Links)",
                    value=(
                        f"• [Initiation Rituals (Getting Started)]({self.aws_docs[service_name]}latest/dg/getting-started.html)\n"
                        f"• [Sage's Compendium (Developer Guide)]({self.aws_docs[service_name]}latest/dg/)\n"
                        f"• [Invocation Reference (API Reference)]({self.aws_docs[service_name]}latest/api/)\n"
                        f"• [Command Incantations (CLI Reference)]({self.aws_docs[service_name]}cli/)"
                    ),
                    inline=False
                )
                
                # Add mystical resources
                embed.add_field(
                    name="🔍 Supplementary Grimoires (Additional Resources)",
                    value=(
                        f"• [Training of the Adepts (AWS Training)]({self.aws_docs[service_name]}latest/dg/getting-started.html)\n"
                        f"• [Practical Enchantments (AWS Workshops)](https://workshops.aws/)\n"
                        f"• [Arcane Solutions (AWS Solutions)](https://aws.amazon.com/solutions/)"
                    ),
                    inline=False
                )
                
                # Set thumbnail to AWS logo with mystical aura
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
                
                # Add mystical footer
                embed.set_footer(text="✨ Use /aws to learn more about this service's features and use cases ✨")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
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
            log_vision(OracleVision.OMEN, f"Failed to reveal sacred texts for {service_name}", e)
            await interaction.response.send_message(
                get_error_message("docs_not_found"),
                ephemeral=True
            )

    @app_commands.command(name="setup_services", description="🌌 Create a dedicated channel for AWS services catalog")
    @app_commands.describe(
        channel_name="The name for the services catalog channel (default: aws-services)"
    )
    @commands.has_permissions(manage_channels=True)
    async def setup_services(self, interaction: discord.Interaction, channel_name: str = "aws-services"):
        """Create and set up the AWS services catalog channel."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Create the channel if it doesn't exist
            guild = interaction.guild
            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            
            if existing_channel:
                # Clear existing channel
                await existing_channel.purge(limit=100)
                channel = existing_channel
                channel_id = str(existing_channel.id)
            else:
                # Create new channel
                channel = await guild.create_text_channel(
                    name=channel_name,
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
            log_vision(OracleVision.OMEN, f"Failed to establish the services catalog channel", e)
            await interaction.followup.send(
                get_error_message("general"),
                ephemeral=True
            )
    
    @app_commands.command(name="refresh_services", description="🌌 Refresh the AWS services catalog")
    @commands.has_permissions(manage_messages=True)
    async def refresh_services(self, interaction: discord.Interaction):
        """Refresh the AWS services catalog display."""
        try:
            # Find the services channel
            services_channel = discord.utils.get(interaction.guild.channels, name="aws-services")
            if not services_channel:
                services_channel = discord.utils.get(interaction.guild.channels, name="aws_services")
            
            if not services_channel:
                await interaction.response.send_message(
                    "🌑 I could not find the services catalog channel. Please use `/setup_services` first.",
                    ephemeral=True
                )
                return

            # Create the catalog embed
            embed = discord.Embed(
                title="🌌 AWS Services Catalog",
                description="Behold the mystical services of the AWS realm:",
                color=discord.Color.purple()
            )

            # Group services by type/category
            categories = {
                "Storage": ["s3", "efs"],
                "Compute": ["ec2", "lambda", "fargate"],
                "Database": ["dynamodb", "rds", "aurora"],
                "Networking": ["vpc", "cloudfront", "route53"],
                "Security": ["iam", "kms", "guardduty"],
                "Monitoring": ["cloudwatch", "cloudtrail"],
                "Integration": ["sns", "sqs", "eventbridge"],
                "Containers": ["ecs", "eks"],
                "Developer Tools": ["codepipeline", "codebuild", "codecommit"]
            }

            # Add fields for each category
            for category, services in categories.items():
                field_value = ""
                for service_name in services:
                    if service_name in self.aws_services:
                        service = self.aws_services[service_name]
                        field_value += f"{service['icon']} **{service['name']}** - {service['mystical_name']}\n"
                
                if field_value:
                    embed.add_field(
                        name=f"✨ {category}",
                        value=field_value,
                        inline=False
                    )

            # Clear existing messages and send new catalog
            await services_channel.purge()
            await services_channel.send(embed=embed)
            
            await interaction.response.send_message(
                "🌟 The services catalog has been refreshed with new mystical knowledge!",
                ephemeral=True
            )
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to refresh the services catalog", e)
            await interaction.response.send_message(
                get_error_message("general"),
                ephemeral=True
            )
    
    @app_commands.command(name="debug_tips", description="🔍 Debug the AWS tips system (admin only)")
    @utils.permissions.is_admin()
    async def debug_tips(self, interaction: discord.Interaction):
        """Debug the AWS tips system and display current status."""
        try:
            # Get the current tips status
            tips_status = {
                "tips_file_exists": os.path.exists(self.tips_file),
                "total_tips": len(self.aws_tips) if hasattr(self, 'aws_tips') else 0,
                "last_tip_time": self.last_tip_time if hasattr(self, 'last_tip_time') else None,
                "next_tip_scheduled": self.next_tip_time if hasattr(self, 'next_tip_time') else None
            }
            
            # Create debug embed
            embed = discord.Embed(
                title="🔍 AWS Tips System Debug",
                description="Current system status and diagnostics",
                color=discord.Color.blue()
            )
            
            for key, value in tips_status.items():
                embed.add_field(
                    name=key.replace('_', ' ').title(),
                    value=str(value),
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error in debug_tips: {e}")
            await interaction.response.send_message(
                "⚠️ An error occurred while debugging the tips system.",
                ephemeral=True
            )

    @app_commands.command(name="reset_tips", description="🔄 Reset the AWS tips system (admin only)")
    @utils.permissions.is_admin()
    async def reset_tips(self, interaction: discord.Interaction):
        """Reset the AWS tips system to its initial state."""
        try:
            # Reset the tips system
            self.aws_tips = []
            self.last_tip_time = None
            self.next_tip_time = None
            
            # Clear the tips file
            if os.path.exists(self.tips_file):
                os.remove(self.tips_file)
            
            # Reinitialize the tips system
            await self.load_aws_tips()
            
            await interaction.response.send_message(
                "✨ AWS Tips system has been reset successfully!",
                ephemeral=True
            )
            
        except Exception as e:
            logging.error(f"Error in reset_tips: {e}")
            await interaction.response.send_message(
                "⚠️ An error occurred while resetting the tips system.",
                ephemeral=True
            )

    @app_commands.command(name="fix_tips_file", description="🔧 Fix the AWS tips file if corrupted (admin only)")
    @utils.permissions.is_admin()
    async def fix_tips_file(self, interaction: discord.Interaction):
        """Attempt to fix a corrupted AWS tips file."""
        try:
            # First, create a backup of the current file if it exists
            if os.path.exists(self.tips_file):
                backup_file = f"{self.tips_file}.backup"
                shutil.copy2(self.tips_file, backup_file)
                
                # Try to load and validate the tips
                try:
                    with open(self.tips_file, 'r') as f:
                        tips_data = json.load(f)
                    
                    # Validate and clean the tips data
                    valid_tips = []
                    for tip in tips_data:
                        if isinstance(tip, dict) and 'content' in tip:
                            valid_tips.append(tip)
                    
                    # Save the cleaned data
                    with open(self.tips_file, 'w') as f:
                        json.dump(valid_tips, f, indent=2)
                    
                    # Reload the tips system
                    await self.load_aws_tips()
                    
                    await interaction.response.send_message(
                        f"✅ Tips file has been fixed! Found {len(valid_tips)} valid tips.",
                        ephemeral=True
                    )
                    
                except Exception as e:
                    # If fixing failed, restore the backup
                    if os.path.exists(backup_file):
                        shutil.copy2(backup_file, self.tips_file)
                    raise e
                
            else:
                await interaction.response.send_message(
                    "⚠️ No tips file found to fix.",
                    ephemeral=True
                )
                
        except Exception as e:
            logging.error(f"Error in fix_tips_file: {e}")
            await interaction.response.send_message(
                "⚠️ An error occurred while fixing the tips file.",
                ephemeral=True
            )
        
    @app_commands.command(name="reload_tips", description="🔄 Reload AWS tips without resetting state (admin only)")
    @utils.permissions.is_admin()
    async def reload_tips(self, interaction: discord.Interaction):
        """Reload AWS tips without resetting the state."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Save the current state
            current_state = self.tip_state.copy()
            
            # Reload tips
            self.aws_tips = self._load_aws_tips()
            self.all_tips = self._flatten_tips()
            
            # Restore the state
            self.tip_state = current_state
            
            # Validate the current index
            total_tips = len(self.all_tips)
            if total_tips > 0 and self.tip_state.get("current_index", 0) >= total_tips:
                self.tip_state["current_index"] = 0
                self._save_tip_state()
                
            await interaction.followup.send(
                f"✅ AWS tips have been reloaded. Found {total_tips} tips across {len(self.aws_tips)} categories.",
                ephemeral=True
            )
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to reload tips", e)
            await interaction.followup.send(
                f"❌ Error reloading tips: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="trigger_tip", description="🔮 Manually trigger the daily AWS tip (admin only)")
    @utils.permissions.is_admin()
    async def trigger_tip(self, interaction: discord.Interaction):
        """Manually trigger the daily AWS tip."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Reload tips data to ensure we have the latest
            self.aws_tips = self._load_aws_tips()
            self.all_tips = self._flatten_tips()
            
            # Check if we have any tips
            if not self.all_tips:
                await interaction.followup.send(
                    "❌ No tips available. Please check the aws_tips.json file.",
                    ephemeral=True
                )
                return
                
            # Force the tip to advance by setting last_updated to yesterday
            yesterday = (datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - 
                        timedelta(days=1)).strftime("%Y-%m-%d")
            self.tip_state["last_updated"] = yesterday
            self._save_tip_state()
            
            # Get the tips channel
            channel = discord.utils.get(interaction.guild.channels, name=self.tips_channel_name)
            if not channel:
                await interaction.followup.send(
                    f"❌ Tips channel '{self.tips_channel_name}' not found.",
                    ephemeral=True
                )
                return
                
            # Get the next tip
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
            displayed_tip = (current_index - 1) if current_index > 0 else (total_tips - 1)
            
            embed.set_footer(text=f"✨ Wisdom {displayed_tip + 1} of {total_tips} • The Oracle reveals new wisdom with each celestial cycle ✨")
            
            # Send the tip
            await channel.send(embed=embed)
            
            # Confirm to admin
            await interaction.followup.send(
                f"✅ Tip '{tip['title']}' has been sent to #{self.tips_channel_name}.",
                ephemeral=True
            )
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to trigger tip", e)
            await interaction.followup.send(
                f"❌ Error triggering tip: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="debug_tips", description="🔍 Debug the AWS tips system (admin only)")
    @utils.permissions.is_admin()
    async def debug_tips(self, interaction: discord.Interaction):
        """Debug the AWS tips system and provide diagnostic information."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if tips file exists and is valid JSON
            tips_exists = os.path.exists(AWS_TIPS_FILE)
            tips_valid = False
            tips_count = 0
            flattened_tips_count = 0
            
            if tips_exists:
                try:
                    with open(AWS_TIPS_FILE, 'r') as f:
                        tips_data = json.load(f)
                        tips_valid = True
                        tips_count = sum(len(tips) for tips in tips_data.values())
                except json.JSONDecodeError:
                    tips_valid = False
            
            # Check if tip state file exists and is valid JSON
            state_exists = os.path.exists(AWS_TIP_STATE_FILE)
            state_valid = False
            current_index = None
            last_updated = None
            
            if state_exists:
                try:
                    with open(AWS_TIP_STATE_FILE, 'r') as f:
                        state_data = json.load(f)
                        state_valid = True
                        current_index = state_data.get("current_index")
                        last_updated = state_data.get("last_updated")
                except json.JSONDecodeError:
                    state_valid = False
            
            # Check the flattened tips list
            flattened_tips_count = len(self.all_tips)
            
            # Create diagnostic embed
            embed = discord.Embed(
                title="🔍 AWS Tips System Diagnostic",
                description="Diagnostic information about the AWS tips system",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Tips File",
                value=f"Exists: {tips_exists}\nValid JSON: {tips_valid}\nTip Count: {tips_count}",
                inline=False
            )
            
            embed.add_field(
                name="Tip State",
                value=f"Exists: {state_exists}\nValid JSON: {state_valid}\nCurrent Index: {current_index}\nLast Updated: {last_updated}",
                inline=False
            )
            
            embed.add_field(
                name="Flattened Tips",
                value=f"Count: {flattened_tips_count}",
                inline=False
            )
            
            embed.add_field(
                name="Today's Date",
                value=f"{datetime.utcnow().strftime('%Y-%m-%d')}",
                inline=False
            )
            
            # Add a sample tip if available
            if flattened_tips_count > 0 and current_index is not None and current_index < flattened_tips_count:
                category, tip = self.all_tips[current_index]
                embed.add_field(
                    name="Current Tip",
                    value=f"Category: {category}\nTitle: {tip['title']}\nIndex: {current_index}",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to debug tips system", e)
            await interaction.followup.send(
                f"❌ Error debugging tips system: {str(e)}",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """
    Add the mystical AWSInfo cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(AWSInfo(bot))