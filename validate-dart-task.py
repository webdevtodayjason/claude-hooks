#!/usr/bin/env python3
"""
Dart task validation hook.
Ensures all tasks are created with proper parent IDs and hierarchy.
This is a generic example that can be customized for your project.
"""
import json
import sys


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Only process Dart create_task calls
        if tool_name != 'mcp__dart__create_task':
            sys.exit(0)
        
        # Example validation: Ensure tasks have required fields
        title = tool_input.get('title', '')
        if not title:
            print("❌ Task title is required", file=sys.stderr)
            sys.exit(2)
        
        # Example: Check if task has a parent ID (customize based on your workflow)
        parent_id = tool_input.get('parentId', '')
        dartboard = tool_input.get('dartboard', '')
        
        # You can customize this logic based on your project's requirements
        # For example, you might require parent IDs for certain dartboards:
        # if dartboard == 'YourProject/Tasks' and not parent_id:
        #     print("❌ Tasks in this dartboard require a parent ID", file=sys.stderr)
        #     sys.exit(2)
        
        # Example: Suggest priority if not set
        if 'priority' not in tool_input:
            print("💡 Tip: Consider setting a priority for this task", file=sys.stderr)
        
        # Example: Validate dartboard format (should contain workspace/board)
        if dartboard and '/' not in dartboard:
            print("⚠️  Dartboard should be in format: workspace/board", file=sys.stderr)
        
        # Success - task creation can proceed
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in Dart task validation hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()