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
from utils.config import load_json_data, save_json_data
from utils.oracle import log_vision, OracleVision, get_error_message
from utils.permission_levels import admin_only, everyone

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
        """Load AWS services from the mystical scrolls."""
        try:
            return load_json_data(AWS_SERVICES_FILE, {})
        except Exception as e:
            log_vision(OracleVision.OMEN, f"The Oracle failed to decipher the AWS services scroll", e)
            return {}
    
    def _load_aws_tips(self) -> Dict[str, List[Dict[str, str]]]:
        """Load AWS tips from the ancient tomes."""
        try:
            return load_json_data(AWS_TIPS_FILE, {})
        except Exception as e:
            log_vision(OracleVision.OMEN, f"The Oracle's wisdom could not be retrieved from the ancient tomes", e)
            return {}
    
    def _load_aws_docs(self) -> Dict[str, str]:
        """Load AWS documentation links from the mystical archives."""
        try:
            return load_json_data(AWS_DOCS_FILE, {})
        except Exception as e:
            log_vision(OracleVision.OMEN, f"The sacred documentation pathways could not be revealed", e)
            return {}
            
    def _load_tip_state(self) -> Dict[str, Any]:
        """Load the current tip state from the mystical archives."""
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
        """Save the current tip state to the mystical archives."""
        try:
            return save_json_data(AWS_TIP_STATE_FILE, self.tip_state)
        except Exception as e:
            log_vision(OracleVision.OMEN, f"The Oracle failed to record its wisdom cycle in the cosmic ledger", e)
            return False
            
    def _flatten_tips(self) -> List[Tuple[str, Dict[str, str]]]:
        """Flatten all tips into a single list with their categories."""
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
                        # Get a random tip
                        category, tip = random.choice(self.all_tips)
                        
                        # Create the mystical tip embed
                        embed = discord.Embed(
                            title=f"✨ Oracle's Cloud Wisdom: {tip['title']}",
                            description=tip['description'],
                            color=discord.Color.purple()
                        )
                        
                        embed.add_field(
                            name="🌌 Domain",
                            value=f"{category}",
                            inline=True
                        )
                        
                        embed.add_field(
                            name="📜 Learn More",
                            value=f"[Documentation]({tip['learn_more']})",
                            inline=True
                        )
                        
                        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
                        embed.set_footer(text="✨ Daily AWS wisdom from the Oracle ✨")
                        
                        await channel.send(embed=embed)
                        log_vision(OracleVision.MURMUR, f"Daily tip sent to {guild.name}")
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
    @everyone()
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
                    suggestion_text = f"\\n\\nPerhaps you seek:\\n" + "\\n".join(f"• {self.aws_services[s]['mystical_name']} (`{s}`)" for s in suggestions)
                
                await interaction.response.send_message(
                    f"🌌 The name '{service_name}' is not inscribed in our mystical tomes.{suggestion_text}\\n\\n"
                    "Known services in the AWS constellation:\\n" +
                    "\\n".join(f"• {self.aws_services[s]['mystical_name']} (`{s}`)" for s in sorted(self.aws_services.keys())),
                    ephemeral=True
                )
                return
            
            # Retrieve the service's mystical properties
            service = self.aws_services[service_name]
            
            # Create an enchanted embed with the service information
            embed = discord.Embed(
                title=f"{service['icon']} {service['name']} - {service['mystical_name']}",
                description=f"{service['description']}",
                color=discord.Color.purple()
            )
            
            # Add mystical use cases
            embed.add_field(
                name="🔮 Common Use Cases",
                value=service['use_cases'],
                inline=False
            )
            
            # Add learning resources
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
                name="📚 Learning Resources",
                value=(
                    f"• [Official Documentation](https://docs.aws.amazon.com/{service_name})\\n"
                    f"• [Service Overview](https://aws.amazon.com/{service_url}/)\\n"
                    f"• [Getting Started](https://aws.amazon.com/{service_url}/getting-started/)\\n"
                    f"• [FAQs](https://aws.amazon.com/{service_url}/faqs/)"
                ),
                inline=False
            )
            
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
            embed.set_footer(text="✨ The Oracle awaits your questions about other AWS services ✨")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"The Oracle's vision of service {service_name} was obscured", e)
            await interaction.response.send_message(
                get_error_message("general"),
                ephemeral=True
            )
    
    @app_commands.command(name="docs", description="📜 Get AWS documentation links (visible only to you)")
    @app_commands.describe(
        service_name="The name of the AWS service (e.g., s3, lambda, ec2)"
    )
    @everyone()
    async def docs(self, interaction: discord.Interaction, service_name: str):
        """Get documentation links for an AWS service."""
        try:
            service_name = service_name.lower()
            
            if service_name in self.aws_docs:
                service_info = self.aws_services.get(service_name, {})
                service_mystical_name = service_info.get('mystical_name', service_name.upper())
                service_full_name = service_info.get('name', service_name.upper())
                
                embed = discord.Embed(
                    title=f"📜 Documentation for {service_mystical_name}",
                    description=f"*{service_full_name}*\\n\\nOfficial AWS documentation:",
                    color=discord.Color.purple()
                )
                
                embed.add_field(
                    name="📖 Main Documentation",
                    value=f"[Open Documentation]({self.aws_docs[service_name]})",
                    inline=False
                )
                
                embed.add_field(
                    name="⚡ Quick Links",
                    value=(
                        f"• [Getting Started]({self.aws_docs[service_name]}latest/dg/getting-started.html)\\n"
                        f"• [Developer Guide]({self.aws_docs[service_name]}latest/dg/)\\n"
                        f"• [API Reference]({self.aws_docs[service_name]}latest/api/)\\n"
                        f"• [CLI Reference]({self.aws_docs[service_name]}cli/)"
                    ),
                    inline=False
                )
                
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
                embed.set_footer(text="✨ Use /aws to learn more about this service's features ✨")
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
            else:
                suggestions = []
                for service in self.aws_docs.keys():
                    if service_name in service or service in service_name:
                        suggestions.append(service)
                
                suggestion_text = ""
                if suggestions:
                    suggestion_text = "\\n\\nPerhaps you seek:\\n" + "\\n".join(f"• `{s}`" for s in suggestions)
                
                await interaction.response.send_message(
                    f"🌌 Cannot locate documentation for '{service_name}'.{suggestion_text}\\n\\n"
                    "Available documentation:\\n" +
                    "\\n".join(f"• `{s}`" for s in sorted(self.aws_docs.keys())),
                    ephemeral=True
                )
                
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to get documentation for {service_name}", e)
            await interaction.response.send_message(
                get_error_message("docs_not_found"),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Add the AWSInfo cog to the bot."""
    await bot.add_cog(AWSInfo(bot))