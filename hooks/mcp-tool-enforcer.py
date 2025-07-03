#!/usr/bin/env python3
"""
MCP tool enforcement hook.
Suggests using MCP tools when appropriate alternatives are available.
"""
import json
import sys
import re


# Map of non-MCP tools to their MCP equivalents
MCP_ALTERNATIVES = {
    'WebFetch': {
        'patterns': ['fetch', 'curl', 'wget', 'axios', 'requests'],
        'mcp_tools': ['mcp__fetch__fetch', 'mcp__browser__navigate'],
        'message': "Consider using MCP fetch tools instead of direct web requests"
    },
    'WebSearch': {
        'patterns': ['google', 'search', 'bing', 'duckduckgo'],
        'mcp_tools': ['mcp__search__search'],
        'message': "Consider using MCP search tools for web searches"
    },
    'Database': {
        'patterns': ['mysql', 'postgres', 'sqlite', 'mongodb'],
        'mcp_tools': ['mcp__database__query', 'mcp__sqlite__query'],
        'message': "Consider using MCP database tools for database operations"
    },
    'FileSystem': {
        'patterns': ['fs.', 'readFile', 'writeFile', 'mkdir', 'rmdir'],
        'mcp_tools': ['mcp__filesystem__read', 'mcp__filesystem__write'],
        'message': "Consider using MCP filesystem tools for file operations"
    },
    'Git': {
        'patterns': ['git clone', 'git pull', 'git push', 'git checkout'],
        'mcp_tools': ['mcp__git__clone', 'mcp__git__pull', 'mcp__git__push'],
        'message': "Consider using MCP git tools for repository operations"
    },
    'Memory': {
        'patterns': ['localStorage', 'sessionStorage', 'cache', 'store'],
        'mcp_tools': ['mcp__memory__store', 'mcp__memory__retrieve'],
        'message': "Consider using MCP memory tools for data persistence"
    }
}


def check_bash_command(command):
    """Check if a bash command could use MCP tools instead."""
    suggestions = []
    
    command_lower = command.lower()
    
    # Check for patterns that suggest MCP alternatives
    for category, info in MCP_ALTERNATIVES.items():
        for pattern in info['patterns']:
            if pattern in command_lower:
                suggestions.append({
                    'category': category,
                    'message': info['message'],
                    'alternatives': info['mcp_tools']
                })
                break
    
    return suggestions


def check_code_content(content, file_type):
    """Check code content for operations that could use MCP tools."""
    suggestions = []
    
    # Skip if it's a configuration file
    if file_type in ['json', 'yaml', 'yml', 'toml', 'ini']:
        return suggestions
    
    content_lower = content.lower()
    
    # Check for patterns in code
    for category, info in MCP_ALTERNATIVES.items():
        for pattern in info['patterns']:
            if pattern in content_lower:
                # Verify it's actual code, not a comment
                lines = content.split('\n')
                for line in lines:
                    if pattern in line.lower() and not line.strip().startswith(('/', '#', '*')):
                        suggestions.append({
                            'category': category,
                            'message': info['message'],
                            'alternatives': info['mcp_tools']
                        })
                        break
                break
    
    return suggestions


def format_suggestions(suggestions):
    """Format suggestions for output."""
    if not suggestions:
        return None
    
    # Deduplicate suggestions
    unique_suggestions = []
    seen = set()
    
    for suggestion in suggestions:
        key = suggestion['category']
        if key not in seen:
            seen.add(key)
            unique_suggestions.append(suggestion)
    
    output = {
        "decision": "approve",
        "reason": "MCP tool alternatives available",
        "suggestions": []
    }
    
    for suggestion in unique_suggestions:
        output["suggestions"].append({
            "message": suggestion['message'],
            "alternatives": suggestion['alternatives']
        })
    
    return output


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        suggestions = []
        
        # Check Bash commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            suggestions = check_bash_command(command)
        
        # Check file operations
        elif tool_name in ['Write', 'Edit', 'MultiEdit']:
            file_path = tool_input.get('file_path', '')
            file_type = file_path.split('.')[-1] if '.' in file_path else ''
            
            # Get content based on tool type
            if tool_name == 'Write':
                content = tool_input.get('content', '')
            elif tool_name == 'Edit':
                content = tool_input.get('new_string', '')
            else:  # MultiEdit
                content = ""
                for edit in tool_input.get('edits', []):
                    content += edit.get('new_string', '') + "\n"
            
            suggestions = check_code_content(content, file_type)
        
        # Format and output suggestions
        if suggestions:
            output = format_suggestions(suggestions)
            if output:
                # Output as structured JSON for Claude to process
                print(json.dumps(output))
                
                # Also log suggestions to stderr for visibility
                print("\nMCP Tool Suggestions:", file=sys.stderr)
                for suggestion in output["suggestions"]:
                    print(f"💡 {suggestion['message']}", file=sys.stderr)
                    print(f"   Available tools: {', '.join(suggestion['alternatives'])}", file=sys.stderr)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Don't fail operations due to this hook
        sys.exit(0)


if __name__ == "__main__":
    main()