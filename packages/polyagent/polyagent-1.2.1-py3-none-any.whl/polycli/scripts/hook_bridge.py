#!/usr/bin/env python3
"""
PolyCLI Hook Bridge - Captures Claude Code events and writes to event file.

This script is installed as 'polycli-hook' console command and is meant to be
configured as a Claude Code hook to capture real-time events.
"""

import json
import sys
import os
import fcntl
from datetime import datetime
from pathlib import Path


def main():
    """Main entry point for hook bridge."""
    try:
        # Read hook input from stdin
        data = json.load(sys.stdin)
        
        # Add timestamp for ordering
        data['polycli_timestamp'] = datetime.now().isoformat()
        
        # @@@ event-file-id - Use environment variable if set, else fall back to session_id
        # This prevents collisions when multiple Claude instances run simultaneously
        event_file_id = os.environ.get('POLYCLI_EVENT_FILE_ID')
        if not event_file_id:
            # Fallback: use Claude's session_id
            event_file_id = data.get('session_id', 'unknown')
        
        # Determine event file path
        event_dir = Path('/tmp/polycli-events')
        event_dir.mkdir(exist_ok=True)
        event_file = event_dir / f'{event_file_id}.jsonl'
        
        # Append to event file with locking
        with open(event_file, 'a') as f:
            # @@@ File locking - Ensure atomic writes even with rapid events
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(json.dumps(data) + '\n')
            f.flush()  # Ensure it's written immediately
            fcntl.flock(f, fcntl.LOCK_UN)
        
        # Always exit 0 to not interfere with Claude Code
        sys.exit(0)
        
    except Exception as e:
        # Log errors but don't block Claude Code
        error_file = Path('/tmp/polycli-events/errors.log')
        error_file.parent.mkdir(exist_ok=True)
        with open(error_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Error: {e}\n")
        
        # Exit cleanly
        sys.exit(0)


if __name__ == '__main__':
    main()