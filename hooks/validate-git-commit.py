#!/usr/bin/env python3
"""
Git commit message validation hook.
Enforces commit standards and blocks co-authored commits per project rules.
"""
import json
import re
import sys


def validate_commit_message(message):
    """Validate commit message against project standards."""
    errors = []
    warnings = []
    
    # Check for Co-Authored-By (blocked per project rules)
    if "Co-Authored-By" in message or "co-authored-by" in message.lower():
        errors.append("Co-authored commits are not allowed per project rules")
    
    # Check for Claude signature (should be removed)
    if "🤖 Generated with [Claude Code]" in message or "🤖 Generated with Claude" in message:
        errors.append("Remove Claude signature from commit messages")
    
    # Extract the main commit message (first line)
    lines = message.strip().split('\n')
    if not lines:
        errors.append("Empty commit message")
        return errors, warnings
    
    main_message = lines[0].strip()
    
    # Check message length
    if len(main_message) > 72:
        warnings.append(f"First line should be ≤72 characters (current: {len(main_message)})")
    elif len(main_message) < 10:
        errors.append("Commit message too short (minimum 10 characters)")
    
    # Check for conventional commit format (optional but recommended)
    conventional_pattern = r'^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?: .+'
    if re.match(conventional_pattern, main_message):
        # Validate conventional commit format
        if not re.match(r'^[a-z]+(\(.+\))?: [a-z]', main_message):
            warnings.append("Conventional commits should start with lowercase after type")
    else:
        # Check for capital letter at start
        if main_message and not main_message[0].isupper():
            warnings.append("Commit message should start with a capital letter")
    
    # Check for imperative mood (basic check)
    past_tense_patterns = [
        r'\b(added|deleted|changed|fixed|updated|removed|created|modified)\b',
        r'\b(implemented|refactored|improved|optimized)\b'
    ]
    for pattern in past_tense_patterns:
        if re.search(pattern, main_message, re.IGNORECASE):
            warnings.append("Use imperative mood (e.g., 'Add' not 'Added')")
            break
    
    # Check for issue references
    if '#' not in message and 'fix' in main_message.lower():
        warnings.append("Consider referencing an issue number (e.g., #123)")
    
    # Check body formatting (if present)
    if len(lines) > 1:
        # Check for blank line after first line
        if len(lines) > 1 and lines[1].strip() != "":
            errors.append("Add blank line after commit message summary")
        
        # Check body line length
        for i, line in enumerate(lines[2:], start=3):
            if len(line) > 72 and not line.startswith('http'):
                warnings.append(f"Line {i} exceeds 72 characters")
    
    return errors, warnings


def extract_commit_message_from_command(command):
    """Extract commit message from git commit command."""
    # Handle different commit message formats
    patterns = [
        r'-m\s+"([^"]+)"',  # -m "message"
        r"-m\s+'([^']+)'",  # -m 'message'
        r'-m\s+([^\s]+)',   # -m message (single word)
        r'--message="([^"]+)"',  # --message="message"
        r"--message='([^']+)'",  # --message='message'
        # Handle heredoc format
        r'-m\s+"\$\(cat\s+<<[\'"]?EOF[\'"]?\n(.*?)\nEOF\s*\)"',
        r"-m\s+'\$\(cat\s+<<['\"]?EOF['\"]?\n(.*?)\nEOF\s*\)'"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command, re.DOTALL)
        if match:
            return match.group(1)
    
    return None


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        command = input_data.get('tool_input', {}).get('command', '')
        
        # Only process git commit commands
        if tool_name != 'Bash' or 'git commit' not in command:
            sys.exit(0)
        
        # Skip if it's an amend or no-edit commit
        if '--amend' in command and '--no-edit' in command:
            sys.exit(0)
        
        # Extract commit message
        commit_message = extract_commit_message_from_command(command)
        
        if not commit_message:
            # Can't extract message, might be using an editor
            sys.exit(0)
        
        # Validate the commit message
        errors, warnings = validate_commit_message(commit_message)
        
        # If there are errors, block the commit
        if errors:
            print("Commit message validation failed!\n", file=sys.stderr)
            for error in errors:
                print(f"❌ {error}", file=sys.stderr)
            
            if warnings:
                print("\nWarnings:", file=sys.stderr)
                for warning in warnings:
                    print(f"⚠️  {warning}", file=sys.stderr)
            
            print("\nPlease fix the errors and try again.", file=sys.stderr)
            sys.exit(2)  # Exit code 2 blocks the tool call
        
        # Show warnings but don't block
        if warnings:
            print("Commit message warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"⚠️  {warning}", file=sys.stderr)
            print("\nProceeding with commit...", file=sys.stderr)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in commit validation hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()