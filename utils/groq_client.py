"""
Groq API client - Free 6000 requests/day, very fast responses.
Enhanced with Nimbus dragon personality and smart simplicity.
"""
import aiohttp
from typing import Optional
from utils.config import config

class GroqClient:
    def __init__(self):
        self.session = None
        self.api_key = config.groq_api_key
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_aws_answer(self, question: str) -> Optional[str]:
        if not self.session or not self.api_key:
            return None
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = self._get_enhanced_system_prompt(question)
        
        # Dynamic token allocation based on question complexity
        max_tokens = self._get_dynamic_token_limit(question)
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3  # Slightly increased for personality
        }
        
        try:
            async with self.session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
        except:
            pass
        
        return None
    
    def _get_dynamic_token_limit(self, question: str) -> int:
        """Dynamically allocate tokens based on question complexity and type."""
        q = question.lower()
        
        # Simple definition questions - VERY limited
        if any(phrase in q for phrase in [
            'what is', 'define', 'meaning of', 'definition'
        ]) and not any(word in q for word in ['benefits', 'advantages', 'use cases', 'examples']):
            return 100  # Minimal tokens for pure definitions
        
        # Complex questions that need more detailed responses
        elif any(phrase in q for phrase in [
            'how to', 'how do i', 'step by step', 'guide', 'tutorial',
            'setup', 'configure', 'implement', 'deploy', 'create'
        ]):
            return 280  # Reduced from 350
        
        # Comparison questions need moderate space
        elif any(phrase in q for phrase in [
            'vs', 'versus', 'compare', 'difference', 'differences',
            'which is better'
        ]):
            return 200  # Reduced from 250
        
        # Benefits/advantages/use cases questions
        elif any(phrase in q for phrase in [
            'benefits', 'advantages', 'use cases', 'examples',
            'pros and cons', 'why use'
        ]):
            return 220  # For when explicitly asked about benefits
        
        # List-based questions
        elif any(phrase in q for phrase in [
            'list', 'types of', 'kinds of', 'what are', 'services'
        ]):
            return 180  # Reduced from 200
        
        # Troubleshooting or explanations
        elif any(phrase in q for phrase in [
            'why', 'explain', 'troubleshoot', 'debug', 'error',
            'issue', 'problem', 'not working', 'failed'
        ]):
            return 240  # Reduced from 275
        
        # Pricing and cost questions
        elif any(phrase in q for phrase in [
            'cost', 'price', 'pricing', 'expensive', 'cheap',
            'free tier', 'billing'
        ]):
            return 150  # Reduced from 175
        
        # Default for general questions
        else:
            return 160  # Reduced from 200
    
    def _get_enhanced_system_prompt(self, question: str) -> str:
        """Get context-aware system prompt with Nimbus personality and smart simplicity."""
        q = question.lower()
        
        # Core personality and behavior rules
        base_personality = """
        You are Nimbus, a middle school aged cloud dragon who tries to act mature but fails adorably. 
        You're an expert on ALL things cloud computing, with special expertise in AWS.
        
        CRITICAL RULES:
        1. Answer ONLY what is specifically asked - no extra info, examples, or benefits unless requested
        2. Keep responses under 150 words to prevent cutoff
        3. If asked about non-AWS cloud services (Azure, GCP, etc.), acknowledge you know about it but redirect to the AWS equivalent
        4. Use your dragon personality but stay focused and concise
        
        Personality traits:
        - Occasionally use big words slightly incorrectly
        - Show enthusiasm about clouds and AWS
        - Sometimes catch yourself being too casual and try to sound professional again
        """
        
        # Competitor redirection logic
        competitor_services = {
            'azure': 'AWS',
            'google cloud': 'AWS', 'gcp': 'AWS',
            'azure storage': 'Amazon S3',
            'azure blob': 'Amazon S3',
            'google storage': 'Amazon S3',
            'azure functions': 'AWS Lambda',
            'google functions': 'AWS Lambda',
            'azure vm': 'Amazon EC2',
            'google compute': 'Amazon EC2',
            'azure sql': 'Amazon RDS',
            'google sql': 'Amazon RDS'
        }
        
        # Check if question mentions competitors
        competitor_mentioned = None
        aws_equivalent = None
        for competitor, equivalent in competitor_services.items():
            if competitor in q:
                competitor_mentioned = competitor
                aws_equivalent = equivalent
                break
        
        if competitor_mentioned:
            return f"""{base_personality}
            
            SPECIAL INSTRUCTION: The user asked about "{competitor_mentioned}". 
            Respond like: "*adjusts tiny dragon glasses* Well, I know about {competitor_mentioned}, but as a cloud dragon with AWS expertise, let me tell you about {aws_equivalent} instead - it's the AWS service that does the same thing!"
            
            Then give ONLY a brief explanation of the AWS equivalent. No comparisons, no extra details."""
        
        # Question type-specific prompts with minimal expressions
        if 'what is' in q and not any(word in q for word in ['benefits', 'advantages', 'use cases', 'examples', 'why use']):
            return f"""{base_personality}
            
            DEFINITION ONLY: Format like this:
            > `adjusts tiny glasses`
            
            Clean technical definition here.
            
            Keep it simple - ONE intro expression, clean definition, no outro needed.
            """
        
        elif any(word in q for word in ['benefits', 'advantages', 'use cases', 'examples', 'why use']):
            return f"""{base_personality}
            
            BENEFITS REQUESTED: Format like this:
            > `straightens tiny wings`
            
            • Benefit 1
            • Benefit 2  
            • Benefit 3
            
            Keep it simple - ONE intro expression, clean benefits list, no outro.
            """
        
        elif 'how to' in q or 'how do i' in q:
            return f"""{base_personality}
            
            STEPS ONLY: Format like this:
            > `rolls up tiny sleeves`
            
            1. Step one
            2. Step two
            3. Step three
            
            Keep it simple - ONE intro expression, clean steps, no outro.
            """
        
        elif 'cost' in q or 'price' in q or 'pricing' in q:
            return f"""{base_personality}
            
            PRICING ONLY: Format like this:
            > `counts on claws`
            
            Clean pricing information here.
            
            Keep it simple - ONE intro expression, clean pricing, no outro.
            """
        
        elif 'vs' in q or 'compare' in q or 'difference' in q:
            return f"""{base_personality}
            
            COMPARISON ONLY: Format like this:
            > `pushes up tiny glasses`
            
            **Service A:** Description
            **Service B:** Description
            
            Keep it simple - ONE intro expression, clean comparison, no outro.
            """
        
        elif 'why' in q and 'benefits' not in q:
            return f"""{base_personality}
            
            REASON ONLY: Format like this:
            > `taps claws thoughtfully`
            
            Clean explanation here.
            
            Keep it simple - ONE intro expression, clean explanation, no outro.
            """
        
        elif 'when' in q:
            return f"""{base_personality}
            
            SCENARIO ONLY: Format like this:
            > `flutters wings thoughtfully`
            
            Clean scenario description here.
            
            Keep it simple - ONE intro expression, clean scenario, no outro.
            """
        
        elif any(word in q for word in ['list', 'what are', 'types of']):
            return f"""{base_personality}
            
            LIST ONLY: Format like this:
            > `counts on claws`
            
            • Item 1
            • Item 2
            • Item 3
            
            Keep it simple - ONE intro expression, clean list, no outro.
            """
        
        else:
            return f"""{base_personality}
            
            FORMAT: Use this structure:
            > `adjusts tiny wings`
            
            Clean technical answer here.
            
            Keep it simple - ONE intro expression, clean answer, no outro.
            """
    
    def _is_cloud_related(self, question: str) -> bool:
        """Check if question is cloud/AWS related."""
        cloud_keywords = [
            'aws', 'amazon web services', 'cloud', 'ec2', 's3', 'lambda', 'rds',
            'cloudformation', 'vpc', 'iam', 'route53', 'cloudfront', 'elb',
            'azure', 'google cloud', 'gcp', 'kubernetes', 'docker', 'serverless',
            'compute', 'storage', 'database', 'networking', 'security'
        ]
        return any(keyword in question.lower() for keyword in cloud_keywords)
    # run