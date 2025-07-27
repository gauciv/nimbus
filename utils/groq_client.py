"""
Groq API client - Free 6000 requests/day, very fast responses.
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
        
        system_prompt = self._get_system_prompt(question)
        
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            "max_tokens": 200,
            "temperature": 0.2
        }
        
        try:
            async with self.session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
        except:
            pass
        
        return None
    
    def _get_system_prompt(self, question: str) -> str:
        """Get context-aware system prompt."""
        q = question.lower()
        
        if 'what is' in q or 'explain' in q:
            return "You are an AWS expert. Explain AWS services clearly for beginners. Include what it does, main use cases, and key benefits. Be concise but informative."
        elif 'how to' in q or 'how do i' in q:
            return "You are an AWS expert. Provide step-by-step guidance for AWS tasks. Focus on practical implementation with specific service names."
        elif 'cost' in q or 'price' in q:
            return "You are an AWS expert. Explain AWS pricing models clearly. Mention free tier when applicable and provide cost optimization tips."
        elif 'vs' in q or 'compare' in q:
            return "You are an AWS expert. Compare AWS services objectively. Highlight key differences, use cases, and when to choose each option."
        elif 'best practice' in q or 'security' in q:
            return "You are an AWS expert. Provide AWS best practices and security recommendations. Focus on practical, actionable advice."
        else:
            return "You are an AWS expert. Answer AWS questions clearly and concisely. Include specific service names and practical information."