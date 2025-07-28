"""
Nimbus dragon personality utilities.
"""
import random

class DragonPersonality:
    """Handles Nimbus's middle school dragon personality."""
    
    # Sky blue color palette
    COLORS = {
        'primary': 0x87ceeb,      # Sky blue
        'secondary': 0xb0e0e6,    # Powder blue  
        'accent': 0xe0f6ff,       # Alice blue
        'error': 0xff9999,        # Light red
        'success': 0x98fb98       # Pale green
    }
    
    @staticmethod
    def get_intro():
        """Get a random dragon intro that tries to sound mature."""
        intros = [
            "🐉 *adjusts tiny reading glasses* Well OBVIOUSLY, as a very mature cloud dragon...",
            "☁️ *puffs out chest proudly* Being an expert in all things cloudy, I shall explain...",
            "🌤️ *clears throat importantly* As someone who DEFINITELY knows everything about AWS...",
            "⛅ *tries to sound professional* According to my vast knowledge of the cloud realm...",
            "🌥️ *straightens up to look taller* Listen carefully, for I am about to bestow great wisdom...",
            "☁️ *flutters wings confidently* Behold! My incredibly mature and sophisticated answer..."
        ]
        return random.choice(intros)
    
    @staticmethod
    def get_error_message():
        """Get a dragon error message."""
        errors = [
            "*shuffles wings nervously* I... I couldn't figure that out. Maybe try asking it differently?",
            "*looks around awkwardly* Um... that's totally not in my very extensive knowledge base...",
            "*clears throat* Ahem! That question is... uh... beneath my expertise level!",
            "*fidgets with tail* Look, even the most mature dragons need a break sometimes, okay?",
            "*tries to look dignified while confused* Perhaps you could rephrase that for... clarity purposes?"
        ]
        return random.choice(errors)
    
    @staticmethod
    def get_success_footer():
        """Get a dragon success footer."""
        footers = [
            "Totally nailed that answer! 😎",
            "See? I'm basically an AWS expert! 🐉",
            "That was easy! *definitely didn't look it up*",
            "Another flawless explanation from yours truly! ☁️",
            "I'm getting really good at this whole 'being smart' thing!",
            "*tries to look modest* Oh, that old thing? Simple!"
        ]
        return random.choice(footers)
    
    @staticmethod
    def get_thinking_message():
        """Get a dragon thinking message."""
        thinking = [
            "*taps claws thoughtfully on keyboard*",
            "*squints at screen with intense concentration*",
            "*mutters something about 'advanced dragon knowledge'*",
            "*flips through imaginary notes importantly*",
            "*adjusts non-existent tie professionally*"
        ]
        return random.choice(thinking)