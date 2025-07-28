"""
AI tools to enhance cognition and provide better responses.
"""
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

class AITools:
    def __init__(self):
        self.aws_services = self._load_aws_services()
    
    def _load_aws_services(self) -> Dict:
        """Load AWS services data."""
        try:
            with open('data/aws_services.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def extract_aws_services(self, text: str) -> List[str]:
        """Extract AWS service names from text."""
        text_lower = text.lower()
        found_services = []
        
        service_names = [
            's3', 'ec2', 'lambda', 'rds', 'dynamodb', 'vpc', 'iam',
            'api gateway', 'cloudformation', 'cloudwatch', 'sns', 'sqs',
            'cognito', 'amplify', 'bedrock', 'sagemaker', 'ecs', 'eks'
        ]
        
        for service in service_names:
            if service in text_lower:
                found_services.append(service)
        
        return found_services
    
    def get_service_relationships(self, service: str) -> Dict:
        """Get related services and common combinations."""
        relationships = {
            's3': ['cloudfront', 'lambda', 'ec2', 'iam'],
            'lambda': ['api gateway', 'dynamodb', 's3', 'cloudwatch'],
            'api gateway': ['lambda', 'cognito', 'cloudwatch', 'iam'],
            'ec2': ['vpc', 'elb', 'auto scaling', 'cloudwatch'],
            'rds': ['vpc', 'ec2', 'lambda', 'cloudwatch'],
            'dynamodb': ['lambda', 'api gateway', 'cognito', 'iam']
        }
        
        return {
            'related_services': relationships.get(service.lower(), []),
            'common_patterns': self._get_architecture_patterns(service)
        }
    
    def _get_architecture_patterns(self, service: str) -> List[str]:
        """Get common architecture patterns for a service."""
        patterns = {
            'lambda': ['Serverless API', 'Event processing', 'Microservices'],
            's3': ['Static website', 'Data lake', 'Backup storage'],
            'api gateway': ['REST API', 'Microservices gateway', 'Mobile backend'],
            'dynamodb': ['Session store', 'Real-time apps', 'Gaming leaderboards']
        }
        
        return patterns.get(service.lower(), [])
    
    def analyze_question_intent(self, question: str) -> Dict:
        """Analyze what the user is trying to learn."""
        q = question.lower()
        
        intent = {
            'type': 'general',
            'complexity': 'beginner',
            'focus_areas': [],
            'suggested_followups': []
        }
        
        # Determine question type
        if any(word in q for word in ['what is', 'explain', 'define']):
            intent['type'] = 'definition'
        elif any(word in q for word in ['how to', 'how do i', 'steps']):
            intent['type'] = 'tutorial'
        elif any(word in q for word in ['vs', 'compare', 'difference']):
            intent['type'] = 'comparison'
        elif any(word in q for word in ['cost', 'price', 'pricing']):
            intent['type'] = 'pricing'
        elif any(word in q for word in ['best practice', 'recommend']):
            intent['type'] = 'best_practice'
        
        # Determine complexity
        if any(word in q for word in ['advanced', 'enterprise', 'production']):
            intent['complexity'] = 'advanced'
        elif any(word in q for word in ['intermediate', 'scaling']):
            intent['complexity'] = 'intermediate'
        
        # Extract focus areas
        services = self.extract_aws_services(question)
        intent['focus_areas'] = services
        
        return intent
    
    def get_pricing_context(self, service: str) -> str:
        """Get pricing context for a service."""
        pricing_info = {
            's3': 'Pay for storage used, requests, and data transfer. Free tier: 5GB storage.',
            'lambda': 'Pay per request and compute time. Free tier: 1M requests/month.',
            'dynamodb': 'Pay for read/write capacity and storage. Free tier: 25GB storage.',
            'api gateway': 'Pay per API call. Free tier: 1M API calls/month.',
            'ec2': 'Pay for compute time. Free tier: 750 hours t2.micro/month.'
        }
        
        return pricing_info.get(service.lower(), 'Pricing varies by usage. Check AWS pricing calculator.')
    
    def enhance_response_with_tools(self, question: str, base_response: str) -> str:
        """Enhance response using AI tools."""
        intent = self.analyze_question_intent(question)
        services = intent['focus_areas']
        
        enhanced_response = base_response
        
        # Add pricing info if relevant
        if intent['type'] == 'pricing' and services:
            pricing = self.get_pricing_context(services[0])
            enhanced_response += f"\n\n💰 **Pricing**: {pricing}"
        
        # Add related services
        if services and len(services) == 1:
            relationships = self.get_service_relationships(services[0])
            if relationships['related_services']:
                related = ', '.join(relationships['related_services'][:3])
                enhanced_response += f"\n\n🔗 **Often used with**: {related}"
        
        return enhanced_response