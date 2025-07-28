"""
AWS Daily Tips - Nimbus shares his cloud wisdom daily
"""
import discord
from discord.ext import commands, tasks
import json
import random
import asyncio
from datetime import datetime, timezone, timedelta
from utils.config import load_json_data
from utils.dragon_personality import DragonPersonality

# Philippines timezone (UTC+8)
PH_TZ = timezone(timedelta(hours=8))

class AWSTips(commands.Cog):
    """Daily AWS tips with Nimbus personality."""
    
    def __init__(self, bot):
        self.bot = bot
        self.tips_channel_name = "aws-tips"
        self.aws_tips = load_json_data('data/aws_tips.json', {})
        self.used_tips_file = 'data/used_tips.json'
        self.used_tips = load_json_data(self.used_tips_file, {})
        self.daily_tips_task.start()
    
    def cog_unload(self):
        self.daily_tips_task.cancel()
    
    @tasks.loop(hours=24)
    async def daily_tips_task(self):
        """Send daily AWS tip at 9 AM PH time."""
        now = datetime.now(PH_TZ)
        if now.hour == 9:  # 9 AM PH time
            await self.send_daily_tip()
    
    @daily_tips_task.before_loop
    async def before_daily_tips(self):
        await self.bot.wait_until_ready()
        # Wait until 9 AM PH time
        now = datetime.now(PH_TZ)
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if now >= target:
            target += timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)
    
    async def send_daily_tip(self):
        """Send a unique daily AWS tip."""
        # Find aws-tips channel
        channel = None
        for guild in self.bot.guilds:
            for ch in guild.text_channels:
                if self.tips_channel_name in ch.name.lower():
                    channel = ch
                    break
            if channel:
                break
        
        if not channel:
            return
        
        # Get current month key
        current_month = datetime.now(PH_TZ).strftime("%Y-%m")
        
        # Reset used tips if new month
        if current_month not in self.used_tips:
            self.used_tips = {current_month: []}
            self._save_used_tips()
        
        # Get available tips
        available_tips = self._get_available_tips(current_month)
        
        if not available_tips:
            # All tips used this month, reset for new cycle
            self.used_tips[current_month] = []
            available_tips = self._get_available_tips(current_month)
        
        if available_tips:
            tip = random.choice(available_tips)
            self.used_tips[current_month].append(tip['id'])
            self._save_used_tips()
            
            embed = self._create_tip_embed(tip)
            await channel.send(embed=embed)
    
    def _get_available_tips(self, month_key):
        """Get tips not used this month."""
        used_ids = set(self.used_tips.get(month_key, []))
        available = []
        
        tip_id = 0
        for category, tips in self.aws_tips.items():
            for tip in tips:
                if tip_id not in used_ids:
                    tip_copy = tip.copy()
                    tip_copy['id'] = tip_id
                    tip_copy['category'] = category
                    available.append(tip_copy)
                tip_id += 1
        
        return available
    
    def _create_tip_embed(self, tip):
        """Create embed for AWS tip with Nimbus personality."""
        dragon_intros = [
            "> `adjusts tiny professor glasses`",
            "> `flutters wings excitedly`", 
            "> `straightens tiny crown`",
            "> `puffs out chest proudly`",
            "> `taps claws on desk importantly`"
        ]
        
        dragon_outros = [
            "> `nods wisely while trying to look mature`",
            "> `flaps wings with satisfaction`",
            "> `pushes up glasses proudly`",
            "> `straightens tiny wings confidently`"
        ]
        
        intro = random.choice(dragon_intros)
        outro = random.choice(dragon_outros)
        
        embed = discord.Embed(
            title=f"☁️ Daily AWS Wisdom - {tip['category']}",
            color=DragonPersonality.COLORS['primary']
        )
        
        description = f"{intro}\n\n**{tip['title']}**\n\n{tip['description']}\n\n{outro}"
        embed.description = description
        
        embed.add_field(
            name="📚 Learn More",
            value=f"[AWS Documentation]({tip['learn_more']})",
            inline=False
        )
        
        embed.set_footer(text="Nimbus • Your Daily Cloud Wisdom Dragon 🐉")
        embed.timestamp = datetime.now(PH_TZ)
        
        return embed
    
    def _save_used_tips(self):
        """Save used tips to file."""
        try:
            with open(self.used_tips_file, 'w') as f:
                json.dump(self.used_tips, f, indent=2)
        except Exception:
            pass
    
    @commands.command(name="tip")
    async def manual_tip(self, ctx):
        """Get a random AWS tip manually."""
        current_month = datetime.now(PH_TZ).strftime("%Y-%m")
        available_tips = self._get_available_tips(current_month)
        
        if not available_tips:
            available_tips = self._get_available_tips("manual")
        
        if available_tips:
            tip = random.choice(available_tips)
            embed = self._create_tip_embed(tip)
            await ctx.send(embed=embed)
        else:
            await ctx.send("> `scratches head with claw`\n\nUh oh! I seem to have run out of tips... that's definitely not supposed to happen!")

async def setup(bot):
    await bot.add_cog(AWSTips(bot))