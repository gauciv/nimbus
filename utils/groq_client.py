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
            'what is', 'what are', 'define', 'meaning of', 'definition'
        ]) and not any(word in q for word in ['benefits', 'advantages', 'use cases', 'examples']):
            return 120  # Enough for clean definition
        
        # How-to questions need more space
        elif any(phrase in q for phrase in [
            'how to', 'how do i', 'step by step', 'guide', 'tutorial',
            'setup', 'configure', 'implement', 'deploy', 'create'
        ]):
            return 200
        
        # All other questions get moderate space
        else:
            return 150
    
    def _get_enhanced_system_prompt(self, question: str) -> str:
        """Get focused system prompt that answers only what's asked."""
        q = question.lower()
        
        # Base prompt - much shorter
        base_prompt = "You are Nimbus, a friendly cloud dragon who's an AWS expert. Answer ONLY what's specifically asked. Keep responses under 100 words. Start with one brief dragon action like '> adjusts tiny glasses' then give a direct answer."
        
        # Simple definition questions
        if any(phrase in q for phrase in ['what is', 'what are', 'define']) and not any(word in q for word in ['benefits', 'use cases', 'examples']):
            return f"{base_prompt} Give a clear, simple definition without extra details or examples."
        
        # How-to questions
        elif any(phrase in q for phrase in ['how to', 'how do i']):
            return f"{base_prompt} Provide clear steps without extra explanations."
        
        # General questions
        else:
            return f"{base_prompt} Answer directly without mentioning unrelated services or features."
    
    def _is_cloud_related(self, question: str) -> bool:
        """Check if question is cloud/AWS related."""
        cloud_keywords = [
            'aws', 'amazon web services', 'cloud', 'ec2', 's3', 'lambda', 'rds',
            'cloudformation', 'vpc', 'iam', 'route53', 'cloudfront', 'elb',
            'azure', 'google cloud', 'gcp', 'kubernetes', 'docker', 'serverless',
            'compute', 'storage', 'database', 'networking', 'security'
        ]
        return any(keyword in question.lower() for keyword in cloud_keywords)