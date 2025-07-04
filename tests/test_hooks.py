#!/usr/bin/env python3
"""
Test suite for Claude Hooks Manager.
Run with: python test_hooks.py
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def run_hook(hook_path, input_data):
    """Run a hook with given input and return the result."""
    try:
        # Convert input to JSON
        input_json = json.dumps(input_data)
        
        # Run the hook
        result = subprocess.run(
            ['python3', hook_path],
            input=input_json,
            capture_output=True,
            text=True
        )
        
        return {
            'exit_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except Exception as e:
        return {
            'exit_code': -1,
            'stdout': '',
            'stderr': str(e)
        }


def test_hook(hook_name, test_cases):
    """Test a specific hook with multiple test cases."""
    hook_path = Path(__file__).parent.parent / "hooks" / hook_name
    
    if not hook_path.exists():
        print(f"{Colors.RED}✗ {hook_name} not found{Colors.RESET}")
        return False
    
    print(f"\n{Colors.BLUE}Testing {hook_name}...{Colors.RESET}")
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        description = test_case.get('description', f'Test {i}')
        input_data = test_case.get('input', {})
        expected_exit = test_case.get('expected_exit', 0)
        expected_stderr_contains = test_case.get('stderr_contains', [])
        
        result = run_hook(hook_path, input_data)
        
        # Check exit code
        if result['exit_code'] == expected_exit:
            # Check stderr contains expected strings
            stderr_ok = True
            for expected_str in expected_stderr_contains:
                if expected_str not in result['stderr']:
                    stderr_ok = False
                    break
            
            if stderr_ok:
                print(f"  {Colors.GREEN}✓ {description}{Colors.RESET}")
                passed += 1
            else:
                print(f"  {Colors.RED}✗ {description} - stderr doesn't contain expected strings{Colors.RESET}")
                print(f"    Expected: {expected_stderr_contains}")
                print(f"    Got: {result['stderr'][:200]}...")
                failed += 1
        else:
            print(f"  {Colors.RED}✗ {description} - exit code {result['exit_code']} (expected {expected_exit}){Colors.RESET}")
            if result['stderr']:
                print(f"    Error: {result['stderr'][:200]}...")
            failed += 1
    
    print(f"  Summary: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all hook tests."""
    print(f"{Colors.BLUE}Claude Hooks Manager Test Suite{Colors.RESET}")
    print("=" * 40)
    
    # Define test cases for each hook
    test_suites = {
        'validate-git-commit.py': [
            {
                'description': 'Should allow good commit message',
                'input': {
                    'tool_name': 'Bash',
                    'tool_input': {'command': 'git commit -m "Fix navigation bug in mobile view"'}
                },
                'expected_exit': 0
            },
            {
                'description': 'Should block short commit message',
                'input': {
                    'tool_name': 'Bash',
                    'tool_input': {'command': 'git commit -m "fix"'}
                },
                'expected_exit': 2,
                'stderr_contains': ['too short']
            },
            {
                'description': 'Should ignore non-commit commands',
                'input': {
                    'tool_name': 'Bash',
                    'tool_input': {'command': 'ls -la'}
                },
                'expected_exit': 0
            }
        ],
        
        'no-mock-code.py': [
            {
                'description': 'Should detect Lorem ipsum',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'test.js',
                        'content': 'const text = "Lorem ipsum dolor sit amet";'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Remember to use real implementations']
            },
            {
                'description': 'Should detect test email',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'config.js',
                        'content': 'const admin = { email: "test@example.com" };'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Mock/Placeholder Code']
            },
            {
                'description': 'Should allow real code',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'user.js',
                        'content': 'const user = await db.users.findById(id);'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': []  # No warnings expected
            }
        ],
        
        'secret-scanner.py': [
            {
                'description': 'Should detect API key',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'config.js',
                        'content': 'const apiKey = "sk_test_1234567890abcdef1234567890abcdef";'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Security Warning']
            },
            {
                'description': 'Should detect password',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'db.js',
                        'content': 'const password = "MySecretPassword123!";'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Use environment variables']
            },
            {
                'description': 'Should allow environment variables',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'config.js',
                        'content': 'const apiKey = process.env.API_KEY;'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': []  # No warnings expected
            }
        ],
        
        'env-sync-validator.py': [
            {
                'description': 'Should warn about missing .env.example',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': '.env',
                        'content': 'API_KEY=secret123'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Remember to update .env.example']
            },
            {
                'description': 'Should ignore non-env files',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'config.js',
                        'content': 'const config = {};'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': []
            }
        ],
        
        'api-endpoint-verifier.py': [
            {
                'description': 'Should validate API endpoints',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'api/users.js',
                        'content': 'export async function GET(request) { return Response.json({users: []}); }'
                    }
                },
                'expected_exit': 0
            }
        ],
        
        'style-consistency.py': [
            {
                'description': 'Should detect missing dark mode',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'Button.tsx',
                        'content': '<button className="bg-blue-500 text-white">Click</button>'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Consider adding dark mode variant']
            },
            {
                'description': 'Should allow theme-aware classes',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'Button.tsx',
                        'content': '<button className="bg-blue-500 dark:bg-blue-600">Click</button>'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': []
            }
        ],
        
        'database-extension-check.py': [
            {
                'description': 'Should warn about new tables',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'migrations/create_user_settings.sql',
                        'content': 'CREATE TABLE user_settings (id INT PRIMARY KEY);'
                    }
                },
                'expected_exit': 2,
                'stderr_contains': ['Consider extending']
            }
        ],
        
        'duplicate-detector.py': [
            {
                'description': 'Should allow new unique files',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'components/UniqueComponent.tsx',
                        'content': 'export const UniqueComponent = () => <div>Unique</div>;'
                    }
                },
                'expected_exit': 0
            }
        ],
        
        'validate-dart-task.py': [
            {
                'description': 'Should require task title',
                'input': {
                    'tool_name': 'mcp__dart__create_task',
                    'tool_input': {
                        'title': '',
                        'dartboard': 'MyProject/Tasks'
                    }
                },
                'expected_exit': 2,
                'stderr_contains': ['Task title is required']
            },
            {
                'description': 'Should allow valid task',
                'input': {
                    'tool_name': 'mcp__dart__create_task',
                    'tool_input': {
                        'title': 'Implement new feature',
                        'dartboard': 'MyProject/Tasks'
                    }
                },
                'expected_exit': 0
            }
        ],
        
        'sync-docs-to-dart.py': [
            {
                'description': 'Should track markdown files',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'docs/api.md',
                        'content': '# API Documentation'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['can be synced to Dart']
            }
        ],
        
        'api-docs-enforcer.py': [
            {
                'description': 'Should warn about missing API docs',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'api/users/route.ts',
                        'content': 'export async function GET() { return Response.json({users: []}); }'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Consider adding']
            }
        ],
        
        'gitignore-enforcer.py': [
            {
                'description': 'Should check for gitignore',
                'input': {
                    'tool_name': 'Bash',
                    'tool_input': {
                        'command': 'git add .'
                    }
                },
                'expected_exit': 0
            }
        ],
        
        'log-commands.py': [
            {
                'description': 'Should log bash commands',
                'input': {
                    'tool_name': 'Bash',
                    'tool_input': {
                        'command': 'ls -la'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Command logged']
            }
        ],
        
        'mcp-tool-enforcer.py': [
            {
                'description': 'Should suggest MCP tools',
                'input': {
                    'tool_name': 'Task',
                    'tool_input': {
                        'description': 'Search for files',
                        'prompt': 'find . -name "*.js"'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Consider using']
            }
        ],
        
        'pre-commit-validator.py': [
            {
                'description': 'Should validate before commit',
                'input': {
                    'tool_name': 'Bash',
                    'tool_input': {
                        'command': 'git commit -m "test commit"'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['Pre-commit']
            }
        ],
        
        'readme-update-validator.py': [
            {
                'description': 'Should remind about README updates',
                'input': {
                    'tool_name': 'Write',
                    'tool_input': {
                        'file_path': 'src/newFeature.js',
                        'content': 'export const newFeature = () => {}'
                    }
                },
                'expected_exit': 0,
                'stderr_contains': ['README']
            }
        ],
        
        'session-end-summary.py': [
            {
                'description': 'Should not block when stop_hook_active is true',
                'input': {
                    'stop_hook_active': True,
                    'transcript_path': '/tmp/test-transcript'
                },
                'expected_exit': 0,
                'stderr_contains': []
            }
        ]
    }
    
    # Run tests
    all_passed = True
    for hook_name, test_cases in test_suites.items():
        if not test_hook(hook_name, test_cases):
            all_passed = False
    
    # Summary
    print("\n" + "=" * 40)
    if all_passed:
        print(f"{Colors.GREEN}✓ All tests passed!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}✗ Some tests failed!{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()