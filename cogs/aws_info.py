"""
AWS information cog for the Nimbus Discord bot.
Provides commands for AWS service information and documentation.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import random
from datetime import datetime
from discord.ext import tasks
from typing import Dict, Any, List

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
    # More services would be defined here...
}

# AWS Documentation Links
AWS_DOCS = {
    # Compute
    "ec2": "https://docs.aws.amazon.com/ec2/",
    "lambda": "https://docs.aws.amazon.com/lambda/",
    "ecs": "https://docs.aws.amazon.com/ecs/",
    # More documentation links would be defined here...
}

# AWS Tips organized by categories
AWS_TIPS = {
    "Cost Optimization": [
        {
            "title": "Use EC2 Reserved Instances",
            "description": "Save up to 75% on EC2 costs by purchasing Reserved Instances for predictable workloads.",
            "learn_more": "https://aws.amazon.com/ec2/pricing/reserved-instances/"
        },
        # More tips would be defined here...
    ],
    # More categories would be defined here...
}

class AWSInfo(commands.Cog):
    """Commands for AWS service information and documentation."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the AWS info cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.tips_channel_name = "aws-tips"
        self.last_category = None  # Track last category to avoid repetition
        self.daily_tip.start()
    
    def cog_unload(self):
        """Clean up when the cog is unloaded."""
        self.daily_tip.cancel()
    
    def get_random_tip(self):
        """
        Get a random tip, avoiding the same category twice in a row.
        
        Returns:
            tuple: (category, tip)
        """
        # Get a random category, different from the last one
        available_categories = [cat for cat in AWS_TIPS.keys() if cat != self.last_category]
        if not available_categories:
            available_categories = list(AWS_TIPS.keys())
        
        category = random.choice(available_categories)
        self.last_category = category
        
        # Get a random tip from the category
        tip = random.choice(AWS_TIPS[category])
        return category, tip
    
    @tasks.loop(hours=24)
    async def daily_tip(self):
        """Send a daily AWS tip to the designated channel."""
        try:
            # Find the tips channel in all guilds
            for guild in self.bot.guilds:
                channel = discord.utils.get(guild.channels, name=self.tips_channel_name)
                
                if channel:
                    # Get a random tip
                    category, tip = self.get_random_tip()
                    
                    # Create the tip embed
                    embed = discord.Embed(
                        title=f"☁️ AWS Cloud Tip of the Day: {tip['title']}",
                        description=tip['description'],
                        color=discord.Color.from_rgb(255, 153, 0)  # AWS Orange
                    )
                    
                    # Add category and learn more link
                    embed.add_field(
                        name="Category",
                        value=f"📚 {category}",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Learn More",
                        value=f"[Click here for documentation]({tip['learn_more']})",
                        inline=True
                    )
                    
                    # Set thumbnail
                    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
                    
                    # Add footer with tip count
                    total_tips = sum(len(tips) for tips in AWS_TIPS.values())
                    embed.set_footer(text=f"Tip {random.randint(1, total_tips)} of {total_tips} • New tip every 24 hours!")
                    
                    await channel.send(embed=embed)
                    logging.info(f"Sent daily AWS tip to {guild.name}")
        
        except Exception as e:
            logging.error(f"Error sending daily tip: {e}")
    
    @daily_tip.before_loop
    async def before_daily_tip(self):
        """Wait until the bot is ready before starting the loop."""
        await self.bot.wait_until_ready()
        
        # Calculate time until next run (9:00 AM UTC)
        now = datetime.utcnow()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run = next_run.replace(day=now.day + 1)
        
        await discord.utils.sleep_until(next_run)
    
    @app_commands.command(name="aws", description="Learn about AWS services")
    @app_commands.describe(
        service_name="The name of the AWS service (e.g., s3, ec2, lambda, rds)"
    )
    async def aws(self, interaction: discord.Interaction, service_name: str):
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
    
    @app_commands.command(name="docs", description="Get official AWS documentation link for a service")
    @app_commands.describe(
        service_name="The name of the AWS service (e.g., s3, lambda, ec2)"
    )
    async def docs(self, interaction: discord.Interaction, service_name: str):
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

async def setup(bot: commands.Bot):
    """
    Add the AWSInfo cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(AWSInfo(bot))