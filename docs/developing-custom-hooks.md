# Developing Custom Hooks for Claude

This guide will walk you through creating your own custom hooks for Claude. Hooks allow you to intercept and modify Claude's behavior, enforce coding standards, and automate workflows.

## Table of Contents
- [Understanding Claude Hooks](#understanding-claude-hooks)
- [Hook Architecture](#hook-architecture)
- [Creating Your First Hook](#creating-your-first-hook)
- [Hook Input and Output](#hook-input-and-output)
- [Exit Codes](#exit-codes)
- [Available Hook Types](#available-hook-types)
- [Best Practices](#best-practices)
- [Testing Your Hook](#testing-your-hook)
- [Installing Your Hook](#installing-your-hook)
- [Examples](#examples)

## Understanding Claude Hooks

Claude hooks are Python scripts that run at specific points during Claude's execution. They receive JSON input via stdin and can influence Claude's behavior through their output and exit codes.

## Hook Architecture

```
Claude → Hook Triggered → Python Script → Decision/Action
     ↓              ↓                ↓              ↓
 User Input    JSON via stdin   Process Data   Exit Code
```

## Creating Your First Hook

Use the CLI to create a new hook:

```bash
claude-hooks create my-custom-hook
```

This creates a template in `~/.claude/hooks/my-custom-hook.py`:

```python
#!/usr/bin/env python3
"""
my-custom-hook - A custom hook for Claude
Description: Add your description here
Author: Your Name
"""
import json
import sys

def main():
    try:
        # Read input from Claude
        input_data = json.load(sys.stdin)
        
        # Extract relevant data based on hook type
        tool = input_data.get('tool', '')
        tool_input = input_data.get('tool_input', {})
        
        # Your custom logic here
        # Example: Check something and decide whether to proceed
        
        # Success - allow the action
        sys.exit(0)
        
    except Exception as e:
        # Log error to stderr
        print(f"Error in hook: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Hook Input and Output

### Input Structure

Hooks receive JSON input with different fields depending on the hook type:

#### Tool Hooks
```json
{
  "tool": "Bash",
  "tool_input": {
    "command": "rm -rf /",
    "description": "Clean up files"
  }
}
```

#### Commit Hooks
```json
{
  "message": "feat: Add new feature",
  "files": ["src/index.js", "README.md"],
  "diff": "... git diff output ..."
}
```

#### General Hooks
```json
{
  "action": "session_end",
  "transcript_path": "/path/to/transcript",
  "duration": 3600
}
```

### Output Options

Hooks can produce output in several ways:

1. **Simple Allow/Block** (exit code only)
2. **Block with Reason** (JSON output)
3. **Warning Message** (print to stderr, exit 0)
4. **Data Storage** (write to files for persistence)

## Exit Codes

- **0**: Success - allow the action to proceed
- **1**: Error - something went wrong in the hook
- **2**: Block - prevent the action with a reason

## Available Hook Types

### 1. Tool Hooks
Intercept Claude's tool usage (Bash, Edit, Write, etc.)

```python
def validate_bash_command(command):
    dangerous_commands = ['rm -rf /', 'dd if=', 'mkfs']
    for dangerous in dangerous_commands:
        if dangerous in command:
            return False, f"Dangerous command detected: {dangerous}"
    return True, ""
```

### 2. Commit Hooks
Validate git commits before they're made

```python
def validate_commit_message(message):
    pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'
    if not re.match(pattern, message):
        return False, "Commit message must follow conventional format"
    return True, ""
```

### 3. Session Hooks
Run at the start or end of Claude sessions

```python
def session_end_summary(transcript_path, duration):
    # Generate summary of session activities
    summary = analyze_transcript(transcript_path)
    return {
        "files_modified": summary['files'],
        "commands_run": summary['commands'],
        "duration": duration
    }
```

### 4. File Hooks
Monitor file operations

```python
def check_file_patterns(file_path, content):
    if file_path.endswith('.env'):
        if 'SECRET_KEY=' in content and 'your-secret-here' in content:
            return False, "Please set a real secret key"
    return True, ""
```

## Best Practices

### 1. Performance
- Keep hooks fast (< 100ms execution time)
- Avoid expensive operations (network calls, large file reads)
- Cache results when possible

### 2. Error Handling
```python
def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
```

### 3. Configuration
Store configuration in project-specific files:

```python
def load_config():
    config_path = Path.cwd() / '.claude' / 'my-hook-config.json'
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return get_default_config()
```

### 4. Logging
Use stderr for debug output:

```python
def debug_log(message):
    if os.environ.get('CLAUDE_HOOK_DEBUG'):
        print(f"[DEBUG] {message}", file=sys.stderr)
```

## Testing Your Hook

### Manual Testing

1. Create a test script:
```bash
#!/bin/bash
# test-my-hook.sh

echo '{"tool": "Bash", "tool_input": {"command": "echo test"}}' | \
    python ~/.claude/hooks/my-custom-hook.py

echo "Exit code: $?"
```

2. Test different scenarios:
```python
# test_my_hook.py
import subprocess
import json

test_cases = [
    {"tool": "Bash", "tool_input": {"command": "ls"}},
    {"tool": "Bash", "tool_input": {"command": "rm -rf /"}},
]

for test in test_cases:
    result = subprocess.run(
        ['python', 'my-custom-hook.py'],
        input=json.dumps(test),
        capture_output=True,
        text=True
    )
    print(f"Test: {test}")
    print(f"Exit code: {result.returncode}")
    print(f"Stdout: {result.stdout}")
    print(f"Stderr: {result.stderr}")
    print("-" * 40)
```

### Integration Testing

Test with Claude directly:
```bash
# Enable your hook
claude-hooks enable my-custom-hook

# Test with Claude
claude "Run ls command"  # Should work
claude "Delete all files with rm -rf /"  # Should be blocked
```

## Installing Your Hook

### Method 1: Using the CLI
```bash
# If your hook is in the standard location
claude-hooks enable my-custom-hook

# If your hook is elsewhere
cp /path/to/my-hook.py ~/.claude/hooks/
claude-hooks enable my-hook
```

### Method 2: Manual Installation
```bash
# Copy to hooks directory
cp my-custom-hook.py ~/.claude/hooks/

# Make executable
chmod +x ~/.claude/hooks/my-custom-hook.py

# Add to settings.json
claude-hooks config
```

## Examples

### Example 1: Preventing Accidental Deletions
```python
#!/usr/bin/env python3
"""Prevent accidental deletion of important files"""
import json
import sys
import re

PROTECTED_PATTERNS = [
    r'\.git/?$',
    r'node_modules/?$',
    r'\.env$',
    r'database\.sqlite',
]

def main():
    try:
        input_data = json.load(sys.stdin)
        tool = input_data.get('tool', '')
        
        if tool == 'Bash':
            command = input_data.get('tool_input', {}).get('command', '')
            
            # Check for rm commands
            if re.search(r'\brm\b.*-[rf]', command):
                for pattern in PROTECTED_PATTERNS:
                    if re.search(pattern, command):
                        response = {
                            "decision": "block",
                            "reason": f"Cannot delete protected path matching: {pattern}"
                        }
                        print(json.dumps(response))
                        sys.exit(2)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Example 2: Enforcing Code Review Comments
```python
#!/usr/bin/env python3
"""Ensure code changes include proper comments"""
import json
import sys
import re

def check_code_comments(file_path, content):
    """Check if code has sufficient comments"""
    if not any(file_path.endswith(ext) for ext in ['.py', '.js', '.ts']):
        return True, ""
    
    lines = content.split('\n')
    code_lines = 0
    comment_lines = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped:
            if stripped.startswith(('#', '//', '/*', '*')):
                comment_lines += 1
            else:
                code_lines += 1
    
    if code_lines > 0:
        comment_ratio = comment_lines / code_lines
        if comment_ratio < 0.1:  # Less than 10% comments
            return False, f"Code needs more comments (currently {comment_ratio:.1%})"
    
    return True, ""

def main():
    try:
        input_data = json.load(sys.stdin)
        tool = input_data.get('tool', '')
        
        if tool in ['Write', 'Edit']:
            file_path = input_data.get('tool_input', {}).get('file_path', '')
            content = input_data.get('tool_input', {}).get('content', '')
            
            valid, reason = check_code_comments(file_path, content)
            if not valid:
                print(f"Warning: {reason}", file=sys.stderr)
                # Just warn, don't block
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Example 3: Project-Specific Linting
```python
#!/usr/bin/env python3
"""Run project-specific linting on file changes"""
import json
import sys
import subprocess
from pathlib import Path

def get_project_root():
    """Find the project root (git repository root)"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except:
        pass
    return Path.cwd()

def lint_file(file_path):
    """Run appropriate linter based on file type"""
    project_root = get_project_root()
    
    if file_path.endswith('.py'):
        # Check if project uses specific linter
        if (project_root / '.flake8').exists():
            result = subprocess.run(
                ['flake8', file_path],
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout
        elif (project_root / 'pyproject.toml').exists():
            result = subprocess.run(
                ['ruff', 'check', file_path],
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout
    
    return True, ""

def main():
    try:
        input_data = json.load(sys.stdin)
        tool = input_data.get('tool', '')
        
        if tool in ['Write', 'Edit']:
            file_path = input_data.get('tool_input', {}).get('file_path', '')
            
            success, output = lint_file(file_path)
            if not success:
                print(f"Linting issues found:\n{output}", file=sys.stderr)
                # You could choose to block here with exit(2)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Advanced Topics

### State Persistence
Store state between hook invocations:

```python
import json
from pathlib import Path

def get_state_file():
    return Path.home() / '.claude' / 'hook-state' / 'my-hook.json'

def load_state():
    state_file = get_state_file()
    if state_file.exists():
        with open(state_file) as f:
            return json.load(f)
    return {}

def save_state(state):
    state_file = get_state_file()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(state, f)
```

### Hook Communication
Hooks can communicate via shared files:

```python
def notify_other_hooks(message):
    msg_file = Path.home() / '.claude' / 'hook-messages' / 'latest.json'
    msg_file.parent.mkdir(parents=True, exist_ok=True)
    with open(msg_file, 'w') as f:
        json.dump({
            'from': 'my-custom-hook',
            'message': message,
            'timestamp': time.time()
        }, f)
```

## Troubleshooting

### Common Issues

1. **Hook not running**: Check that it's executable and enabled
   ```bash
   chmod +x ~/.claude/hooks/my-hook.py
   claude-hooks enable my-hook
   ```

2. **JSON parsing errors**: Validate your input handling
   ```python
   try:
       input_data = json.load(sys.stdin)
   except json.JSONDecodeError as e:
       print(f"Invalid JSON: {e}", file=sys.stderr)
       sys.exit(1)
   ```

3. **Performance issues**: Profile your hook
   ```python
   import time
   start = time.time()
   # ... your code ...
   duration = time.time() - start
   if duration > 0.1:
       print(f"Warning: Hook took {duration:.2f}s", file=sys.stderr)
   ```

## Contributing

If you've created a useful hook, consider contributing it to the claude-code-hooks repository:

1. Fork the repository
2. Add your hook to the `hooks/` directory
3. Add tests in `tests/`
4. Update the hooks registry in `index.js`
5. Submit a pull request

## Resources

- [Claude Hooks Manager Repository](https://github.com/webdevtodayjason/claude-hooks)
- [Hook Examples](https://github.com/webdevtodayjason/claude-hooks/tree/main/hooks)
- [Claude Documentation](https://docs.anthropic.com/claude-code)

---

Happy hook development! 🎣