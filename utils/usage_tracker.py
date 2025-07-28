"""
Track API usage and bot statistics.
"""
import json
from datetime import datetime, date
from typing import Dict

class UsageTracker:
    def __init__(self, stats_file='data/usage_stats.json'):
        self.stats_file = stats_file
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load usage statistics."""
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'total_questions': 0,
                'groq_requests': 0,
                'hf_requests': 0,
                'cache_hits': 0,
                'daily_stats': {},
                'last_reset': str(date.today())
            }
    
    def _save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass
    
    def _check_daily_reset(self):
        """Reset daily counters if new day."""
        today = str(date.today())
        if self.stats['last_reset'] != today:
            self.stats['daily_stats'][today] = {
                'questions': 0,
                'groq_requests': 0,
                'hf_requests': 0,
                'cache_hits': 0
            }
            self.stats['last_reset'] = today
    
    def track_question(self, source='unknown'):
        """Track a question asked."""
        self._check_daily_reset()
        today = str(date.today())
        
        self.stats['total_questions'] += 1
        self.stats['daily_stats'][today]['questions'] += 1
        
        if source == 'groq':
            self.stats['groq_requests'] += 1
            self.stats['daily_stats'][today]['groq_requests'] += 1
        elif source == 'huggingface':
            self.stats['hf_requests'] += 1
            self.stats['daily_stats'][today]['hf_requests'] += 1
        elif source == 'cache':
            self.stats['cache_hits'] += 1
            self.stats['daily_stats'][today]['cache_hits'] += 1
        
        self._save_stats()
    
    def get_usage_summary(self) -> str:
        """Get usage summary string."""
        today = str(date.today())
        daily = self.stats['daily_stats'].get(today, {})
        
        groq_remaining = max(0, 6000 - self.stats['groq_requests'])
        
        return (f"📊 **Usage Stats**\n"
                f"• Total questions: {self.stats['total_questions']}\n"
                f"• Today: {daily.get('questions', 0)} questions\n"
                f"• Groq remaining: {groq_remaining}/6000\n"
                f"• Cache efficiency: {self.stats['cache_hits']}/{self.stats['total_questions']}")
    
    def get_stats(self) -> Dict:
        """Get raw statistics."""
        return self.stats