"""
Permission level decorators for consistent command access control.
"""
from discord import app_commands
from utils.permissions import is_admin, is_core_team

# Permission level decorators
def admin_only():
    """Decorator for commands that require administrator permissions."""
    return is_admin()

def core_team_only():
    """Decorator for commands that require Core Team role."""
    return is_core_team()

def everyone():
    """Decorator for commands available to everyone (no restrictions)."""
    def decorator(func):
        return func
    return decorator

# Permission level mapping for easy reference
PERMISSION_LEVELS = {
    'admin': admin_only,
    'core_team': core_team_only, 
    'everyone': everyone
}