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
        
        # Check for identity questions first (special exception to AWS-only rule)
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
                title="☁️ Um, that's not about clouds...",
                description="*clears throat importantly* As a very mature and knowledgeable cloud dragon, I can ONLY help with AWS stuff! ...Please?",
                color=DragonPersonality.COLORS['primary']
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
                    # Add dragon personality to response with better length handling
                    dragon_intro = DragonPersonality.get_intro()
                    
                    # Better response truncation that finishes sentences
                    if len(ai_response) > 1800:
                        ai_response = self._smart_truncate(ai_response, 1800)
                    
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
                description=DragonPersonality.get_error_message(),
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
    

    


async def setup(bot):
    await bot.add_cog(AskNimbus(bot))