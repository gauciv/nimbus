"""
Free AWS content client using public APIs and documentation.
"""
import aiohttp
import json
from typing import Optional
from utils.logging_config import get_logger
from utils.config import config
from utils.rag_client import SimpleRAG
from utils.response_cache import ResponseCache

logger = get_logger(__name__)

class AWSFreeClient:
    """Completely free AWS content client."""
    
    def __init__(self):
        self.session = None
        self.aws_services = self._load_aws_services()
        self.rag = SimpleRAG()
        self.cache = ResponseCache()
    
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
        """Get AWS answer using enhanced free sources."""
        
        # Check cache first
        cached_response = self.cache.get_cached_response(question)
        if cached_response:
            return cached_response
        
        # Try Groq AI first (best responses)
        groq_answer = await self._try_groq_with_rag(question)
        if groq_answer and self._is_quality_response(groq_answer):
            self.cache.cache_response(question, groq_answer)
            return groq_answer
        
        # Fallback to Hugging Face
        hf_answer = await self._try_free_ai_with_aws_context(question)
        if hf_answer and self._is_quality_response(hf_answer):
            self.cache.cache_response(question, hf_answer)
            return hf_answer
        
        # Last resort: local knowledge base (only if AI fails)
        service_answer = self._get_service_info(question)
        if service_answer:
            return service_answer
        
        return "I couldn't find information about that. Please try rephrasing your AWS question."
    
    def _is_quality_response(self, response: str) -> bool:
        """Check if response meets quality standards."""
        if not response or len(response.strip()) < 20:
            return False
        
        # Check for common bad responses
        bad_indicators = [
            'i cannot', 'i can\'t', 'sorry', 'i don\'t know',
            'as an ai', 'i\'m not able', 'i apologize'
        ]
        
        response_lower = response.lower()
        if any(indicator in response_lower for indicator in bad_indicators):
            return False
        
        # Must contain AWS-related content
        aws_indicators = [
            'aws', 'amazon', 'cloud', 'service', 'ec2', 's3', 'lambda',
            'database', 'storage', 'compute', 'serverless'
        ]
        
        if not any(indicator in response_lower for indicator in aws_indicators):
            return False
        
        return True
    
    async def _search_aws_docs(self, question: str) -> Optional[str]:
        """Search AWS documentation (free)."""
        # AWS doesn't have a free public search API
        # But we can use pre-loaded knowledge base
        return None
    
    def _get_service_info(self, question: str) -> Optional[str]:
        """Get service info from local knowledge base."""
        question_lower = question.lower()
        
        # Handle common service name variations
        service_mappings = {
            'dynamo': 'dynamodb',
            'ec2': 'ec2',
            's3': 's3',
            'lambda': 'lambda',
            'rds': 'rds'
        }
        
        # Check for service name variations
        for variant, canonical in service_mappings.items():
            if variant in question_lower:
                # Look for the canonical name in our services
                for service, info in self.aws_services.items():
                    if canonical in service.lower():
                        description = info.get('description', 'AWS service')
                        use_cases = info.get('use_cases', 'Various AWS workloads')
                        
                        return f"**{service}**: {description}\n\n**Use Cases**: {use_cases}"
        
        # Fallback to original matching
        for service, info in self.aws_services.items():
            if service.lower() in question_lower:
                description = info.get('description', 'AWS service')
                use_cases = info.get('use_cases', 'Various AWS workloads')
                
                return f"**{service}**: {description}\n\n**Use Cases**: {use_cases}"
        
        return None
    
    async def _try_free_ai_with_aws_context(self, question: str) -> Optional[str]:
        """Use free AI with AWS context and guardrails."""
        if not self.session or not config.huggingface_api_key:
            return None
        
        # Check if question is AWS-related first
        if not self._is_aws_related(question):
            return "I can only answer AWS and cloud computing questions. Please ask about AWS services, architecture, pricing, or best practices."
        
        # Use a better model for AWS questions
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
        headers = {"Authorization": f"Bearer {config.huggingface_api_key}"}
        
        # Smart context-aware prompting
        context = self._get_question_context(question)
        prompt = f"AWS Expert: {context}\n\nQ: {question}\nA:"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.4,
                "top_p": 0.9,
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
    
    def _is_aws_related(self, question: str) -> bool:
        """Smart AWS detection with proper guardrails."""
        q = question.lower().replace('-', ' ').replace('_', ' ')
        
        # First check for obvious non-AWS topics
        non_aws_topics = [
            'python', 'javascript', 'java', 'c++', 'html', 'css', 'react', 'vue', 'angular',
            'cooking', 'recipe', 'food', 'music', 'movie', 'game', 'sport', 'weather',
            'math', 'physics', 'chemistry', 'biology', 'history', 'geography'
        ]
        
        for topic in non_aws_topics:
            if topic in q and 'aws' not in q and 'cloud' not in q:
                return False
        
        # Direct AWS mentions
        if any(word in q for word in ['aws', 'amazon web services', 'amazon cloud']):
            return True
        
        # AWS services (including common variations)
        aws_services = [
            's3', 'ec2', 'lambda', 'rds', 'dynamodb', 'dynamo', 'vpc', 'iam',
            'api gateway', 'gateway api', 'apigateway', 'cognito', 'amplify',
            'cloudformation', 'cloudwatch', 'sns', 'sqs', 'bedrock', 'sagemaker',
            'ecs', 'eks', 'fargate', 'route53', 'cloudfront', 'elb', 'elastic load balancer',
            'redshift', 'athena', 'glue', 'kinesis', 'step functions', 'eventbridge',
            'elastic beanstalk', 'lightsail', 'workspaces', 'connect'
        ]
        
        for service in aws_services:
            if service in q:
                return True
        
        # Cloud/tech terms (only if they seem AWS-related)
        cloud_terms = ['cloud', 'serverless', 'microservices', 'container']
        if any(term in q for term in cloud_terms):
            return True
        
        # Infrastructure terms
        infra_terms = ['deployment', 'hosting', 'scaling', 'load balancer', 'cdn', 'database']
        if any(term in q for term in infra_terms):
            return True
        
        return False
    
    def _try_rag_answer(self, question: str) -> Optional[str]:
        """Try to answer using RAG with local knowledge."""
        context = self.rag.search_relevant_context(question)
        if context and len(context) > 50:
            return f"Based on AWS knowledge: {context}"
        return None
    
    async def _try_groq_with_rag(self, question: str) -> Optional[str]:
        """Try Groq API with RAG context."""
        try:
            from utils.groq_client import GroqClient
            
            # Enhance question with RAG context
            context = self.rag.search_relevant_context(question)
            if context:
                enhanced_question = f"Context: {context}\n\nQuestion: {question}"
            else:
                enhanced_question = question
            
            async with GroqClient() as client:
                return await client.get_aws_answer(enhanced_question)
        except:
            return None
    
    async def _try_groq(self, question: str) -> Optional[str]:
        """Try Groq API (free 6000 requests/day)."""
        try:
            from utils.groq_client import GroqClient
            async with GroqClient() as client:
                return await client.get_aws_answer(question)
        except:
            return None
    
    def _get_question_context(self, question: str) -> str:
        """Add smart context based on question type."""
        q = question.lower()
        
        if 'cost' in q or 'price' in q:
            return "AWS uses pay-as-you-go pricing with free tier."
        elif 'vs' in q or 'compare' in q:
            return "AWS services have different use cases and trade-offs."
        elif 'security' in q:
            return "AWS follows shared responsibility security model."
        elif 'serverless' in q or 'lambda' in q:
            return "Serverless eliminates server management."
        elif 'database' in q:
            return "AWS offers managed databases for different needs."
        else:
            return "AWS provides scalable cloud services."
    
    def _enhance_with_sources(self, response: str, question: str) -> str:
        """Add relevant AWS documentation links to response."""
        # Keep response reasonable length but not too short
        if len(response) > 500:
            response = response[:497] + "..."
        
        # Add relevant documentation links
        sources = []
        question_lower = question.lower()
        
        # Service-specific documentation
        service_docs = {
            'ec2': 'https://docs.aws.amazon.com/ec2/',
            's3': 'https://docs.aws.amazon.com/s3/',
            'lambda': 'https://docs.aws.amazon.com/lambda/',
            'rds': 'https://docs.aws.amazon.com/rds/',
            'dynamodb': 'https://docs.aws.amazon.com/dynamodb/',
            'vpc': 'https://docs.aws.amazon.com/vpc/',
            'iam': 'https://docs.aws.amazon.com/iam/',
            'cloudformation': 'https://docs.aws.amazon.com/cloudformation/',
            'api gateway': 'https://docs.aws.amazon.com/apigateway/'
        }
        
        # Add specific service docs
        for service, doc_url in service_docs.items():
            if service in question_lower:
                sources.append(f"[{service.upper()} Docs]({doc_url})")
                break
        
        # Add general AWS resources
        if 'pricing' in question_lower or 'cost' in question_lower:
            sources.append('[AWS Pricing](https://aws.amazon.com/pricing/)')
        
        if 'architecture' in question_lower or 'design' in question_lower:
            sources.append('[AWS Architecture Center](https://aws.amazon.com/architecture/)')
        
        if 'certification' in question_lower or 'learning' in question_lower:
            sources.append('[AWS Training](https://aws.amazon.com/training/)')
        
        # Always add general documentation
        if not sources:
            sources.append('[AWS Documentation](https://docs.aws.amazon.com/)')
        
        # Format response with single source
        if sources:
            response += f"\n\n📚 **Learn more:** {sources[0]}"
        
        return response