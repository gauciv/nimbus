"""
Information cog for the Nimbus Discord bot.
Provides commands for displaying information about the club and resources.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.config import load_json_data
from utils.oracle import log_vision, OracleVision, get_error_message

class Info(commands.Cog):
    """Commands for displaying information and resources."""
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the info cog.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.club_info = load_json_data('data/club_info.json', {})
    
    @app_commands.command(name="about", description="✨ Learn about the AWS Cloud Club and its Sages (visible only to you)")
    async def about(self, interaction: discord.Interaction):
        """Display information about the AWS Cloud Club and its leaders."""
        try:
            # Reload club info to ensure we have the latest data
            self.club_info = load_json_data('data/club_info.json', self.club_info)
            
            embed = discord.Embed(
                title=f"✨ {self.club_info.get('name', 'AWS Cloud Club')}",
                description=(
                    f"Welcome, seeker, to the mystical realm of AWS Cloud Club (AWS Student Community)! "
                    f"{self.club_info.get('description', '')}\n\n"
                    f"*This is a student-led community focused on learning and exploring AWS cloud technologies together.*"
                ),
                color=discord.Color.purple()  # Mystical purple
            )

            # Mission Statement
            mission_items = self.club_info.get('mission', [])
            mission_text = "To illuminate the path of cloud wisdom (share AWS knowledge) through:\n"
            mission_text += "\n".join([f"• {item}" for item in mission_items])
            
            embed.add_field(
                name="📜 Our Sacred Mission (Club Goals)",
                value=mission_text,
                inline=False
            )

            # Current Officers
            leaders = self.club_info.get('leadership', [])
            if leaders:
                leaders_text = ""
                for leader in leaders:
                    leaders_text += f"**{leader.get('role', '')}**\n"
                    leaders_text += f"{leader.get('name', '')} - *{leader.get('title', '')}*\n\n"
                leaders_text += "*The Council of Elders is still forming. Join us to shape the future of our mystical order!*"
                
                embed.add_field(
                    name="🔮 Guild Sages (Club Leadership)",
                    value=leaders_text,
                    inline=False
                )

            # Activities and Events
            activities = self.club_info.get('activities', [])
            activities_text = "\n".join([f"• {activity}" for activity in activities])
            
            embed.add_field(
                name="🌟 Our Mystical Practices (Club Activities)",
                value=activities_text,
                inline=False
            )

            # Contact Information
            social_links = self.club_info.get('social_links', {})
            contact_text = "• Join our Discord sanctuary\n"
            
            if social_links.get('instagram'):
                contact_text += f"• [Instagram Scrying Pool]({social_links['instagram']})\n"
            
            if social_links.get('facebook'):
                contact_text += f"• [Facebook Astral Projection]({social_links['facebook']})\n"
            
            embed.add_field(
                name="📫 Commune With Us (Contact Information)",
                value=contact_text,
                inline=False
            )

            # Set footer with meeting info
            meeting = self.club_info.get('meeting_info', {})
            if meeting.get('day') and meeting.get('time') and meeting.get('location'):
                footer_text = f"✨ Gatherings: {meeting['day']} at {meeting['time']} in {meeting['location']} ✨"
            else:
                footer_text = "✨ The stars will reveal our gathering times soon. Stay vigilant for announcements! ✨"
                
            embed.set_footer(text=footer_text)
            
            # AWS Logo with mystical aura
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to reveal club information", e)
            await interaction.response.send_message(
                get_error_message("general"),
                ephemeral=True
            )
    
    @app_commands.command(name="links", description="✨ Discover mystical pathways to AWS Cloud Club resources (visible only to you)")
    async def links(self, interaction: discord.Interaction):
        """Display important links and resources."""
        try:
            # Reload club info to ensure we have the latest data
            self.club_info = load_json_data('data/club_info.json', self.club_info)
            
            embed = discord.Embed(
                title="🔮 Mystical Pathways (Important Links)",
                description="Sacred links (useful resources) to expand your knowledge of the cloud realms (AWS services)!",
                color=discord.Color.purple()  # Mystical purple
            )

            # Social Media Links
            social_links = self.club_info.get('social_links', {})
            social_text = ""
            
            if social_links.get('instagram'):
                social_text += f"• [Instagram Scrying Pool]({social_links['instagram']})\n"
            
            if social_links.get('facebook'):
                social_text += f"• [Facebook Ethereal Plane]({social_links['facebook']})\n"
                
            if social_links.get('discord'):
                social_text += f"• [Discord Sanctuary]({social_links['discord']})\n"
                
            if social_text:
                embed.add_field(
                    name="📱 Astral Projections (Social Media)",
                    value=social_text,
                    inline=False
                )

            # AWS Learning Resources
            embed.add_field(
                name="📚 Tomes of Knowledge (Learning Resources)",
                value=(
                    "• [AWS Skill Builder](https://explore.skillbuilder.aws) - *Path of the Adept* (Free training courses)\n"
                    "• [AWS Documentation](https://docs.aws.amazon.com) - *Sacred Scrolls* (Official documentation)\n"
                    "• [AWS Architecture Center](https://aws.amazon.com/architecture) - *Blueprint of the Cosmos* (Reference architectures)\n"
                    "• [AWS Free Tier](https://aws.amazon.com/free) - *Novice's First Enchantments* (Free AWS services)"
                ),
                inline=False
            )

            # Certification Resources
            embed.add_field(
                name="📜 Paths to Enlightenment (Certification Resources)",
                value=(
                    "• [Certification Portal](https://aws.amazon.com/certification) - *Trials of Mastery* (AWS certification info)\n"
                    "• [Exam Preparation](https://aws.amazon.com/certification/certification-prep) - *Ritual Preparation* (Study materials)\n"
                    "• [Practice Challenges](https://explore.skillbuilder.aws/learn/course/external/view/elearning/9449/aws-certification-official-practice-question-sets-english) - *Training Grounds* (Practice exams)"
                ),
                inline=False
            )

            # AWS Community Resources
            embed.add_field(
                name="🌐 Mystical Communities (AWS Community)",
                value=(
                    "• [AWS Community](https://aws.amazon.com/developer/community/) - *Council of Elders* (Developer community)\n"
                    "• [AWS Events](https://aws.amazon.com/events/) - *Grand Gatherings* (Conferences & webinars)\n"
                    "• [AWS User Groups](https://aws.amazon.com/developer/community/usergroups/) - *Local Covens* (Local meetups)"
                ),
                inline=False
            )

            # Set a footer with update information
            embed.set_footer(text="✨ These mystical pathways were last aligned with the cosmos on the present moon ✨")
            
            # Set the AWS logo as thumbnail with mystical aura
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to reveal mystical pathways", e)
            await interaction.response.send_message(
                get_error_message("general"),
                ephemeral=True
            )
            
    @app_commands.command(name="update_info", description="✨ Update club information (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def update_info(self, interaction: discord.Interaction, field: str, value: str):
        """Update club information (Admin only)."""
        try:
            # Check if user has admin permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    get_error_message("permission"),
                    ephemeral=True
                )
                return
                
            # Reload club info to ensure we have the latest data
            self.club_info = load_json_data('data/club_info.json', {})
            
            # Handle nested fields with dot notation (e.g., "social_links.instagram")
            if "." in field:
                parts = field.split(".")
                if len(parts) == 2 and parts[0] in self.club_info and isinstance(self.club_info[parts[0]], dict):
                    self.club_info[parts[0]][parts[1]] = value
                    from utils.config import save_json_data
                    save_json_data('data/club_info.json', self.club_info)
                    await interaction.response.send_message(
                        f"✨ The cosmic records have been updated. Field `{field}` is now set to `{value}`.",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(
                        f"🌑 The field `{field}` does not exist in the cosmic records.",
                        ephemeral=True
                    )
            # Handle top-level fields
            elif field in self.club_info:
                # Handle special cases for lists
                if field in ["mission", "activities", "leadership"] and isinstance(self.club_info[field], list):
                    await interaction.response.send_message(
                        f"🌑 The field `{field}` is a list and cannot be updated with this command. Please edit the club_info.json file directly.",
                        ephemeral=True
                    )
                else:
                    self.club_info[field] = value
                    from utils.config import save_json_data
                    save_json_data('data/club_info.json', self.club_info)
                    await interaction.response.send_message(
                        f"✨ The cosmic records have been updated. Field `{field}` is now set to `{value}`.",
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    f"🌑 The field `{field}` does not exist in the cosmic records.",
                    ephemeral=True
                )
                
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to update club information field: {field}", e)
            await interaction.response.send_message(
                get_error_message("save_failed"),
                ephemeral=True
            )
    
    @app_commands.command(name="join", description="✨ Learn how to join the AWS Cloud Club (visible only to you)")
    async def join(self, interaction: discord.Interaction):
        """Display information about joining the club."""
        try:
            embed = discord.Embed(
                title="✨ Join Our Mystical Order (Become a Member)",
                description=(
                    "The AWS Cloud Club welcomes all seekers of cloud wisdom (students interested in AWS)! "
                    "Follow these steps to begin your journey with us."
                ),
                color=discord.Color.purple()  # Mystical purple
            )

            # Steps to Join
            embed.add_field(
                name="🔮 The Path to Initiation (Joining Steps)",
                value=(
                    "**1.** Introduce yourself in the <#1384409113181814845> channel (arrivals)\n"
                    "**2.** Select your roles in <#1384476784493334569> (role-assignment)\n"
                    "**3.** Read our sacred rules in <#1384409127966474310> (rules)\n"
                    "**4.** Engage with our community in <#1384049292129337488> (general-chat)\n"
                    "**5.** Attend our mystical gatherings (events announced in <#1384409111797567521>)"
                ),
                inline=False
            )

            # Benefits
            embed.add_field(
                name="✨ Gifts of Membership (Benefits)",
                value=(
                    "• Access to mystical AWS knowledge (learning resources)\n"
                    "• Guidance from experienced cloud sages (mentorship)\n"
                    "• Participation in hands-on enchantments (workshops)\n"
                    "• Connection to the AWS community (networking)\n"
                    "• Preparation for certification quests (exam prep)"
                ),
                inline=False
            )

            # Requirements
            embed.add_field(
                name="📜 Requirements",
                value=(
                    "• Interest in cloud computing and AWS\n"
                    "• Willingness to learn and participate\n"
                    "• Respect for fellow seekers\n"
                    "• No prior experience necessary - all are welcome!"
                ),
                inline=False
            )

            # Contact
            embed.add_field(
                name="📫 Questions?",
                value=(
                    "Reach out to our Guild Sages:\n"
                    "• Mikaela Vianca Molina\n"
                    "• John Vincent Augusto\n\n"
                    "Or ask in the <#1384409143464693812> channel!"
                ),
                inline=False
            )

            # Set footer
            embed.set_footer(text="✨ We look forward to welcoming you into our mystical fellowship! ✨")
            
            # AWS Logo with mystical aura
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            log_vision(OracleVision.OMEN, f"Failed to reveal joining information", e)
            await interaction.response.send_message(
                get_error_message("general"),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """
    Add the Info cog to the bot.
    
    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(Info(bot))