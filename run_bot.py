import sys
import traceback
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_debug.log')
    ]
)

try:
    print("\n=== Starting Bot with Debug Wrapper ===")
    import bot
except Exception as e:
    print("\n=== Fatal Error ===")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
