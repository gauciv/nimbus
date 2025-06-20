import discord
from discord import app_commands
from discord.ext import commands, tasks
from typing import List, Optional
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
from utils.permission_levels import core_team_only, everyone

class Engagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Store active polls in memory
        self.active_polls = {}
        self._result_messages = {}  # Track result messages for updates
        # Start the task to check for ended polls
        self.check_ended_polls.start()

    def cog_unload(self):
        self.check_ended_polls.cancel()

    def _parse_duration(self, duration_str: str) -> int:
        """Convert duration string to minutes."""
        try:
            # First check if duration is in HH:MM AM/PM format
            try:
                time_obj = datetime.strptime(duration_str, "%I:%M %p")
                now = datetime.now()
                end_time = now.replace(hour=time_obj.hour, minute=time_obj.minute)
                if end_time < now:  # If time is earlier than now, assume next day
                    end_time += timedelta(days=1)
                return int((end_time - now).total_seconds() / 60)
            except ValueError:
                # If not time format, try duration format
                if duration_str.endswith('m'):
                    return int(duration_str[:-1])
                elif duration_str.endswith('h'):
                    return int(duration_str[:-1]) * 60
                elif duration_str.endswith('d'):
                    return int(duration_str[:-1]) * 1440
                elif duration_str.endswith('w'):
                    return int(duration_str[:-1]) * 10080
                else:
                    return int(duration_str)
        except ValueError:
            return 1440  # Default to 24 hours

    @app_commands.command(
        name="poll",
        description="✨ Create an enchanted poll for community decisions"
    )
    @everyone()
    @app_commands.describe(
        question="The mystical question to ask",
        duration='Time to end (e.g., "7:30 PM") or duration (30m, 2h, 1d, 1w). Default: 1d',
        option1="First option",
        option2="Second option",
        option3="Optional third option",
        option4="Optional fourth option",
        allow_multiple="Allow members to vote for multiple options"
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: Optional[str] = None,
        option4: Optional[str] = None,
        duration: str = "1d",
        allow_multiple: bool = False
    ):
        """Create an interactive poll with real-time results"""
        try:
            # Parse duration
            minutes = self._parse_duration(duration)
            if minutes < 5:
                await interaction.response.send_message(
                    "⚠️ Poll duration must be at least 5 minutes!\n"
                    "Format guide:\n"
                    "• Specific time: '7:30 PM'\n"
                    "• Duration: '30m' (minutes), '2h' (hours), '1d' (days), '1w' (weeks)",
                    ephemeral=True
                )
                return
            if minutes > 10080:  # 1 week
                await interaction.response.send_message(
                    "⚠️ Poll duration cannot exceed 1 week!\n"
                    "Format guide:\n"
                    "• Specific time: '7:30 PM'\n"
                    "• Duration: '30m' (minutes), '2h' (hours), '1d' (days), '1w' (weeks)",
                    ephemeral=True
                )
                return

            # Create list of options, filtering out None values
            options = [opt for opt in [option1, option2, option3, option4] if opt is not None]
            
            # Create the poll embed
            embed = discord.Embed(
                title=f"✨ Community Poll: {question}",
                description="Cast your mystical vote below!" + 
                          ("\n*(Multiple choices allowed)*" if allow_multiple else ""),
                color=discord.Color.purple()
            )

            # Add options with numbers
            option_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
            for i, option in enumerate(options):
                embed.add_field(
                    name=f"Option {option_emojis[i]}",
                    value=option,
                    inline=False
                )

            # Add participation info
            end_time = datetime.utcnow() + timedelta(minutes=minutes)
            embed.add_field(
                name="🎭 How to Vote",
                value="React with the numbers below to cast your vote!" +
                      ("\nYou can vote for multiple options!" if allow_multiple else ""),
                inline=False
            )
            
            embed.add_field(
                name="⏳ Poll Duration",
                value=(
                    f"**Ends:** {discord.utils.format_dt(end_time)}\n"
                    f"**Time Remaining:** {discord.utils.format_dt(end_time, style='R')}"
                ),
                inline=False
            )

            # Store poll data
            message = await interaction.channel.send(embed=embed)
            self.active_polls[message.id] = {
                "question": question,
                "options": options,
                "emojis": option_emojis[:len(options)],
                "end_time": end_time,
                "author_id": interaction.user.id,
                "channel_id": interaction.channel.id,
                "allow_multiple": allow_multiple,
                "total_voters": set()
            }

            # Add reaction options
            for i in range(len(options)):
                await message.add_reaction(option_emojis[i])

            await interaction.response.send_message(
                "✨ Your mystical poll has been created!",
                ephemeral=True
            )

        except Exception as e:
            logging.error(f"Error creating poll: {e}")
            await interaction.response.send_message(
                "⚠️ An error occurred while creating the poll. Please try again.",
                ephemeral=True
            )

    @app_commands.command(
        name="spotlight",
        description="✨ Celebrate a member's achievements and contributions"
    )
    @core_team_only()
    @app_commands.describe(
        member="The community member to spotlight",
        achievement="Their notable achievement or contribution",
        project_url="Optional link to their project or work",
        category="Category of achievement",
        impact="How this benefits the community"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="Project Launch 🚀", value="project"),
        app_commands.Choice(name="Certification Achievement 📜", value="certification"),
        app_commands.Choice(name="Community Contribution ❤️", value="contribution"),
        app_commands.Choice(name="Technical Article 📝", value="article"),
        app_commands.Choice(name="Cloud Innovation 💡", value="innovation")
    ])
    async def spotlight(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        achievement: str,
        category: str,
        impact: str,
        project_url: Optional[str] = None
    ):
        """Create an engaging spotlight showcase for a community member"""
        try:
            # Category-specific emojis and colors
            category_info = {
                "project": {"emoji": "🚀", "color": discord.Color.blue()},
                "certification": {"emoji": "📜", "color": discord.Color.green()},
                "contribution": {"emoji": "❤️", "color": discord.Color.red()},
                "article": {"emoji": "📝", "color": discord.Color.purple()},
                "innovation": {"emoji": "💡", "color": discord.Color.gold()}
            }

            # Create the spotlight embed
            embed = discord.Embed(
                title=f"{category_info[category]['emoji']} Member Spotlight: {member.display_name}",
                color=category_info[category]['color']
            )

            # Add member avatar
            embed.set_thumbnail(url=member.display_avatar.url)

            # Add achievement details with fancy formatting
            embed.add_field(
                name="✨ Achievement",
                value=achievement,
                inline=False
            )

            # Add category-specific section
            category_titles = {
                "project": "🛠️ Project Details",
                "certification": "🎓 Certification Details",
                "contribution": "🤝 Contribution Impact",
                "article": "📚 Article Overview",
                "innovation": "💫 Innovation Highlights"
            }
            
            embed.add_field(
                name=category_titles[category],
                value=impact,
                inline=False
            )

            # Add project URL if provided
            if project_url:
                embed.add_field(
                    name="🔗 Learn More",
                    value=f"[Check it out here]({project_url})",
                    inline=False
                )

            # Add member stats
            member_since = discord.utils.format_dt(member.joined_at, style='D')
            embed.add_field(
                name="🌟 Community Member Since",
                value=member_since,
                inline=True
            )

            # Add roles (excluding @everyone)
            roles = [role.mention for role in member.roles if role.name != "@everyone"]
            if roles:
                embed.add_field(
                    name="✨ Roles & Expertise",
                    value=" ".join(roles[-3:]) + f"\n*...and {len(roles)-3} more*" if len(roles) > 3 else " ".join(roles),
                    inline=True
                )

            # Add footer
            embed.set_footer(
                text=f"Spotlighted by {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )

            # Respond to interaction first to avoid timeout
            await interaction.response.send_message(
                f"✨ Creating spotlight for {member.display_name}...",
                ephemeral=True
            )

            # Send the spotlight message with celebration
            message = await interaction.channel.send(
                f"🌟 **Let's celebrate our amazing community member!** 🌟\n{member.mention}",
                embed=embed
            )

            # Add celebratory reactions
            celebration_reactions = ["🌟", "👏", "🎉", "💫", "🙌"]
            for reaction in celebration_reactions:
                await message.add_reaction(reaction)

            # Update the response
            await interaction.edit_original_response(
                content=f"✨ Spotlight created for {member.display_name}!"
            )

        except Exception as e:
            logging.error(f"Error creating spotlight: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "⚠️ An error occurred while creating the spotlight. Please try again.",
                    ephemeral=True
                )
            else:
                await interaction.edit_original_response(
                    content="⚠️ An error occurred while creating the spotlight. Please try again."
                )

    async def _create_poll_results(self, poll_data: dict, results: list, total_votes: int) -> discord.Embed:
        """Create an engaging poll results embed."""
        embed = discord.Embed(
            title=f"✨ Poll Results: {poll_data['question']}",
            description="The community has spoken! Here are the final results:",
            color=discord.Color.purple()
        )

        # Add fancy progress bars and stats for each option
        for option, votes in results:
            percentage = (votes / total_votes * 100) if total_votes > 0 else 0
            bar_length = int(percentage / 5)  # 20 characters total
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            embed.add_field(
                name=option,
                value=(
                    f"```\n{bar} {percentage:.1f}%\n"
                    f"Votes: {votes}```"
                ),
                inline=False
            )

        # Add participation stats
        embed.add_field(
            name="📊 Poll Statistics",
            value=(
                f"**Total Votes:** {total_votes}\n"
                f"**Unique Voters:** {len(poll_data['total_voters'])}\n"
                f"**Options:** {len(poll_data['options'])}\n"
                f"**Type:** {'Multiple Choice' if poll_data['allow_multiple'] else 'Single Choice'}"
            ),
            inline=False
        )

        # Add footer with poll metadata
        author = self.bot.get_user(poll_data['author_id'])
        author_name = author.display_name if author else "Unknown"
        embed.set_footer(
            text=f"Poll created by {author_name} • Final results",
            icon_url=author.display_avatar.url if author else None
        )

        return embed

    async def _update_poll_results(self, message_id: int):
        """Update poll results in real-time."""
        try:
            poll_data = self.active_polls[message_id]
            channel = self.bot.get_channel(poll_data["channel_id"])
            message = await channel.fetch_message(message_id)

            # Count reactions
            results = []
            total_votes = 0
            unique_voters = set()

            for i, emoji in enumerate(poll_data["emojis"]):
                reaction = discord.utils.get(message.reactions, emoji=emoji)
                if reaction:
                    # Get the actual users who reacted
                    async for user in reaction.users():
                        if not user.bot:
                            unique_voters.add(user.id)
                    votes = reaction.count - 1  # Subtract bot's reaction
                else:
                    votes = 0
                results.append((poll_data["options"][i], votes))
                total_votes += votes

            # Update poll data with unique voters
            poll_data["total_voters"] = unique_voters
            
            # Sort results by votes
            results.sort(key=lambda x: x[1], reverse=True)

            # Create and send/update results embed
            embed = await self._create_poll_results(poll_data, results, total_votes)
            
            if message_id in self._result_messages:
                try:
                    result_message = await channel.fetch_message(self._result_messages[message_id])
                    await result_message.edit(embed=embed)
                except:
                    result_message = await channel.send(embed=embed)
                    self._result_messages[message_id] = result_message.id
            else:
                result_message = await channel.send(embed=embed)
                self._result_messages[message_id] = result_message.id

        except Exception as e:
            logging.error(f"Error updating poll results: {e}")

    @tasks.loop(minutes=1)
    async def check_ended_polls(self):
        """Check for and handle ended polls."""
        current_time = datetime.utcnow()
        ended_polls = []

        for poll_id, poll_data in self.active_polls.items():
            try:
                if current_time >= poll_data["end_time"]:
                    # Update results one final time
                    await self._update_poll_results(poll_id)
                    
                    # Get the channel and message
                    channel = self.bot.get_channel(poll_data["channel_id"])
                    
                    # Add poll to ended list
                    ended_polls.append(poll_id)
                    
                    # Announce poll end
                    await channel.send(
                        f"🎊 The poll **{poll_data['question']}** has ended! Check the results above!"
                    )
                elif (poll_data["end_time"] - current_time).total_seconds() % 300 == 0:
                    # Update results every 5 minutes for active polls
                    await self._update_poll_results(poll_id)
                    
            except Exception as e:
                logging.error(f"Error handling poll {poll_id}: {e}")
                ended_polls.append(poll_id)

        # Remove ended polls
        for poll_id in ended_polls:
            self.active_polls.pop(poll_id, None)
            self._result_messages.pop(poll_id, None)

    @check_ended_polls.before_loop
    async def before_check_ended_polls(self):
        """Wait until the bot is ready before starting the task"""
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Engagement(bot))
