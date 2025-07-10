#!/usr/bin/env python3
"""
Context Forge PreCompact Hook
Detects Context Forge projects and prepares context refresh instructions
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

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
    
    # Log what we found
    log_debug(f"Context Forge detection in {cwd}:")
    log_debug(f"  CLAUDE.md: {has_claude_md}")
    log_debug(f"  Docs/Implementation.md: {has_docs}")
    log_debug(f"  PRPs/: {has_prps}")
    log_debug(f"  .context-forge/config.json: {has_config}")
    
    return has_claude_md and (has_docs or has_prps or has_config)

def extract_current_stage(transcript_path):
    """Extract current implementation stage from transcript"""
    try:
        # Read last few messages to find stage references
        if Path(transcript_path).exists():
            with open(transcript_path, 'r') as f:
                content = f.read()
                
            # Look for stage references
            stage_markers = ["Stage 1", "Stage 2", "Stage 3", "Stage 4"]
            for marker in reversed(stage_markers):
                if marker.lower() in content.lower():
                    log_debug(f"Found reference to {marker}")
                    return marker
                    
    except Exception as e:
        log_debug(f"Error reading transcript: {e}")
    
    return None

def get_active_prp():
    """Determine which PRP file is most relevant"""
    prp_dir = Path.cwd() / "PRPs"
    
    if not prp_dir.exists():
        return None
        
    # Priority order for PRPs
    prp_priority = ["base.md", "planning.md", "validation-gate.md", "spec.md"]
    
    for prp in prp_priority:
        if (prp_dir / prp).exists():
            return prp
            
    # Return first .md file found
    prp_files = list(prp_dir.glob("*.md"))
    if prp_files:
        return prp_files[0].name
        
    return None

def create_compaction_marker():
    """Create a marker file for the Stop hook to detect"""
    marker_file = Path.home() / ".claude" / "context-forge-compaction-marker"
    marker_file.parent.mkdir(exist_ok=True)
    marker_file.touch()
    log_debug("Created compaction marker for Stop hook")

def main():
    """Main hook execution"""
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)
        
        session_id = input_data.get("session_id", "unknown")
        transcript_path = input_data.get("transcript_path", "")
        trigger = input_data.get("trigger", "unknown")
        custom_instructions = input_data.get("custom_instructions", "")
        
        log_debug(f"PreCompact hook triggered: trigger={trigger}, session={session_id}")
        
        # Check if this is a Context Forge project
        if not is_context_forge_project():
            log_debug("Not a Context Forge project, exiting normally")
            sys.exit(0)
            
        log_debug("Context Forge project detected!")
        
        # Create marker for Stop hook
        create_compaction_marker()
        
        # Extract current stage
        current_stage = extract_current_stage(transcript_path)
        active_prp = get_active_prp()
        
        # Prepare refresh instructions
        refresh_parts = []
        
        # Always start with CLAUDE.md
        refresh_parts.append("IMPORTANT: Context refresh required after compaction.")
        refresh_parts.append("1. Re-read CLAUDE.md to restore project rules and conventions")
        
        # Add stage information
        if current_stage:
            refresh_parts.append(f"2. Check Docs/Implementation.md - you are currently working on {current_stage}")
        else:
            refresh_parts.append("2. Check Docs/Implementation.md to identify current development stage")
            
        # Add PRP information
        if active_prp:
            refresh_parts.append(f"3. Review PRPs/{active_prp} for implementation guidelines")
            
        # Add bug tracking if exists
        if (Path.cwd() / "Docs" / "Bug_tracking.md").exists():
            refresh_parts.append("4. Check Docs/Bug_tracking.md for known issues")
            
        refresh_message = "\n".join(refresh_parts)
        
        # For manual trigger, append to custom instructions
        if trigger == "manual" and custom_instructions:
            refresh_message = f"{custom_instructions}\n\n{refresh_message}"
            
        # Output JSON response
        response = {
            "decision": "block",
            "reason": refresh_message,
            "suppressOutput": False
        }
        
        print(json.dumps(response))
        log_debug(f"Sent refresh instructions for post-compaction")
        
    except Exception as e:
        log_debug(f"Error in PreCompact hook: {e}")
        # Exit gracefully on error
        sys.exit(0)

if __name__ == "__main__":
    main()