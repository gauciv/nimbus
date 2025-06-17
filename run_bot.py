"""
Debug wrapper for the Nimbus Discord Bot.
Provides enhanced error handling and logging for bot startup.
"""
import sys
import traceback
import logging
import os
import asyncio

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/bot_debug.log')
    ]
)

def run_bot_with_error_handling():
    """Run the bot with enhanced error handling."""
    try:
        print("\n=== Starting Bot with Debug Wrapper ===")
        
        # Import and run the bot
        import bot
        asyncio.run(bot.main())
        
    except ModuleNotFoundError as e:
        print("\n=== Module Error ===")
        print(f"Missing module: {e}")
        print("Make sure all required packages are installed.")
        print("Try running: pip install -r requirements.txt")
        traceback.print_exc()
        sys.exit(1)
        
    except ImportError as e:
        print("\n=== Import Error ===")
        print(f"Error importing module: {e}")
        traceback.print_exc()
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n=== Bot Shutdown ===")
        print("Bot was shut down via keyboard interrupt (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        print("\n=== Fatal Error ===")
        print("An unexpected error occurred while starting the bot:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        
        # Additional debug information
        print("\nDebug Information:")
        print(f"Python version: {sys.version}")
        print(f"Operating system: {sys.platform}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        
        if hasattr(e, '__context__') and e.__context__:
            print("\nCaused by:")
            traceback.print_exception(type(e.__context__), e.__context__, e.__context__.__traceback__)
        sys.exit(1)

if __name__ == "__main__":
    run_bot_with_error_handling()