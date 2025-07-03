#!/usr/bin/env python3
"""
Session end summary hook.
Reminds about pending Dart updates, documentation sync, and session activities.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def get_project_root():
    """Get the current project root directory."""
    try:
        # Try to find git root
        result = os.popen('git rev-parse --show-toplevel 2>/dev/null').read().strip()
        if result:
            return Path(result)
    except:
        pass
    # Fallback to current directory
    return Path.cwd()


def is_dart_project():
    """Check if the current project uses Dart integration."""
    project_root = get_project_root()
    
    # Check for .claude/dart-config.json
    dart_config = project_root / '.claude' / 'dart-config.json'
    if dart_config.exists():
        return True
    
    # Check for CLAUDE.md with Dart references
    claude_md = Path.home() / '.claude' / 'CLAUDE.md'
    if claude_md.exists():
        try:
            with open(claude_md, 'r') as f:
                content = f.read()
                # Look for Dart-specific mentions
                if 'mcp__dart__' in content or 'Dart MCP' in content:
                    return True
        except:
            pass
    
    return False


def read_pending_syncs():
    """Read pending documentation syncs from project directory."""
    project_root = get_project_root()
    sync_file = project_root / '.claude' / 'pending-dart-syncs.json'
    
    if sync_file.exists():
        try:
            with open(sync_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return []


def read_command_log():
    """Read recent commands from the log."""
    log_file = Path.home() / '.claude' / 'bash-command-log.txt'
    recent_commands = []
    
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 10 commands
                recent_commands = lines[-10:] if len(lines) > 10 else lines
        except:
            pass
    
    return recent_commands


def analyze_session_activity(transcript_path):
    """Analyze the session transcript for key activities."""
    activities = {
        'dart_tasks_created': 0,
        'dart_tasks_updated': 0,
        'files_created': 0,
        'files_modified': 0,
        'commits_made': 0,
        'tests_run': 0,
        'has_uncommitted_changes': False
    }
    
    try:
        # Check for uncommitted changes
        result = os.popen('git status --porcelain 2>/dev/null').read()
        if result.strip():
            activities['has_uncommitted_changes'] = True
    except:
        pass
    
    return activities


def load_project_config():
    """Load project-specific configuration."""
    project_root = get_project_root()
    config_file = project_root / '.claude' / 'session-summary.json'
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default configuration
    return {
        "show_dart_reminders": is_dart_project(),
        "show_git_reminders": True,
        "custom_reminders": []
    }


def generate_reminders(activities, pending_syncs):
    """Generate reminder messages based on session activities."""
    reminders = []
    config = load_project_config()
    
    # Dart-specific reminders (only if project uses Dart)
    if config.get('show_dart_reminders', False):
        # Check for pending documentation syncs
        if pending_syncs:
            reminders.append(f"📝 {len(pending_syncs)} document(s) pending sync to Dart:")
            for sync in pending_syncs[:3]:  # Show first 3
                reminders.append(f"   • {sync.get('title', 'Unknown')}")
            if len(pending_syncs) > 3:
                reminders.append(f"   • ... and {len(pending_syncs) - 3} more")
            reminders.append("   Run mcp__dart__create_doc to sync them")
        
        # Dart task reminders
        reminders.append("\n📋 Dart Task Reminders:")
        reminders.append("• Update task status if you worked on any tasks")
        reminders.append("• Add comments to tasks for progress tracking")
        reminders.append("• Mark completed tasks as 'Done'")
    
    # Git reminders (general)
    if config.get('show_git_reminders', True):
        # Check for uncommitted changes
        if activities.get('has_uncommitted_changes'):
            reminders.append("\n💾 You have uncommitted changes - consider committing your work")
    
    # Custom project-specific reminders
    custom_reminders = config.get('custom_reminders', [])
    if custom_reminders:
        reminders.append("\n🔧 Project-Specific Reminders:")
        for reminder in custom_reminders:
            reminders.append(f"• {reminder}")
    
    # Only add general workflow reminders if no custom ones are provided
    if not custom_reminders and not config.get('show_dart_reminders', False):
        reminders.append("\n🔧 General Reminders:")
        reminders.append("• Review and commit your changes")
        reminders.append("• Run tests before committing")
        reminders.append("• Update documentation as needed")
    
    return reminders


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        stop_hook_active = input_data.get('stop_hook_active', False)
        transcript_path = input_data.get('transcript_path', '')
        
        # Don't create infinite loops
        if stop_hook_active:
            sys.exit(0)
        
        # Read pending syncs
        pending_syncs = read_pending_syncs()
        
        # Analyze session activity
        activities = analyze_session_activity(transcript_path)
        
        # Generate reminders
        reminders = generate_reminders(activities, pending_syncs)
        
        # Build the response
        if reminders:
            reminder_text = "\n".join(reminders)
            
            # Output JSON response to continue with reminders
            response = {
                "decision": "block",
                "reason": f"Session Summary:\n\n{reminder_text}\n\nPlease review these items before ending the session."
            }
            
            print(json.dumps(response))
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Don't fail the hook on errors
        sys.exit(0)


if __name__ == "__main__":
    main()