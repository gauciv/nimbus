"""
Cost-efficient AI client for Nimbus chatbot functionality.
"""
import aiohttp
from typing import Optional, Dict, Any
from utils.config import config
from utils.logging_config import get_logger

logger = get_logger(__name__)

class AIClient:
    """Multi-provider AI client with cost optimization."""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def chat_completion(self, message: str, context: str = "") -> Optional[str]:
        """Get AI response with fallback providers."""
        
        # Try providers in order of cost efficiency
        providers = [
            self._try_huggingface,
            self._try_openai,
            self._try_anthropic
        ]
        
        for provider in providers:
            try:
                response = await provider(message, context)
                if response:
                    return response
            except Exception as e:
                logger.warning("Provider failed", provider=provider.__name__, error=str(e))
        
        return "I'm having trouble connecting to my knowledge base right now. Please try again later."
    
    async def _try_huggingface(self, message: str, context: str) -> Optional[str]:
        """Try Hugging Face Inference API (most cost-effective)."""
        if not config.huggingface_api_key:
            return None
        
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {"Authorization": f"Bearer {config.huggingface_api_key}"}
        
        payload = {
            "inputs": f"{context}\nUser: {message}\nNimbus:",
            "parameters": {"max_length": 200, "temperature": 0.7}
        }
        
        async with self.session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data[0]["generated_text"].split("Nimbus:")[-1].strip()
        return None
    
    async def _try_openai(self, message: str, context: str) -> Optional[str]:
        """Try OpenAI API (moderate cost)."""
        if not config.openai_api_key:
            return None
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": f"You are Nimbus, a mystical AWS Discord bot. {context}"},
                {"role": "user", "content": message}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        async with self.session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
        return None
    
    async def _try_anthropic(self, message: str, context: str) -> Optional[str]:
        """Try Anthropic Claude API (backup)."""
        if not config.anthropic_api_key:
            return None
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": config.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 150,
            "messages": [
                {"role": "user", "content": f"{context}\n\n{message}"}
            ]
        }
        
        async with self.session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["content"][0]["text"]
        return None