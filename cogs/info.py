"""
Information cog for the Nimbus Discord bot.
Provides commands for displaying information about the club and resources.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging

class Info(commands.Cog):
    """Commands for displaying information and resources."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the info cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
    
    @app_commands.command(name="about", description="Learn about the AWS Cloud Club and its officers")
    async def about(self, interaction: discord.Interaction):
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
    
    @app_commands.command(name="links", description="Get important AWS Cloud Club links and resources")
    async def links(self, interaction: discord.Interaction):
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
                ), inline=False
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

async def setup(bot: commands.Bot):
    """
    Add the Info cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(Info(bot))