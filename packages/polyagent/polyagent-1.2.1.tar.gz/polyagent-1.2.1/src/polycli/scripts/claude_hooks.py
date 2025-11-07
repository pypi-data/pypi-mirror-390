"""
Claude Code hooks management for PolyCLI integration.

This module manages Claude Code hook configurations to enable real-time
event streaming from Claude Code to PolyCLI.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
from datetime import datetime


class ClaudeHooksManager:
    """Manage Claude Code hooks configuration."""
    
    # Hook events we want to monitor
    MONITORED_EVENTS = [
        'PreToolUse',
        'PostToolUse',
        'UserPromptSubmit',
        'Stop',
        'SessionStart',
        'SessionEnd',
        'Notification'
    ]
    
    def __init__(self, scope: str = 'local'):
        """
        Initialize hooks manager.
        
        Args:
            scope: 'local' for project settings, 'global' for user settings
        """
        self.scope = scope
        self.settings_path = self._get_settings_path()
        
    def _get_settings_path(self) -> Path:
        """Get the path to Claude settings file."""
        if self.scope == 'global':
            # Global user settings
            home = Path.home()
            return home / '.claude' / 'settings.json'
        else:
            # Local project settings
            cwd = Path.cwd()
            return cwd / '.claude' / 'settings.json'
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load current settings or return empty dict."""
        if not self.settings_path.exists():
            return {}
        
        try:
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_settings(self, settings: Dict[str, Any]) -> None:
        """Save settings to file."""
        # Create directory if needed
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing settings
        if self.settings_path.exists():
            backup_path = self.settings_path.with_suffix('.json.backup')
            shutil.copy2(self.settings_path, backup_path)
        
        # Write new settings
        with open(self.settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def _get_hook_command(self) -> str:
        """Get the hook command that will be used."""
        import sys
        return f'"{sys.executable}" -m polycli.scripts.hook_bridge'
    
    def install_bridge_hooks(self, command: str = None) -> bool:
        """
        Install PolyCLI bridge hooks for all monitored events.
        
        Args:
            command: Command to execute (default: auto-detect current Python)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Auto-detect current Python environment if not specified
            if command is None:
                import sys
                # Use the exact Python interpreter that has PolyCLI installed
                command = f'"{sys.executable}" -m polycli.scripts.hook_bridge'
            
            settings = self._load_settings()
            
            # Initialize hooks section if needed
            if 'hooks' not in settings:
                settings['hooks'] = {}
            
            # Add hooks for each event type
            for event in self.MONITORED_EVENTS:
                hook_config = {
                    'hooks': [
                        {
                            'type': 'command',
                            'command': command,
                            'timeout': 5  # 5 seconds should be plenty
                        }
                    ]
                }
                
                # For tool-related events, add matcher
                if event in ['PreToolUse', 'PostToolUse']:
                    hook_config['matcher'] = '*'  # Match all tools
                
                # Initialize event array if needed
                if event not in settings['hooks']:
                    settings['hooks'][event] = []
                
                # Check if already installed
                already_installed = False
                for existing in settings['hooks'][event]:
                    if existing.get('hooks', [{}])[0].get('command') == command:
                        already_installed = True
                        break
                
                if not already_installed:
                    settings['hooks'][event].append(hook_config)
            
            # Save updated settings
            self._save_settings(settings)
            return True
            
        except Exception as e:
            print(f"Error installing hooks: {e}")
            return False
    
    def uninstall_bridge_hooks(self, command: str = None) -> bool:
        """
        Remove PolyCLI bridge hooks.
        
        Args:
            command: Command to match for removal (default: auto-detect)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Auto-detect current Python environment if not specified
            if command is None:
                import sys
                command = f'"{sys.executable}" -m polycli.scripts.hook_bridge'
            
            settings = self._load_settings()
            
            if 'hooks' not in settings:
                return True  # Nothing to uninstall
            
            # Remove hooks for each event type
            for event in self.MONITORED_EVENTS:
                if event not in settings['hooks']:
                    continue
                
                # Filter out our hooks
                settings['hooks'][event] = [
                    hook for hook in settings['hooks'][event]
                    if not any(
                        h.get('command') == command 
                        for h in hook.get('hooks', [])
                    )
                ]
                
                # Clean up empty arrays
                if not settings['hooks'][event]:
                    del settings['hooks'][event]
            
            # Clean up empty hooks section
            if settings['hooks'] == {}:
                del settings['hooks']
            
            # Save updated settings
            self._save_settings(settings)
            return True
            
        except Exception as e:
            print(f"Error uninstalling hooks: {e}")
            return False
    
    def list_hooks(self) -> Dict[str, List[Dict]]:
        """
        List current hooks configuration.
        
        Returns:
            Dictionary of event names to hook configurations
        """
        settings = self._load_settings()
        return settings.get('hooks', {})
    
    def is_installed(self, command: str = None) -> bool:
        """
        Check if PolyCLI hooks are installed.
        
        Args:
            command: Command to check for (default: checks for any PolyCLI hooks)
            
        Returns:
            True if hooks are installed, False otherwise
        """
        hooks = self.list_hooks()
        
        # If no command specified, check for any PolyCLI-related hooks
        if command is None:
            import sys
            # Check for both possible formats
            possible_commands = [
                f'"{sys.executable}" -m polycli.scripts.hook_bridge',
                f'{sys.executable} -m polycli.scripts.hook_bridge',  # Without quotes
                'polycli-cchook-bridge',  # Old format
                'python -m polycli.scripts.hook_bridge',  # Generic Python
                'python3 -m polycli.scripts.hook_bridge'  # Python3 specific
            ]
        else:
            possible_commands = [command]
        
        for event in self.MONITORED_EVENTS:
            if event in hooks:
                for hook_config in hooks[event]:
                    for hook in hook_config.get('hooks', []):
                        hook_command = hook.get('command', '')
                        # Check if any of our possible commands match
                        for cmd in possible_commands:
                            if hook_command == cmd or 'polycli.scripts.hook_bridge' in hook_command:
                                return True
        
        return False


# CLI interface for testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m polycli.scripts.claude_hooks [install|uninstall|list|check]")
        sys.exit(1)
    
    action = sys.argv[1]
    scope = sys.argv[2] if len(sys.argv) > 2 else 'local'
    
    manager = ClaudeHooksManager(scope=scope)
    
    if action == 'install':
        if manager.install_bridge_hooks():
            print(f"✓ Installed PolyCLI hooks in {scope} settings")
        else:
            print(f"✗ Failed to install hooks")
            
    elif action == 'uninstall':
        if manager.uninstall_bridge_hooks():
            print(f"✓ Uninstalled PolyCLI hooks from {scope} settings")
        else:
            print(f"✗ Failed to uninstall hooks")
            
    elif action == 'list':
        hooks = manager.list_hooks()
        if hooks:
            print(json.dumps(hooks, indent=2))
        else:
            print("No hooks configured")
            
    elif action == 'check':
        if manager.is_installed():
            print(f"✓ PolyCLI hooks are installed in {scope} settings")
        else:
            print(f"✗ PolyCLI hooks are not installed in {scope} settings")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)