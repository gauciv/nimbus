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
from discord.ext import tasks
from typing import Dict, Any, List, Tuple
from utils.config import load_json_data

# File paths for AWS data
AWS_SERVICES_FILE = 'data/aws_services.json'
AWS_TIPS_FILE = 'data/aws_tips.json'
AWS_DOCS_FILE = 'data/aws_docs.json'

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
        self.last_tip_index = -1  # Track last tip to avoid repetition
        self.aws_services = self._load_aws_services()
        self.aws_tips = self._load_aws_tips()
        self.aws_docs = self._load_aws_docs()
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
    
    def cog_unload(self):
        """Release the magical energies when the cog is unloaded."""
        self.daily_tip.cancel()
    
    def get_random_tip(self) -> Tuple[str, Dict[str, str]]:
        """
        Consult the Oracle for a random tip, ensuring no repetition.
        
        Returns:
            tuple: (category, tip)
        """
        # Flatten all tips into a single list with their categories
        all_tips = []
        for category, tips in self.aws_tips.items():
            for tip in tips:
                all_tips.append((category, tip))
        
        # Get a random tip, different from the last one
        total_tips = len(all_tips)
        if total_tips == 0:
            return "General", {"title": "No tips available", "description": "The Oracle's wisdom is currently veiled.", "learn_more": "https://aws.amazon.com"}
        
        # Choose a new random index different from the last one
        available_indices = list(range(total_tips))
        if self.last_tip_index in available_indices:
            available_indices.remove(self.last_tip_index)
        
        if not available_indices:  # If we've somehow exhausted all tips
            available_indices = list(range(total_tips))
        
        tip_index = random.choice(available_indices)
        self.last_tip_index = tip_index
        
        return all_tips[tip_index]
    
    @tasks.loop(hours=24)
    async def daily_tip(self):
        """Channel the Oracle's daily wisdom to the designated ethereal plane."""
        try:
            # Find the tips channel in all guilds
            for guild in self.bot.guilds:
                channel = discord.utils.get(guild.channels, name=self.tips_channel_name)
                
                if channel:
                    # Consult the Oracle for wisdom
                    category, tip = self.get_random_tip()
                    
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
                    
                    # Add mystical footer
                    total_tips = sum(len(tips) for tips in self.aws_tips.values())
                    embed.set_footer(text=f"✨ The Oracle reveals new wisdom with each celestial cycle ✨")
                    
                    await channel.send(embed=embed)
                    logging.info(f"The Oracle has shared wisdom with {guild.name}")
        
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
            embed.add_field(
                name="📚 Ancient Scrolls",
                value=(
                    f"• [Sacred Documentation](https://docs.aws.amazon.com/{service_name})\n"
                    f"• [Initiation Rituals](https://aws.amazon.com/{service_name}/getting-started)\n"
                    f"• [Mystical Questions](https://aws.amazon.com/{service_name}/faqs)"
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

    @app_commands.command(name="services", description="🌌 Reveal all services in the AWS constellation")
    async def services(self, interaction: discord.Interaction):
        """Display all available AWS services with their mystical names."""
        try:
            if not self.aws_services:
                await interaction.response.send_message(
                    "🌑 The cosmic catalog is currently veiled in shadow. Please seek wisdom again later.",
                    ephemeral=True
                )
                return
                
            # Create categories for services
            categories = {
                "Compute": ["ec2", "lambda", "ecs", "eks", "elasticbeanstalk"],
                "Storage": ["s3", "efs"],
                "Database": ["rds", "dynamodb"],
                "Networking": ["vpc", "route53", "cloudfront"],
                "Security": ["iam", "kms", "secretsmanager"],
                "Monitoring": ["cloudwatch"],
                "Messaging": ["sns", "sqs"],
                "Development": ["codepipeline", "codebuild", "codecommit", "codedeploy"],
                "Analytics": ["athena", "glue", "kinesis", "sagemaker"],
                "Infrastructure": ["cloudformation"]
            }
            
            # Create an embed for each category
            embeds = []
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
                
                embeds.append(embed)
            
            # Send the first embed and add a note about pagination if needed
            if embeds:
                first_embed = embeds[0]
                first_embed.set_footer(text=f"✨ Page 1/{len(embeds)} • Use /aws <service> to learn more about a specific service ✨")
                await interaction.response.send_message(embed=first_embed)
                
                # Send additional embeds as follow-ups if there are more
                for i, embed in enumerate(embeds[1:], 2):
                    embed.set_footer(text=f"✨ Page {i}/{len(embeds)} • Use /aws <service> to learn more about a specific service ✨")
                    await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(
                    "🌑 The cosmic catalog is currently empty. The Oracle's vision is clouded.",
                    ephemeral=True
                )
                
        except Exception as e:
            logging.error(f"Error revealing service catalog: {e}")
            await interaction.response.send_message(
                "🌑 The cosmic forces are disturbed. The Oracle cannot reveal the service catalog at this time.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """
    Add the mystical AWSInfo cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(AWSInfo(bot))