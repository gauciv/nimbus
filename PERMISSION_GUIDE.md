# Permission Levels Guide

## Usage
Import and use permission decorators consistently:

```python
from utils.permission_levels import admin_only, core_team_only, everyone

@app_commands.command(name="example")
@admin_only()  # or @core_team_only() or @everyone()
async def example_command(self, interaction):
    pass
```

## Permission Levels

### Admin Only (`@admin_only()`)
- All setup commands (`/setup`, `/setup_channels`, `/setup_core_team`, etc.)
- Configuration commands (`/update_channel_config`)
- Debug commands (`/debug_tips`, `/reload_tips`, etc.)

### Core Team Only (`@core_team_only()`)
- Event management (`/event`, `/cancel_event`)
- Announcements (`/announce`, `/topic`)
- Content management commands

### Everyone (`@everyone()`)
- Information commands (`/aws`, `/docs`, `/about`)
- User interaction commands (`/poll`, `/spotlight`)
- Help commands

## Current Issues to Fix
Commands with inconsistent permissions that need updating:
- Some setup commands missing admin checks
- Event commands with mixed permission levels
- Debug commands with different decorators