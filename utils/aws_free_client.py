"""
Free AWS content client using public APIs and documentation.
"""
import aiohttp
import json
from typing import Optional
from utils.logging_config import get_logger

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
        if not self.session:
            return None
        
        # Use Hugging Face free tier with AWS context
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        
        aws_context = ("You are an AWS expert assistant. Answer questions about "
                      "Amazon Web Services with accurate, helpful information.")
        
        payload = {
            "inputs": f"{aws_context}\nUser: {question}\nAWS Expert:",
            "parameters": {"max_length": 200, "temperature": 0.7}
        }
        
        try:
            async with self.session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and data:
                        response = data[0].get("generated_text", "")
                        # Extract only the assistant's response
                        if "AWS Expert:" in response:
                            return response.split("AWS Expert:")[-1].strip()
        except Exception as e:
            logger.warning("Free AI request failed", error=str(e))
        
        return None