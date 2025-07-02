#!/usr/bin/env python3
"""
Dart task validation hook.
Ensures all tasks are created with proper Phase parent IDs.
"""
import json
import sys


# Known Phase IDs from the holace project
PHASE_IDS = {
    "Phase 0": "ncxtyKRzdRfe",
    "Phase 1": "PIgIBkeqFBhr",
    "Phase 2": "v6AHq6wPaV19",
    "Phase 2.1": "ZA9dxFvdqVzZ",
    "Phase 2.2": "B5bSyMTFj4hv",
    "Phase 3": "yfGhAykyJlOo",
    "Phase 4": "Mp8H62kNLclG",
    "Phase 5": "TuoSvdsNYmCh",
    "Phase 6": "ibzf2m2YPwci",
    "Phase 7": "aCNss1ngJbNH",
    "Phase 8": "Jrd2YRe33Z6e",
    "Phase 9": "testing-deployment"  # Placeholder, update when created
}


def main():
    try:
        # Read input
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Only process Dart create_task calls
        if tool_name != 'mcp__dart__create_task':
            sys.exit(0)
        
        # Check if dartboard is holace/Tasks
        dartboard = tool_input.get('dartboard', '')
        if dartboard != 'holace/Tasks':
            # Not a holace task, allow creation
            sys.exit(0)
        
        # Check if task has a parent ID
        parent_id = tool_input.get('parentId', '')
        if not parent_id:
            print("Task creation blocked!\n", file=sys.stderr)
            print("❌ All tasks in holace/Tasks must have a parent Phase", file=sys.stderr)
            print("\nAvailable Phases:", file=sys.stderr)
            for phase_name, phase_id in PHASE_IDS.items():
                if phase_id != "testing-deployment":
                    print(f"  • {phase_name}: {phase_id}", file=sys.stderr)
            print("\nPlease specify a parentId for the appropriate Phase.", file=sys.stderr)
            print("\nTip: Use mcp__dart__list_tasks with title='Phase' to find Phase IDs", file=sys.stderr)
            sys.exit(2)  # Block the task creation
        
        # Validate that the parent ID is a known Phase
        if parent_id not in PHASE_IDS.values():
            # It might be a valid subtask under another task, so just warn
            phase_names = [name for name, id in PHASE_IDS.items() if id == parent_id]
            if not phase_names:
                print(f"Warning: Parent ID {parent_id} is not a known Phase", file=sys.stderr)
                print("Make sure this is a valid parent task ID.", file=sys.stderr)
        
        # Additional validation for task properties
        title = tool_input.get('title', '')
        if not title:
            print("❌ Task title is required", file=sys.stderr)
            sys.exit(2)
        
        # Suggest appropriate priority based on Phase
        if parent_id in PHASE_IDS.values():
            phase_name = next((name for name, id in PHASE_IDS.items() if id == parent_id), None)
            if phase_name and 'priority' not in tool_input:
                print(f"Tip: Consider setting priority for {phase_name} task", file=sys.stderr)
        
        # Success - task creation can proceed
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error in Dart task validation hook: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()