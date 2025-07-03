#!/usr/bin/env python3
"""
Documentation sync hook.
Reminds you to sync documentation to Dart when .md files are created/modified.
This is a generic example that can be customized for your project.
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


def is_dart_enabled():
    """Check if Dart sync is enabled for this project."""
    project_root = get_project_root()
    
    # Check for .claude/dart-config.json
    dart_config = project_root / '.claude' / 'dart-config.json'
    if dart_config.exists():
        try:
            with open(dart_config, 'r') as f:
                config = json.load(f)
                return config.get('enable_doc_sync', True)
        except:
            pass
    
    # Check for .claude/sync-config.json
    sync_config = project_root / '.claude' / 'sync-config.json'
    if sync_config.exists():
        try:
            with open(sync_config, 'r') as f:
                config = json.load(f)
                return config.get('dart_sync_enabled', False)
        except:
            pass
    
    # For backward compatibility and testing, enable by default if no config exists
    # Projects can explicitly disable by creating a config file
    return True


def should_sync_to_dart(file_path):
    """Determine if a file should be synced to Dart."""
    # First check if Dart sync is enabled
    if not is_dart_enabled():
        return False
    
    # Skip files in specific directories
    skip_dirs = ['.git', 'node_modules', '.next', 'dist', 'build', '.claude']
    path_parts = Path(file_path).parts
    
    for skip_dir in skip_dirs:
        if skip_dir in path_parts:
            return False
    
    # Only sync markdown files
    if not file_path.endswith('.md'):
        return False
    
    return True


def get_dart_doc_title(file_path):
    """Generate a title for the Dart doc based on file path."""
    path = Path(file_path)
    
    # Use filename without extension as base
    base_name = path.stem
    
    # Add directory context if not in root
    if path.parent != Path('.'):
        parent_name = path.parent.name
        if parent_name not in ['docs', 'documentation']:
            base_name = f"{parent_name}/{base_name}"
    
    # Convert to title case and replace separators
    title = base_name.replace('-', ' ').replace('_', ' ').title()
    
    return title


def extract_content(tool_name, tool_input):
    """Extract content from different tool inputs."""
    if tool_name == 'Write':
        return tool_input.get('content', '')
    elif tool_name == 'Edit':
        # For Edit, we'd need to read the file and apply the edit
        # For now, we'll skip Edit operations
        return None
    elif tool_name == 'MultiEdit':
        # For MultiEdit, we'd need to read the file and apply all edits
        # For now, we'll skip MultiEdit operations
        return None
    
    return None


def create_dart_sync_reminder(file_path, content):
    """Create a reminder to sync the document to Dart."""
    output = {
        "decision": "approve",
        "reason": f"Document can be synced to Dart after creation",
        "suppressOutput": False
    }
    
    # Store information for later sync
    sync_info = {
        "file_path": file_path,
        "title": get_dart_doc_title(file_path),
        "content_preview": content[:200] + "..." if len(content) > 200 else content,
        "timestamp": datetime.now().isoformat()
    }
    
    # Log the sync requirement in project directory
    project_root = get_project_root()
    claude_dir = project_root / '.claude'
    
    # Create .claude directory if it doesn't exist
    try:
        claude_dir.mkdir(exist_ok=True)
    except:
        # Fallback to home directory if can't create in project
        claude_dir = Path.home() / '.claude' / 'hooks'
    
    log_file = claude_dir / 'pending-dart-syncs.json'
    pending_syncs = []
    
    try:
        if log_file.exists():
            with open(log_file, 'r') as f:
                pending_syncs = json.load(f)
    except:
        pass
    
    # Add new sync info
    pending_syncs.append(sync_info)
    
    # Keep only recent items (last 50)
    if len(pending_syncs) > 50:
        pending_syncs = pending_syncs[-50:]
    
    try:
        with open(log_file, 'w') as f:
            json.dump(pending_syncs, f, indent=2)
    except:
        pass
    
    # Load project-specific Dart configuration
    dart_config = project_root / '.claude' / 'dart-config.json'
    folder_hint = "your preferred folder"
    
    if dart_config.exists():
        try:
            with open(dart_config, 'r') as f:
                config = json.load(f)
                default_folder = config.get('default_docs_folder')
                if default_folder:
                    folder_hint = f"folder: {default_folder}"
        except:
            pass
    
    # Provide feedback
    print(f"📝 Document '{sync_info['title']}' can be synced to Dart", file=sys.stderr)
    print(f"   💡 Use 'mcp__dart__create_doc' to sync documentation", file=sys.stderr)
    print(f"   📁 Choose {folder_hint}", file=sys.stderr)
    
    return output


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Only process Write tool (Edit/MultiEdit would need file reading)
        if tool_name != 'Write':
            sys.exit(0)
        
        # Get file path
        file_path = tool_input.get('file_path', '')
        
        # Check if this should be synced
        if not should_sync_to_dart(file_path):
            sys.exit(0)
        
        # Extract content
        content = extract_content(tool_name, tool_input)
        if content is None:
            sys.exit(0)
        
        # Create sync reminder
        output = create_dart_sync_reminder(file_path, content)
        
        # Output JSON response
        print(json.dumps(output))
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in doc sync hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()