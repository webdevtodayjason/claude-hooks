#!/usr/bin/env python3
"""
Context Forge Stop Hook
Detects if compaction occurred and enforces context refresh for Context Forge projects
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

def log_debug(message):
    """Log debug information to a file"""
    log_file = Path.home() / ".claude" / "context-forge-hook.log"
    log_file.parent.mkdir(exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def is_context_forge_project():
    """Check if current directory is a Context Forge project"""
    cwd = Path.cwd()
    
    # Check for Context Forge markers
    has_claude_md = (cwd / "CLAUDE.md").exists()
    has_docs = (cwd / "Docs" / "Implementation.md").exists()
    has_prps = (cwd / "PRPs").is_dir()
    has_config = (cwd / ".context-forge" / "config.json").exists()
    
    return has_claude_md and (has_docs or has_prps or has_config)

def check_for_recent_compaction():
    """Check if a compaction occurred recently"""
    marker_file = Path.home() / ".claude" / "context-forge-compaction-marker"
    
    if marker_file.exists():
        # Check if marker is recent (within last 5 minutes)
        stat = marker_file.stat()
        file_time = datetime.fromtimestamp(stat.st_mtime)
        if datetime.now() - file_time < timedelta(minutes=5):
            log_debug("Recent compaction detected from marker file")
            # Remove marker to prevent repeated triggers
            marker_file.unlink()
            return True
            
    return False

def create_compaction_marker():
    """Create a marker file to track compaction"""
    marker_file = Path.home() / ".claude" / "context-forge-compaction-marker"
    marker_file.parent.mkdir(exist_ok=True)
    marker_file.touch()
    log_debug("Created compaction marker")

def get_context_refresh_instructions():
    """Generate detailed context refresh instructions"""
    instructions = []
    
    # Check what files exist and build appropriate instructions
    cwd = Path.cwd()
    
    instructions.append("Context refresh required after compaction. Please follow these steps:")
    instructions.append("")
    
    # 1. CLAUDE.md - Always first
    if (cwd / "CLAUDE.md").exists():
        instructions.append("1. Read CLAUDE.md completely to restore project rules, conventions, and technical guidelines")
    
    # 2. Implementation stage
    if (cwd / "Docs" / "Implementation.md").exists():
        instructions.append("2. Check Docs/Implementation.md and identify which stage you were working on")
        instructions.append("   - Look for the most recent stage mentioned in our conversation")
        instructions.append("   - Review the checklist for that stage")
    
    # 3. PRPs
    prp_dir = cwd / "PRPs"
    if prp_dir.exists():
        prp_files = list(prp_dir.glob("*.md"))
        if prp_files:
            instructions.append("3. Review the relevant PRP file:")
            for prp in prp_files[:3]:  # List up to 3 PRPs
                instructions.append(f"   - PRPs/{prp.name}")
    
    # 4. Bug tracking
    if (cwd / "Docs" / "Bug_tracking.md").exists():
        instructions.append("4. Check Docs/Bug_tracking.md for any documented issues")
    
    # 5. Project structure
    if (cwd / "Docs" / "project_structure.md").exists():
        instructions.append("5. Review Docs/project_structure.md if you need to understand file organization")
    
    instructions.append("")
    instructions.append("After reading these files, continue with the task at hand.")
    
    return "\n".join(instructions)

def main():
    """Main hook execution"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        session_id = input_data.get("session_id", "unknown")
        transcript_path = input_data.get("transcript_path", "")
        stop_hook_active = input_data.get("stop_hook_active", False)
        
        log_debug(f"Stop hook triggered: session={session_id}, stop_hook_active={stop_hook_active}")
        
        # Avoid infinite loops
        if stop_hook_active:
            log_debug("Stop hook already active, exiting to prevent loop")
            sys.exit(0)
        
        # Check if this is a Context Forge project
        if not is_context_forge_project():
            log_debug("Not a Context Forge project, exiting normally")
            sys.exit(0)
        
        # Check for recent compaction
        # Note: In real implementation, we'd check the transcript for compaction events
        # For now, we'll use the PreCompact marker approach
        if check_for_recent_compaction():
            log_debug("Recent compaction detected, enforcing context refresh")
            
            # Get refresh instructions
            instructions = get_context_refresh_instructions()
            
            # Output JSON response to block and provide instructions
            response = {
                "decision": "block",
                "reason": instructions
            }
            
            print(json.dumps(response))
            log_debug("Sent context refresh instructions")
        else:
            log_debug("No recent compaction detected")
            # Normal exit
            sys.exit(0)
            
    except Exception as e:
        log_debug(f"Error in Stop hook: {e}")
        # Exit gracefully on error
        sys.exit(0)

if __name__ == "__main__":
    main()