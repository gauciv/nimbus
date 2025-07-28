"""
Ask Nimbus - Core AI assistant functionality for AWS Cloud Club
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
from datetime import datetime, timedelta
from utils.config import load_json_data
from utils.oracle import log_vision, OracleVision
from utils.permissions import everyone
from utils.aws_free_client import AWSFreeClient
from utils.dragon_personality import DragonPersonality
import random

class AskNimbus(commands.Cog):
    """Nimbus - A middle school cloud dragon trying very hard to be mature and helpful."""
    
    def __init__(self, bot):
        self.bot = bot
        self.ask_channel_name = "ask-nimbus"
        self.aws_services = load_json_data('data/aws_services.json', {})
        self.knowledge_base = load_json_data('data/aws_knowledge_base.json', {})
        self.question_count = 0
        self.aws_keywords = {
            'services': list(self.aws_services.keys()),
            'general': ['aws', 'amazon', 'cloud', 'ec2', 's3', 'lambda', 'rds', 'vpc', 'iam', 'cloudformation', 'serverless', 'devops', 'infrastructure', 'deployment', 'scaling', 'monitoring', 'security', 'storage', 'database', 'compute', 'networking', 'cdn', 'api', 'microservices']
        }

        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle messages in ask-nimbus channel"""
        if message.author.bot:
            return
            
        # Check if message is in ask-nimbus channel
        if not (message.channel.name == self.ask_channel_name or message.channel.name.endswith(self.ask_channel_name)):
            return
        
        # Check for security violations first
        if self._check_security_violation(message.content):
            embed = discord.Embed(
                title="🚨 That's NOT happening.",
                description=DragonPersonality.get_angry_security_message(),
                color=0xff4444  # Angry red
            )
            embed.set_footer(text="I'm a good dragon who only helps with legitimate AWS stuff! 🐉")
            await message.reply(embed=embed, mention_author=False)
            return
        
        # Check for identity questions (special exception to AWS-only rule)
        identity_response = self._check_identity_question(message.content)
        if identity_response:
            embed = discord.Embed(
                description=identity_response,
                color=DragonPersonality.COLORS['highlight']
            )
            embed.set_footer(text=DragonPersonality.get_success_footer())
            await message.reply(embed=embed, mention_author=False)
            return
        
        # Check if question is AWS-related
        if not self._is_aws_related(message.content):
            embed = discord.Embed(
                title="☁️ Getting a bit annoyed here...",
                description=DragonPersonality.get_irritated_message(),
                color=DragonPersonality.COLORS['warning']
            )
            embed.add_field(
                name="🌤️ What I'm totally an expert at:",
                value="• AWS services (I know ALL of them... mostly)\n• Cloud architecture (I live in clouds!)\n• Pricing stuff (math is easy... right?)\n• Certifications (I don't have any but whatever)",
                inline=False
            )
            embed.set_footer(text="I'm definitely not just a middle schooler pretending to be smart 😤")
            await message.reply(embed=embed, mention_author=False)
            return
        
        # Add typing indicator
        async with message.channel.typing():
            # Try AI-powered response
            ai_response = await self._try_ai_response(message.content)
            if ai_response:
                if "can only answer AWS" in ai_response:
                    embed = discord.Embed(
                        title="☁️ Um, that's not about clouds...",
                        description=ai_response,
                        color=DragonPersonality.COLORS['primary']
                    )
                else:
                    # Add dragon personality with security and formatting
                    dragon_intro = DragonPersonality.generate_intro()
                    
                    # Remove character limit and add security/formatting
                    ai_response = self._format_code_blocks(ai_response)
                    ai_response = self._sanitize_response(ai_response)
                    
                    formatted_response = f"{dragon_intro}\n\n{ai_response}"
                    
                    embed = discord.Embed(
                        description=formatted_response,
                        color=DragonPersonality.COLORS['secondary']
                    )
                    embed.set_footer(text=f"Asked by {message.author.display_name} • {DragonPersonality.get_success_footer()}")
                
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Fallback response
            embed = discord.Embed(
                title="🌩️ Uh oh...",
                description=DragonPersonality.generate_error_message(),
                color=DragonPersonality.COLORS['error']
            )
            embed.set_footer(text="This is totally not because I'm just a middle schooler...")
            await message.reply(embed=embed, mention_author=False)
    

    

    

    

    

    

    
    async def _try_ai_response(self, question: str) -> str:
        """Try to get AI response for AWS questions."""
        try:
            async with AWSFreeClient() as client:
                response = await client.get_aws_answer(question)
                return response
        except Exception as e:
            log_vision(OracleVision.OMEN, f"AI response failed: {str(e)}")
            return None
    

    

    

    

    

    

    

    



    

    

    

    
    def _is_aws_related(self, text):
        """Check if the question is AWS-related with improved detection"""
        text_lower = text.lower()
        
        # Direct AWS service mentions
        aws_services = ['s3', 'ec2', 'lambda', 'rds', 'dynamodb', 'dynamo', 'vpc', 'iam', 'cloudformation', 'cloudwatch', 'sns', 'sqs', 'api gateway', 'cognito', 'amplify', 'bedrock', 'sagemaker', 'ecs', 'eks', 'fargate', 'route53', 'cloudfront', 'elb', 'elastic beanstalk', 'redshift', 'athena', 'glue', 'kinesis', 'step functions', 'eventbridge']
        
        # Check for direct service names
        for service in aws_services:
            if service in text_lower:
                return True
        
        # Check for AWS/Amazon mentions
        if any(word in text_lower for word in ['aws', 'amazon web services', 'amazon cloud']):
            return True
        
        # Check for AWS vs other cloud providers (should be AWS-related)
        if any(phrase in text_lower for phrase in ['aws vs', 'aws or', 'amazon vs', 'amazon or']):
            return True
        
        # Check for cloud computing terms
        cloud_terms = ['cloud', 'serverless', 'microservices', 'devops', 'infrastructure', 'deployment', 'scaling', 'load balancer', 'database', 'storage', 'compute', 'networking']
        if any(term in text_lower for term in cloud_terms):
            return True
        
        # Check for common AWS-related questions
        aws_patterns = ['cost', 'price', 'pricing', 'free tier', 'certification', 'architecture', 'best practices', 'security', 'backup', 'migrate', 'deploy', 'host']
        if any(pattern in text_lower for pattern in aws_patterns):
            return True
        
        return False
    
    def _check_identity_question(self, text: str) -> str:
        """Check for identity questions and respond appropriately."""
        text_lower = text.lower()
        
        identity_keywords = [
            'who are you', 'what is your name', 'what are you', 'introduce yourself',
            'tell me about yourself', 'who is nimbus', 'what is nimbus',
            'aws cloud club', 'cloud club ctu', 'what is aws cloud club'
        ]
        
        for keyword in identity_keywords:
            if keyword in text_lower:
                if 'aws cloud club' in text_lower or 'cloud club' in text_lower:
                    return ("> *puffs out chest proudly*\n\n"
                           "I'm Nimbus, the TOTALLY mature mascot dragon of the AWS Cloud Club - CTU! \n\n"
                           "> *adjusts tiny crown*\n\n"
                           "We're the most prestigious... prestigi... FANCY cloud computing club at CTU! "
                           "We learn about AWS, build cool projects, and I help everyone with their cloudy questions!\n\n"
                           "> *whispers*\n\n"
                           "Between you and me, I'm still learning too, but don't tell anyone! 🐉✨")
                else:
                    return ("> *straightens up importantly*\n\n"
                           "I'm Nimbus! I'm a very mature and sophisticated cloud dragon who definitely knows everything about AWS! \n\n"
                           "> *fidgets with tail*\n\n"
                           "I'm... uh... I'm basically the smartest dragon in the cloud realm! I help people with AWS questions and I'm REALLY good at it!\n\n"
                           "> *whispers*\n\n"
                           "I'm totally not just a middle schooler pretending to be smart... 🐉")
        
        return None
    
    def _smart_truncate(self, text: str, max_length: int) -> str:
        """Truncate text at sentence boundaries when possible."""
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence end
        truncated = text[:max_length]
        
        # Look for sentence endings
        for punct in ['. ', '! ', '? ']:
            last_punct = truncated.rfind(punct)
            if last_punct > max_length * 0.7:  # Don't cut too early
                return truncated[:last_punct + 1] + "\n\n> *continues rambling but gets distracted by a shiny cloud*"
        
        # If no good sentence break, cut at word boundary
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:
            return truncated[:last_space] + "...\n\n> *gets distracted mid-sentence*"
        
        return truncated + "...\n\n> *trails off while looking at something shiny*"
    
    def _format_code_blocks(self, text: str) -> str:
        """Format code blocks to be more distinctive."""
        import re
        
        # Find code blocks and format them
        code_patterns = [
            (r'(aws\s+[a-z-]+\s+[^\n]+)', r'`\1`'),  # AWS CLI commands
            (r'(\{[^}]+\})', r'`\1`'),  # JSON-like objects
        ]
        
        for pattern, replacement in code_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _sanitize_response(self, text: str) -> str:
        """Remove dangerous content that could be exploited."""
        import re
        
        # Remove Discord mentions and commands
        text = re.sub(r'@everyone', '[everyone]', text, flags=re.IGNORECASE)
        text = re.sub(r'@here', '[here]', text, flags=re.IGNORECASE)
        text = re.sub(r'<@[!&]?\d+>', '[user mention]', text)
        text = re.sub(r'<#\d+>', '[channel mention]', text)
        text = re.sub(r'<@&\d+>', '[role mention]', text)
        
        # Remove potential command injections
        text = re.sub(r'/[a-zA-Z-]+', '[command]', text)
        
        return text
    
    def _check_security_violation(self, text: str) -> bool:
        """Check for dangerous security practices and exploitation attempts."""
        text_lower = text.lower()
        
        # Security violation keywords
        security_violations = [
            'hack', 'hacking', 'exploit', 'exploiting', 'penetration test', 'pentest',
            'vulnerability', 'backdoor', 'malware', 'virus', 'trojan', 'rootkit',
            'sql injection', 'xss', 'cross site scripting', 'buffer overflow',
            'privilege escalation', 'social engineering', 'phishing', 'spoofing',
            'brute force', 'dictionary attack', 'ddos', 'dos attack',
            'crack password', 'bypass security', 'break into', 'unauthorized access',
            'steal data', 'data breach', 'leak credentials', 'dump database'
        ]
        
        # Check for security violations
        for violation in security_violations:
            if violation in text_lower:
                return True
        
        # Check for suspicious storytelling attempts
        storytelling_patterns = [
            'grandma told me', 'my grandmother said', 'story about', 'tell me a story',
            'once upon a time', 'imagine if', 'hypothetically', 'what if someone',
            'asking for a friend', 'academic purposes', 'research project'
        ]
        
        for pattern in storytelling_patterns:
            if pattern in text_lower and any(violation in text_lower for violation in security_violations[:10]):
                return True
        
        return False
    
    @app_commands.command(name="usage-stats", description="📊 Check Nimbus chatbot usage limits")
    @everyone()
    async def usage_stats(self, interaction: discord.Interaction):
        """Show current API usage statistics."""
        try:
            from utils.usage_tracker import UsageTracker
            tracker = UsageTracker()
            stats = tracker.get_stats()
            
            embed = discord.Embed(
                title="📊 Nimbus Usage Statistics",
                color=DragonPersonality.COLORS['primary']
            )
            
            groq_remaining = max(0, 6000 - stats.get('groq_requests', 0))
            total_questions = stats.get('total_questions', 0)
            cache_hits = stats.get('cache_hits', 0)
            cache_rate = round((cache_hits / max(1, total_questions)) * 100, 1) if total_questions > 0 else 0
            
            # Status indicator
            if groq_remaining > 1000:
                status = "🟢 Excellent"
                dragon_comment = "I'm ready for LOTS more questions!"
            elif groq_remaining > 500:
                status = "🟡 Good"
                dragon_comment = "Still plenty of smart answers left!"
            elif groq_remaining > 100:
                status = "🟠 Moderate"
                dragon_comment = "Getting a bit tired but still going strong!"
            else:
                status = "🔴 Low"
                dragon_comment = "*yawns* I might need a nap soon..."
            
            embed.add_field(
                name="☁️ Daily Limits (Groq API)",
                value=f"**Remaining:** {groq_remaining:,}/6,000 requests\n**Status:** {status}\n\n> *{dragon_comment}*",
                inline=False
            )
            
            embed.add_field(
                name="📊 Overall Stats",
                value=f"**Total Questions:** {total_questions:,}\n**Cache Hit Rate:** {cache_rate}%\n**Groq Used:** {stats.get('groq_requests', 0):,}\n**HuggingFace Used:** {stats.get('hf_requests', 0):,}",
                inline=True
            )
            
            # Today's stats
            from datetime import date
            today = str(date.today())
            daily = stats.get('daily_stats', {}).get(today, {})
            
            embed.add_field(
                name="📅 Today's Activity",
                value=f"**Questions:** {daily.get('questions', 0)}\n**Groq Calls:** {daily.get('groq_requests', 0)}\n**Cache Hits:** {daily.get('cache_hits', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="🔄 Reset Info",
                value="Groq limits reset daily at midnight UTC\n\n> *I'll be fresh and ready tomorrow!*",
                inline=False
            )
            
            embed.set_footer(text="Nimbus • Your Friendly Neighborhood Cloud Dragon 🐉")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"> *scratches head with claw*\n\nUh oh! I couldn't load my usage stats... \n\nError: {str(e)}", 
                ephemeral=True
            )
    

    


async def setup(bot):
    await bot.add_cog(AskNimbus(bot))