"""
Simple RAG implementation using local AWS knowledge base.
"""
import json
import re
from typing import List, Dict, Optional

class SimpleRAG:
    def __init__(self):
        self.knowledge_base = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """Load AWS knowledge from multiple sources."""
        knowledge = {}
        
        # Load existing data files
        files = [
            'data/aws_services.json',
            'data/aws_knowledge_base.json',
            'data/aws_docs.json'
        ]
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    knowledge.update(data)
            except:
                pass
        
        return knowledge
    
    def search_relevant_context(self, question: str) -> str:
        """Find relevant context for the question."""
        question_lower = question.lower()
        relevant_info = []
        
        # Search through knowledge base
        for key, value in self.knowledge_base.items():
            if any(word in key.lower() for word in question_lower.split()):
                if isinstance(value, dict):
                    desc = value.get('description', '')
                    use_cases = value.get('use_cases', '')
                    relevant_info.append(f"{key}: {desc} {use_cases}")
                elif isinstance(value, str):
                    relevant_info.append(f"{key}: {value}")
        
        # Return top 3 most relevant pieces
        return " | ".join(relevant_info[:3]) if relevant_info else ""
    
    def enhance_prompt(self, question: str, base_prompt: str) -> str:
        """Enhance prompt with relevant context."""
        context = self.search_relevant_context(question)
        
        if context:
            return f"{base_prompt}\n\nRelevant AWS context: {context}\n\nQuestion: {question}"
        else:
            return f"{base_prompt}\n\nQuestion: {question}"