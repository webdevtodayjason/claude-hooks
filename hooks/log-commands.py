#!/usr/bin/env python3
"""
Command logging hook.
Logs all Bash commands with timestamps and descriptions.
"""
import json
import sys
from datetime import datetime
from pathlib import Path


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        
        # Only log Bash commands
        if tool_name != 'Bash':
            sys.exit(0)
        
        # Extract command info
        command = input_data.get('tool_input', {}).get('command', '')
        description = input_data.get('tool_input', {}).get('description', 'No description')
        session_id = input_data.get('session_id', 'unknown')
        
        # Create log entry
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{session_id[:8]}] {command} - {description}\n"
        
        # Append to log file
        log_file = Path.home() / '.claude' / 'bash-command-log.txt'
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to command log: {e}", file=sys.stderr)
        
        # Also create a daily summary log
        daily_log = Path.home() / '.claude' / 'hooks' / f"commands-{datetime.now().strftime('%Y-%m-%d')}.log"
        try:
            daily_log.parent.mkdir(exist_ok=True)
            with open(daily_log, 'a') as f:
                f.write(log_entry)
        except:
            pass
        
        # Track command frequency
        stats_file = Path.home() / '.claude' / 'hooks' / 'command-stats.json'
        try:
            stats = {}
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            
            # Extract base command
            base_cmd = command.split()[0] if command else 'unknown'
            stats[base_cmd] = stats.get(base_cmd, 0) + 1
            
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except:
            pass
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Don't fail the command due to logging errors
        print(f"Warning: Command logging error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()