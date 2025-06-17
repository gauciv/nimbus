"""
Debug wrapper for the Nimbus Discord Bot.
"""
import sys
import traceback
import logging
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Set up logging with minimal output
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/bot_debug.log')
    ]
)

# Disable verbose logging from discord.py
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('discord.http').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)

def run_bot():
    """Run the bot with clean error handling."""
    try:
        print("\n=== Nimbus Discord Bot v2 ===")
        
        # Import and run the bot
        import bot
        bot.main()
        
    except ModuleNotFoundError as e:
        print(f"\n❌ Missing module: {e}")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Bot was shut down via keyboard interrupt (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {type(e).__name__}: {str(e)}")
        
        # Only show traceback for non-obvious errors
        if not isinstance(e, (FileNotFoundError, PermissionError)):
            print("\nTraceback:")
            traceback.print_exc()
        
        sys.exit(1)

if __name__ == "__main__":
    run_bot()