#!/usr/bin/env python3
"""
Comprehensive test suite for all Claude Hooks Manager hooks.
"""
import json
import subprocess
import sys
from pathlib import Path


def test_hook(hook_name, input_json, expected_exit=0):
    """Test a single hook with timeout."""
    hook_path = Path(__file__).parent.parent / "hooks" / hook_name
    
    try:
        result = subprocess.run(
            ['python3', str(hook_path)],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=5  # 5 second timeout
        )
        return result.returncode == expected_exit
    except subprocess.TimeoutExpired:
        print(f"  ❌ {hook_name} timed out")
        return False
    except Exception as e:
        print(f"  ❌ {hook_name} error: {e}")
        return False


def main():
    """Test all hooks."""
    print("Testing all Claude Hooks Manager hooks...")
    print("=" * 50)
    
    # Define test cases for each hook
    tests = {
        'api-docs-enforcer.py': '{"tool_name":"Write","tool_input":{"file_path":"api/test.ts","content":"export async function GET() {}"}}',
        'api-endpoint-verifier.py': '{"tool_name":"Write","tool_input":{"file_path":"api/users.js","content":"export async function GET() {}"}}',
        'database-extension-check.py': '{"tool_name":"Write","tool_input":{"file_path":"schema.sql","content":"SELECT * FROM users"}}',
        'duplicate-detector.py': '{"tool_name":"Write","tool_input":{"file_path":"new-component.tsx","content":"export const Component = () => {}"}}',
        'env-sync-validator.py': '{"tool_name":"Write","tool_input":{"file_path":"config.js","content":"const x = 1"}}',
        'gitignore-enforcer.py': '{"tool_name":"Bash","tool_input":{"command":"ls"}}',
        'log-commands.py': '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}',
        'mcp-tool-enforcer.py': '{"tool_name":"Bash","tool_input":{"command":"ls"}}',
        'no-mock-code.py': '{"tool_name":"Write","tool_input":{"file_path":"test.js","content":"const x = 1"}}',
        'pre-commit-validator.py': '{"tool_name":"Bash","tool_input":{"command":"ls"}}',
        'readme-update-validator.py': '{"tool_name":"Write","tool_input":{"file_path":"test.js","content":"const x = 1"}}',
        'secret-scanner.py': '{"tool_name":"Write","tool_input":{"file_path":"test.js","content":"const x = 1"}}',
        'session-end-summary.py': '{"stop_hook_active":true,"transcript_path":"/tmp/test"}',
        'style-consistency.py': '{"tool_name":"Write","tool_input":{"file_path":"Button.tsx","content":"<button>Click</button>"}}',
        'sync-docs-to-dart.py': '{"tool_name":"Write","tool_input":{"file_path":"test.js","content":"const x = 1"}}',
        'timestamp-validator.py': '{"tool":"Write","tool_input":{"file_path":"CHANGELOG.md","content":"## [1.0.0] - 2025-07-04\\n\\nTest release"}}',
        'validate-dart-task.py': '{"tool_name":"mcp__dart__create_task","tool_input":{"title":"Test Task"}}',
        'validate-git-commit.py': '{"tool_name":"Bash","tool_input":{"command":"git commit -m \\"Test commit message\\""}}',
    }
    
    passed = 0
    failed = 0
    
    for hook_name, test_input in tests.items():
        print(f"\nTesting {hook_name}...")
        if test_hook(hook_name, test_input):
            print(f"  ✅ {hook_name} passed")
            passed += 1
        else:
            print(f"  ❌ {hook_name} failed")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())