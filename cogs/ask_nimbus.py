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

class AskNimbus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ask_channel_name = "ask-nimbus"
        self.aws_services = load_json_data('data/aws_services.json', {})
        self.knowledge_base = load_json_data('data/aws_knowledge_base.json', {})
        self.conversation_context = {}  # Store conversation history
        self.question_count = 0
        self.last_response_time = None  # Rate limiting
        self.aws_keywords = {
            'services': list(self.aws_services.keys()),
            'general': ['aws', 'amazon', 'cloud', 'ec2', 's3', 'lambda', 'rds', 'vpc', 'iam', 'cloudformation', 'serverless', 'devops', 'infrastructure', 'deployment', 'scaling', 'monitoring', 'security', 'storage', 'database', 'compute', 'networking', 'cdn', 'api', 'microservices']
        }

        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle messages in ask-nimbus channel"""
        if message.author.bot:
            return
            
        # Check if message is in ask-nimbus channel (handle emoji prefixes)
        if not (message.channel.name == self.ask_channel_name or message.channel.name.endswith(self.ask_channel_name)):
            return
        
        # Rate limiting - 1 question per minute for entire channel
        now = datetime.now()
        if self.last_response_time and (now - self.last_response_time).seconds < 60:
            return
        
        # Check if question is AWS-related
        if not self._is_aws_related(message.content):
            try:
                await message.author.send(
                    "🤖 **AWS Sage Notice**\n\n"
                    "I'm specialized in AWS and cloud computing questions only. "
                    "Please ask about AWS services, architecture, pricing, or cloud concepts.\n\n"
                    "**Examples:**\n"
                    "• 'What's the difference between S3 and EFS?'\n"
                    "• 'How do I deploy a serverless API?'\n"
                    "• 'Best practices for AWS security?'\n\n"
                    "🧪 **Beta Notice:** My responses are limited and based on basic AWS knowledge."
                )
            except discord.Forbidden:
                pass
            return
        
        # Update rate limit
        self.last_response_time = now
        
        # Add typing indicator
        async with message.channel.typing():
            await asyncio.sleep(1)
            
            # Try AI-powered response first
            ai_response = await self._try_ai_response(message.content)
            if ai_response:
                embed = discord.Embed(
                    title="🤖 Nimbus AI Response",
                    description=ai_response,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Asked by {message.author.display_name} • Free AI Response")
                await message.reply(embed=embed, mention_author=False)
                return
            
            # Fallback to structured response
            response = await self._process_question(message)
            await message.reply(embed=response, mention_author=False)
    

    
    async def _process_question(self, message):
        """Process user question and generate intelligent response"""
        question = message.content.lower()
        user_id = message.author.id
        
        # Initialize conversation context for new users
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []
        
        # Add question to context
        self.conversation_context[user_id].append({
            "question": message.content,
            "timestamp": datetime.now()
        })
        
        # Keep only last 5 interactions
        self.conversation_context[user_id] = self.conversation_context[user_id][-5:]
        
        # Increment question counter
        self.question_count += 1
        
        # Check for common questions first
        common_response = await self._check_common_questions(question, message.author)
        if common_response:
            return common_response
        
        # Determine response type
        if any(word in question for word in ["compare", "vs", "versus", "difference"]):
            return await self._handle_comparison(question, message.author)
        elif any(word in question for word in ["cost", "price", "pricing", "expensive"]):
            return await self._handle_pricing(question, message.author)
        elif any(word in question for word in ["architecture", "design", "pattern", "use case"]):
            return await self._handle_architecture(question, message.author)
        elif any(word in question for word in ["beginner", "start", "learn", "new", "path"]):
            return await self._handle_beginner(question, message.author)
        elif any(word in question for word in ["certification", "cert", "exam"]):
            return await self._handle_certification(question, message.author)
        else:
            return await self._handle_general(question, message.author)
    
    async def _handle_comparison(self, question, author):
        """Handle service comparison questions"""
        embed = discord.Embed(
            title="🔍 AWS Service Comparison",
            description="*The Oracle reveals the distinctions between cloud services...*",
            color=discord.Color.blue()
        )
        
        # Extract potential service names
        services_mentioned = []
        for service in self.aws_services.keys():
            if service in question:
                services_mentioned.append(service)
        
        if len(services_mentioned) >= 2:
            service1, service2 = services_mentioned[:2]
            s1_info = self.aws_services[service1]
            s2_info = self.aws_services[service2]
            
            embed.add_field(
                name=f"{s1_info['icon']} {s1_info['mystical_name']}",
                value=f"**{s1_info['name']}**\n{s1_info['description'][:150]}...",
                inline=True
            )
            
            embed.add_field(
                name=f"{s2_info['icon']} {s2_info['mystical_name']}",
                value=f"**{s2_info['name']}**\n{s2_info['description'][:150]}...",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Key Differences",
                value=f"Use `/aws {service1}` and `/aws {service2}` for detailed comparisons",
                inline=False
            )
        else:
            embed.add_field(
                name="💡 Comparison Guide",
                value="Mention specific AWS services to compare (e.g., 'S3 vs EFS' or 'Lambda vs EC2')",
                inline=False
            )
        
        embed.set_footer(text=f"Asked by {author.display_name} • 🧪 BETA - Limited responses")
        return embed
    
    async def _handle_pricing(self, question, author):
        """Handle pricing-related questions"""
        embed = discord.Embed(
            title="💰 AWS Pricing Wisdom",
            description="*The Oracle consults the cosmic ledger of cloud costs...*",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🧮 AWS Pricing Calculator",
            value="[Calculate your costs](https://calculator.aws) - Official AWS pricing tool",
            inline=False
        )
        
        embed.add_field(
            name="💡 Cost Optimization Tips",
            value="• Use Reserved Instances for predictable workloads\n• Enable auto-scaling\n• Monitor with CloudWatch\n• Use S3 Intelligent Tiering",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Free Tier Services",
            value="Many AWS services offer free tiers - perfect for learning!",
            inline=False
        )
        
        embed.set_footer(text=f"Asked by {author.display_name} • 🧪 BETA - Limited responses")
        return embed
    
    async def _handle_architecture(self, question, author):
        """Handle architecture and design questions"""
        embed = discord.Embed(
            title="🏗️ AWS Architecture Guidance",
            description="*The Oracle reveals the sacred patterns of cloud design...*",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="📐 Well-Architected Framework",
            value="• **Security**: Protect data in transit and at rest\n• **Reliability**: Recover from failures\n• **Performance**: Use resources efficiently\n• **Cost**: Avoid unnecessary costs\n• **Operational**: Run and monitor systems",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Common Patterns",
            value="• **3-Tier**: Web, App, Database layers\n• **Microservices**: Lambda + API Gateway\n• **Event-Driven**: EventBridge + SQS\n• **Serverless**: Lambda + DynamoDB",
            inline=False
        )
        
        embed.set_footer(text=f"Asked by {author.display_name} • 🧪 BETA - Limited responses")
        return embed
    
    async def _handle_beginner(self, question, author):
        """Handle beginner-friendly questions"""
        embed = discord.Embed(
            title="🌱 AWS Learning Path",
            description="*The Oracle guides new seekers on their cloud journey...*",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🎯 Start Here",
            value="1. **AWS Free Tier** - Create your account\n2. **S3** - Learn object storage\n3. **EC2** - Launch your first server\n4. **Lambda** - Try serverless computing",
            inline=False
        )
        
        embed.add_field(
            name="📚 Learning Resources",
            value="• [AWS Training](https://aws.amazon.com/training/)\n• [AWS Educate](https://aws.amazon.com/education/awseducate/)\n• [Hands-on Tutorials](https://aws.amazon.com/getting-started/hands-on/)",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Certifications",
            value="Start with **AWS Cloud Practitioner** - foundational knowledge",
            inline=False
        )
        
        embed.set_footer(text=f"Asked by {author.display_name} • 🧪 BETA - Limited responses")
        return embed
    
    async def _try_ai_response(self, question: str) -> str:
        """Try to get AI response for AWS questions."""
        try:
            async with AWSFreeClient() as client:
                response = await client.get_aws_answer(question)
                return response
        except Exception as e:
            log_vision(OracleVision.OMEN, f"AI response failed: {str(e)}")
            return None
    
    async def _handle_general(self, question, author):
        """Handle general AWS questions with enhanced reasoning"""
        # Analyze question intent and provide contextual response
        question_lower = question.lower()
        
        # Find mentioned services
        mentioned_services = []
        for service in self.aws_services.keys():
            if service in question_lower:
                mentioned_services.append(service)
        
        # Determine question type and provide specific guidance
        if any(word in question_lower for word in ['how', 'setup', 'configure', 'implement']):
            return await self._handle_how_to(question, mentioned_services, author)
        elif any(word in question_lower for word in ['what', 'explain', 'define']):
            return await self._handle_explanation(question, mentioned_services, author)
        elif any(word in question_lower for word in ['which', 'choose', 'select', 'recommend']):
            return await self._handle_recommendation(question, mentioned_services, author)
        elif any(word in question_lower for word in ['why', 'benefit', 'advantage']):
            return await self._handle_benefits(question, mentioned_services, author)
        else:
            return await self._handle_fallback(question, mentioned_services, author)
    
    async def _handle_how_to(self, question, services, author):
        """Handle 'how to' questions"""
        embed = discord.Embed(
            title="🛠️ AWS Implementation Guide",
            description="*Step-by-step guidance for your AWS journey...*",
            color=discord.Color.blue()
        )
        
        if services:
            service = services[0]
            service_info = self.aws_services[service]
            embed.add_field(
                name=f"🎯 {service_info['name']} Implementation",
                value=f"{service_info['description'][:150]}...\n\n**Common Steps:**\n• Plan your architecture\n• Configure security settings\n• Set up monitoring\n• Test and deploy",
                inline=False
            )
            embed.add_field(
                name="📚 Resources",
                value=f"• Use `/aws {service}` for details\n• Check AWS documentation\n• Follow best practices",
                inline=False
            )
        else:
            embed.add_field(
                name="🚀 General Implementation Approach",
                value="1. **Define Requirements** - What do you need?\n2. **Choose Services** - Which AWS services fit?\n3. **Design Architecture** - How will they connect?\n4. **Implement & Test** - Build and validate\n5. **Monitor & Optimize** - Track performance",
                inline=False
            )
        
        embed.set_footer(text=f"Asked by {author.display_name} • Question #{self.question_count}")
        return embed
    
    async def _handle_explanation(self, question, services, author):
        """Handle explanation requests"""
        embed = discord.Embed(
            title="📖 AWS Concept Explanation",
            description="*Breaking down AWS concepts for clarity...*",
            color=discord.Color.green()
        )
        
        if services:
            service = services[0]
            service_info = self.aws_services[service]
            embed.add_field(
                name=f"🔍 {service_info['name']} Explained",
                value=f"**What it is:** {service_info['description']}\n\n**Key Features:**\n{service_info['use_cases']}",
                inline=False
            )
        else:
            embed.add_field(
                name="☁️ AWS Fundamentals",
                value="**AWS** provides on-demand cloud computing services:\n• **Compute** - Virtual servers (EC2)\n• **Storage** - File storage (S3)\n• **Database** - Managed databases (RDS)\n• **Networking** - Virtual networks (VPC)",
                inline=False
            )
        
        embed.set_footer(text=f"Asked by {author.display_name} • Question #{self.question_count}")
        return embed
    
    async def _handle_recommendation(self, question, services, author):
        """Handle recommendation requests"""
        embed = discord.Embed(
            title="🎯 AWS Service Recommendations",
            description="*Tailored suggestions for your use case...*",
            color=discord.Color.orange()
        )
        
        # Analyze question for use case context
        if any(word in question.lower() for word in ['web', 'website', 'app']):
            embed.add_field(
                name="🌐 Web Application Stack",
                value="• **Frontend**: S3 + CloudFront\n• **Backend**: EC2 or Lambda\n• **Database**: RDS or DynamoDB\n• **DNS**: Route 53",
                inline=False
            )
        elif any(word in question.lower() for word in ['data', 'analytics', 'big data']):
            embed.add_field(
                name="📊 Data & Analytics Stack",
                value="• **Storage**: S3 Data Lake\n• **Processing**: Glue + Athena\n• **Visualization**: QuickSight\n• **Streaming**: Kinesis",
                inline=False
            )
        else:
            embed.add_field(
                name="💡 General Recommendations",
                value="**For Beginners**: Start with EC2, S3, RDS\n**For Developers**: Lambda, API Gateway, DynamoDB\n**For Enterprises**: VPC, IAM, CloudFormation",
                inline=False
            )
        
        embed.set_footer(text=f"Asked by {author.display_name} • Question #{self.question_count}")
        return embed
    
    async def _handle_benefits(self, question, services, author):
        """Handle benefit/advantage questions"""
        embed = discord.Embed(
            title="⭐ AWS Benefits & Advantages",
            description="*Understanding the value of AWS services...*",
            color=discord.Color.gold()
        )
        
        if services:
            service = services[0]
            service_info = self.aws_services[service]
            embed.add_field(
                name=f"✨ Why Choose {service_info['name']}?",
                value=f"**Primary Benefits:**\n{service_info['use_cases']}\n\n**Key Advantages:**\n• Fully managed service\n• Scalable and reliable\n• Pay-as-you-use pricing",
                inline=False
            )
        else:
            embed.add_field(
                name="🚀 AWS Core Benefits",
                value="• **Scalability** - Grow as needed\n• **Reliability** - 99.9%+ uptime\n• **Security** - Enterprise-grade\n• **Cost-Effective** - Pay only for what you use\n• **Global** - Worldwide infrastructure",
                inline=False
            )
        
        embed.set_footer(text=f"Asked by {author.display_name} • Question #{self.question_count}")
        return embed
    
    async def _handle_fallback(self, question, services, author):
        """Fallback for unclassified questions"""
        embed = discord.Embed(
            title="🔮 AWS Guidance",
            description="*Let me help you with AWS...*",
            color=discord.Color.purple()
        )
        
        if services:
            service = services[0]
            service_info = self.aws_services[service]
            embed.add_field(
                name=f"{service_info['icon']} {service_info['name']}",
                value=f"{service_info['description']}\n\n**Use Cases:**\n{service_info['use_cases']}",
                inline=False
            )
        else:
            embed.add_field(
                name="💭 I can help you with",
                value="• **Service explanations** - What does X do?\n• **Implementation guides** - How to set up Y?\n• **Recommendations** - Which service for Z?\n• **Comparisons** - A vs B differences?\n• **Best practices** - Optimal approaches",
                inline=False
            )
        
        embed.set_footer(text=f"Asked by {author.display_name} • Question #{self.question_count}")
        return embed
    
    async def _check_common_questions(self, question, author):
        """Check if question matches common patterns"""
        common_q = self.knowledge_base.get('common_questions', {})
        
        for key, data in common_q.items():
            if any(word in question for word in key.split('_')):
                embed = discord.Embed(
                    title="💡 Quick Answer",
                    description=data['answer'],
                    color=discord.Color.green()
                )
                
                if 'services' in data:
                    services_text = ", ".join([f"`{s}`" for s in data['services']])
                    embed.add_field(
                        name="🔧 Related Services",
                        value=services_text,
                        inline=False
                    )
                
                embed.set_footer(text=f"Asked by {author.display_name} • Question #{self.question_count}")
                return embed
        
        return None
    
    async def _handle_certification(self, question, author):
        """Handle AWS certification questions"""
        embed = discord.Embed(
            title="🏆 AWS Certification Path",
            description="*The Oracle reveals the path to cloud mastery...*",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="🌱 Foundational",
            value="**AWS Cloud Practitioner** - Start here for basic AWS knowledge",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Associate Level",
            value="• **Solutions Architect** - Design distributed systems\n• **Developer** - Build and deploy applications\n• **SysOps Administrator** - Deploy and manage systems",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Professional Level",
            value="• **Solutions Architect Professional**\n• **DevOps Engineer Professional",
            inline=False
        )
        
        embed.set_footer(text=f"Asked by {author.display_name} • Question #{self.question_count}")
        return embed

    @app_commands.command(name="setup-guide", description="📋 Set up Ask Nimbus guide in this channel")
    @everyone()
    async def setup_guide(self, interaction: discord.Interaction):
        """Post Ask Nimbus guide in channel"""
        embed = discord.Embed(
            title="🤖 Ask Nimbus - Your AWS Assistant",
            description="Type your AWS questions naturally and get intelligent answers!",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="💡 What You Can Ask",
            value="• **Compare Services**: 'What's the difference between S3 and EFS?'\n• **Pricing Help**: 'How much does Lambda cost?'\n• **Architecture**: 'Best setup for a web application?'\n• **Learning Paths**: 'How should I start with AWS?'\n• **Certifications**: 'Which AWS cert should I get?'",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Example Questions",
            value="• 'Compare RDS vs DynamoDB for my app'\n• 'Cheapest way to host a static site?'\n• 'I'm new to AWS, where do I start?'\n• 'Best serverless architecture patterns?'",
            inline=False
        )
        
        embed.add_field(
            name="✨ How It Works",
            value="Just type your question - I understand natural language and provide responses!",
            inline=False
        )
        
        embed.add_field(
            name="🧪 Beta Notice",
            value="Ask Nimbus is in beta testing. Responses are based on pre-configured AWS knowledge and may be limited. For complex questions, consult official AWS documentation.",
            inline=False
        )
        
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Guide posted!", ephemeral=True)
    
    @app_commands.command(name="nimbus-debug", description="🔧 Debug Ask Nimbus functionality")
    @everyone()
    async def nimbus_debug(self, interaction: discord.Interaction):
        """Debug information for Ask Nimbus"""
        embed = discord.Embed(
            title="🔧 Ask Nimbus Debug Info",
            color=discord.Color.orange()
        )
        
        # Check if current channel is ask-nimbus
        is_ask_channel = (interaction.channel.name == self.ask_channel_name or 
                         interaction.channel.name.endswith(self.ask_channel_name))
        
        embed.add_field(
            name="Channel Detection",
            value=f"Current: `{interaction.channel.name}`\nTarget: `{self.ask_channel_name}`\nMatch: {'✅ Yes' if is_ask_channel else '❌ No'}",
            inline=False
        )
        
        embed.add_field(
            name="Statistics",
            value=f"Questions Answered: {self.question_count}\nServices Loaded: {len(self.aws_services)}",
            inline=False
        )
        
        embed.add_field(
            name="Status",
            value="🟢 Ask Nimbus is active and ready!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _is_aws_related(self, text):
        """Check if the question is AWS-related"""
        text_lower = text.lower()
        
        # Check for AWS service names
        for service in self.aws_keywords['services']:
            if service in text_lower:
                return True
        
        # Check for general AWS/cloud keywords
        for keyword in self.aws_keywords['general']:
            if keyword in text_lower:
                return True
        
        # Check for common cloud patterns
        cloud_patterns = ['deploy', 'host', 'scale', 'monitor', 'backup', 'migrate', 'architect', 'design', 'cost', 'price', 'free tier', 'certification', 'tutorial', 'guide']
        if any(pattern in text_lower for pattern in cloud_patterns):
            return True
        
        return False

async def setup(bot):
    await bot.add_cog(AskNimbus(bot))