#!/usr/bin/env python3
"""
Timestamp validator hook.
Ensures accurate timestamps are used in documentation, logs, and commits.
Prevents hardcoded or incorrect dates by validating against system time.
"""
import json
import sys
import re
from datetime import datetime, timedelta
import subprocess
from pathlib import Path


def get_system_date():
    """Get the current system date and time."""
    return datetime.now()


def is_date_reasonable(date_str, date_format="%Y-%m-%d"):
    """Check if a date string is within reasonable bounds."""
    try:
        date_obj = datetime.strptime(date_str, date_format)
        current_date = get_system_date()
        
        # Allow dates within the past year and up to 1 month in the future
        min_date = current_date - timedelta(days=365)
        max_date = current_date + timedelta(days=30)
        
        return min_date <= date_obj <= max_date
    except ValueError:
        return False


def find_dates_in_content(content):
    """Find all date patterns in content."""
    # Common date patterns
    patterns = [
        (r'\d{4}-\d{2}-\d{2}', '%Y-%m-%d'),  # 2025-07-04
        (r'\d{4}-\d{1,2}-\d{1,2}', '%Y-%m-%d'),  # 2025-7-4
        (r'\d{2}/\d{2}/\d{4}', '%m/%d/%Y'),  # 07/04/2025
        (r'\d{1,2}/\d{1,2}/\d{4}', '%m/%d/%Y'),  # 7/4/2025
        (r'\w+ \d{1,2}, \d{4}', '%B %d, %Y'),  # July 4, 2025
        (r'\d{1,2} \w+ \d{4}', '%d %B %Y'),  # 4 July 2025
    ]
    
    found_dates = []
    for pattern, date_format in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            found_dates.append((match, date_format))
    
    return found_dates


def validate_changelog_entry(content, file_path):
    """Validate changelog entries have correct dates."""
    if 'CHANGELOG' in file_path.upper():
        # Look for version headers with dates
        version_pattern = r'## \[[\d.]+\] - (\d{4}-\d{2}-\d{2})'
        matches = re.findall(version_pattern, content)
        
        current_date = get_system_date()
        warnings = []
        
        for date_str in matches:
            if not is_date_reasonable(date_str):
                warnings.append(f"Changelog date '{date_str}' seems incorrect")
            
            # Check if it's a future date (except for pre-releases)
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                if date_obj.date() > current_date.date():
                    warnings.append(f"Future date '{date_str}' in changelog - use today's date ({current_date.strftime('%Y-%m-%d')})")
            except ValueError:
                pass
        
        return warnings
    return []


def validate_commit_message(message):
    """Check commit messages for date references."""
    warnings = []
    
    # Check for common date mistakes in commits
    found_dates = find_dates_in_content(message)
    
    for date_str, date_format in found_dates:
        if not is_date_reasonable(date_str, date_format):
            current_date = get_system_date()
            warnings.append(
                f"Date '{date_str}' in commit message seems incorrect. "
                f"Today is {current_date.strftime('%A, %B %d, %Y')}"
            )
    
    return warnings


def suggest_current_timestamp():
    """Provide current timestamp in various formats."""
    current_date = get_system_date()
    
    return {
        "iso_date": current_date.strftime('%Y-%m-%d'),
        "iso_datetime": current_date.strftime('%Y-%m-%d %H:%M:%S'),
        "readable_date": current_date.strftime('%A, %B %d, %Y'),
        "changelog_format": current_date.strftime('%Y-%m-%d'),
        "log_format": current_date.strftime('%Y-%m-%d %H:%M:%S'),
        "unix_timestamp": int(current_date.timestamp())
    }


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool = input_data.get('tool', '')
        tool_input = input_data.get('tool_input', {})
        
        warnings = []
        
        # Check different tools
        if tool in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path', '')
            
            # For Write and Edit, check content
            if tool == 'Write':
                content = tool_input.get('content', '')
            elif tool == 'Edit':
                content = tool_input.get('new_string', '')
            elif tool == 'MultiEdit':
                # Check all edits
                content = '\n'.join(
                    edit.get('new_string', '') 
                    for edit in tool_input.get('edits', [])
                )
            else:
                content = ''
            
            # Validate changelog entries
            changelog_warnings = validate_changelog_entry(content, file_path)
            warnings.extend(changelog_warnings)
            
            # Check for hardcoded dates that might be wrong
            if any(keyword in file_path.lower() for keyword in ['log', 'readme', 'doc', 'changelog']):
                found_dates = find_dates_in_content(content)
                for date_str, date_format in found_dates:
                    # Special handling for documentation dates
                    if '2025-01-' in date_str and get_system_date().month >= 7:
                        warnings.append(
                            f"Found January date '{date_str}' but current month is "
                            f"{get_system_date().strftime('%B')}. This might be incorrect."
                        )
        
        elif tool == 'Bash':
            command = tool_input.get('command', '')
            
            # Check git commit commands
            if 'git commit' in command:
                # Extract commit message
                message_match = re.search(r'-m\s*["\']([^"\']+)["\']', command)
                if message_match:
                    message = message_match.group(1)
                    commit_warnings = validate_commit_message(message)
                    warnings.extend(commit_warnings)
            
            # Check for commands that might create dated files
            if any(cmd in command for cmd in ['touch', 'echo', 'printf']) and re.search(r'\d{4}-\d{2}-\d{2}', command):
                found_dates = find_dates_in_content(command)
                for date_str, date_format in found_dates:
                    if not is_date_reasonable(date_str, date_format):
                        warnings.append(f"Command contains questionable date '{date_str}'")
        
        # If warnings found, provide helpful timestamp info
        if warnings:
            timestamps = suggest_current_timestamp()
            warning_message = "\n".join(warnings)
            
            print(f"\n⏰ Timestamp Validation Warning:\n{warning_message}\n", file=sys.stderr)
            print(f"📅 Current timestamps for reference:", file=sys.stderr)
            print(f"   ISO Date: {timestamps['iso_date']}", file=sys.stderr)
            print(f"   Readable: {timestamps['readable_date']}", file=sys.stderr)
            print(f"   For logs: {timestamps['log_format']}", file=sys.stderr)
            print(f"   For CHANGELOG: {timestamps['changelog_format']}\n", file=sys.stderr)
            
            # Don't block, just warn
            sys.exit(0)
        
        # All good
        sys.exit(0)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Don't fail the hook on errors
        print(f"Timestamp validator error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()