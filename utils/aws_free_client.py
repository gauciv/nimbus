"""
Free AWS content client using public APIs and documentation.
"""
import aiohttp
import json
from typing import Optional
from utils.logging_config import get_logger
from utils.config import config

logger = get_logger(__name__)

class AWSFreeClient:
    """Completely free AWS content client."""
    
    def __init__(self):
        self.session = None
        self.aws_services = self._load_aws_services()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _load_aws_services(self) -> dict:
        """Load AWS services data."""
        try:
            with open('data/aws_services.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    async def get_aws_answer(self, question: str) -> Optional[str]:
        """Get AWS answer using free sources."""
        
        # Try AWS documentation search first
        doc_answer = await self._search_aws_docs(question)
        if doc_answer:
            return doc_answer
        
        # Try service-specific responses
        service_answer = self._get_service_info(question)
        if service_answer:
            return service_answer
        
        # Try Hugging Face with AWS context
        return await self._try_free_ai_with_aws_context(question)
    
    async def _search_aws_docs(self, question: str) -> Optional[str]:
        """Search AWS documentation (free)."""
        # AWS doesn't have a free public search API
        # But we can use pre-loaded knowledge base
        return None
    
    def _get_service_info(self, question: str) -> Optional[str]:
        """Get service info from local knowledge base."""
        question_lower = question.lower()
        
        for service, info in self.aws_services.items():
            if service.lower() in question_lower:
                return f"**{service}**: {info.get('description', 'AWS service')}\n\n" \
                       f"**Use Cases**: {info.get('use_cases', 'Various AWS workloads')}\n" \
                       f"**Pricing**: {info.get('pricing', 'Pay-as-you-go')}"
        
        return None
    
    async def _try_free_ai_with_aws_context(self, question: str) -> Optional[str]:
        """Use free AI with AWS context."""
        if not self.session or not config.huggingface_api_key:
            return None
        
        # Use Hugging Face free tier with AWS context
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {"Authorization": f"Bearer {config.huggingface_api_key}"}
        
        # Create a focused AWS prompt
        prompt = f"AWS Expert: {question}\n\nAnswer:"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            async with self.session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and data:
                        response = data[0].get("generated_text", "").strip()
                        if response and len(response) > 10:
                            return response
                elif resp.status == 503:
                    return "The AI model is currently loading. Please try again in a moment."
        except Exception as e:
            logger.warning(f"Hugging Face API error: {str(e)}")
        
        return None