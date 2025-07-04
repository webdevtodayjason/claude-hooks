# Creating Custom Hooks

Learn how to create your own custom hooks for Claude Hooks Manager.

## Overview

Custom hooks allow you to extend Claude Hooks Manager with project-specific automation. You can create hooks in various languages and integrate them seamlessly with the existing hook system.

## Hook Structure

### Basic Hook Anatomy

Every custom hook consists of:

1. **Hook Definition** - Metadata about the hook
2. **Hook Script** - The executable code
3. **Configuration Schema** - Defines configurable options

### Directory Structure

```
.claude-hooks/
├── custom/
│   ├── my-custom-hook/
│   │   ├── index.js
│   │   ├── hook.json
│   │   └── README.md
│   └── another-hook/
│       ├── run.sh
│       └── hook.json
└── config.json
```

## Creating Your First Custom Hook

### Step 1: Create Hook Directory

```bash
mkdir -p .claude-hooks/custom/my-custom-hook
cd .claude-hooks/custom/my-custom-hook
```

### Step 2: Define Hook Metadata

Create `hook.json`:

```json
{
  "name": "my-custom-hook",
  "version": "1.0.0",
  "description": "A custom hook that validates TODO comments",
  "type": "pre-commit",
  "executable": "index.js",
  "configSchema": {
    "maxTodos": {
      "type": "number",
      "default": 10,
      "description": "Maximum allowed TODO comments"
    },
    "requireAssignee": {
      "type": "boolean",
      "default": false,
      "description": "Require assignee in TODO comments"
    }
  }
}
```

### Step 3: Write Hook Script

Create `index.js`:

```javascript
#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Get configuration
const config = JSON.parse(process.env.CLAUDE_HOOK_CONFIG || '{}');
const stagedFiles = process.env.CLAUDE_STAGED_FILES?.split('\n') || [];

// Hook logic
let todoCount = 0;
let errors = [];

for (const file of stagedFiles) {
  if (!file || !file.endsWith('.js')) continue;
  
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.split('\n');
  
  lines.forEach((line, index) => {
    if (line.includes('TODO')) {
      todoCount++;
      
      if (config.requireAssignee && !line.match(/TODO\s*\(.+\)/)) {
        errors.push(`${file}:${index + 1} - TODO missing assignee`);
      }
    }
  });
}

// Check limits
if (todoCount > config.maxTodos) {
  console.error(`Error: Too many TODOs (${todoCount}/${config.maxTodos})`);
  process.exit(1);
}

if (errors.length > 0) {
  console.error('TODO validation errors:');
  errors.forEach(err => console.error(`  ${err}`));
  process.exit(1);
}

console.log(`✓ TODO check passed (${todoCount} TODOs found)`);
process.exit(0);
```

### Step 4: Make Script Executable

```bash
chmod +x index.js
```

### Step 5: Register the Hook

```bash
claude-hooks register my-custom-hook
claude-hooks install my-custom-hook
```

## Hook Types and Environment Variables

### Available Hook Types

- `pre-commit` - Before commit is created
- `commit-msg` - Validate/modify commit message
- `pre-push` - Before pushing to remote
- `post-commit` - After commit is created
- `pre-rebase` - Before rebase operation

### Environment Variables

All hooks receive these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `CLAUDE_HOOK_TYPE` | The hook type being run | `pre-commit` |
| `CLAUDE_HOOK_CONFIG` | JSON string of hook configuration | `{"maxTodos": 10}` |
| `CLAUDE_STAGED_FILES` | Newline-separated list of staged files | `src/index.js\nsrc/utils.js` |
| `CLAUDE_COMMIT_MSG_FILE` | Path to commit message file (commit-msg only) | `.git/COMMIT_EDITMSG` |
| `CLAUDE_PROJECT_ROOT` | Absolute path to project root | `/home/user/project` |

## Advanced Hook Examples

### Shell Script Hook

Create a hook that checks for sensitive data:

`check-secrets/hook.json`:
```json
{
  "name": "check-secrets",
  "version": "1.0.0",
  "description": "Checks for accidentally committed secrets",
  "type": "pre-commit",
  "executable": "check.sh"
}
```

`check-secrets/check.sh`:
```bash
#!/bin/bash

# Patterns to check
patterns=(
  "password\s*=\s*[\"'][^\"']+[\"']"
  "api[_-]?key\s*=\s*[\"'][^\"']+[\"']"
  "secret\s*=\s*[\"'][^\"']+[\"']"
  "private[_-]?key"
)

# Check staged files
exit_code=0
while IFS= read -r file; do
  if [[ -z "$file" ]]; then
    continue
  fi
  
  for pattern in "${patterns[@]}"; do
    if grep -qiE "$pattern" "$file"; then
      echo "⚠️  Potential secret found in $file"
      echo "   Pattern: $pattern"
      exit_code=1
    fi
  done
done <<< "$CLAUDE_STAGED_FILES"

exit $exit_code
```

### Python Hook

Create a hook that validates Python imports:

`validate-imports/hook.json`:
```json
{
  "name": "validate-imports",
  "version": "1.0.0",
  "description": "Validates Python import statements",
  "type": "pre-commit",
  "executable": "validate.py",
  "configSchema": {
    "allowedImports": {
      "type": "array",
      "default": [],
      "description": "List of allowed import patterns"
    }
  }
}
```

`validate-imports/validate.py`:
```python
#!/usr/bin/env python3

import os
import re
import json
import sys

# Get configuration
config = json.loads(os.environ.get('CLAUDE_HOOK_CONFIG', '{}'))
staged_files = os.environ.get('CLAUDE_STAGED_FILES', '').split('\n')

# Check Python files
errors = []
for file_path in staged_files:
    if not file_path.endswith('.py'):
        continue
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip().startswith('import ') or 'from ' in line:
                # Check against allowed patterns
                allowed = False
                for pattern in config.get('allowedImports', []):
                    if re.match(pattern, line.strip()):
                        allowed = True
                        break
                
                if not allowed and config.get('allowedImports'):
                    errors.append(f"{file_path}:{line_num} - Unauthorized import: {line.strip()}")

if errors:
    print("Import validation errors:")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)

print("✓ Import validation passed")
sys.exit(0)
```

## Hook Communication

### Inter-hook Communication

Hooks can communicate through shared state files:

```javascript
// Write state
const state = { filesProcessed: 10, errors: [] };
fs.writeFileSync('.claude-hooks/.state/my-hook.json', JSON.stringify(state));

// Read state from another hook
const previousState = JSON.parse(
  fs.readFileSync('.claude-hooks/.state/previous-hook.json', 'utf8')
);
```

### Hook Chaining

Define dependencies in `hook.json`:

```json
{
  "name": "my-dependent-hook",
  "dependsOn": ["format-check", "lint-check"],
  "runAfter": ["test-check"]
}
```

## Testing Custom Hooks

### Unit Testing

Create `test.js` for your hook:

```javascript
const { exec } = require('child_process');
const path = require('path');

describe('my-custom-hook', () => {
  it('should pass with valid files', (done) => {
    process.env.CLAUDE_STAGED_FILES = 'test/valid.js';
    process.env.CLAUDE_HOOK_CONFIG = JSON.stringify({ maxTodos: 10 });
    
    exec('node index.js', (error, stdout, stderr) => {
      expect(error).toBeNull();
      expect(stdout).toContain('✓ TODO check passed');
      done();
    });
  });
});
```

### Integration Testing

Test with Claude Hooks Manager:

```bash
# Test run without committing
claude-hooks run my-custom-hook --test

# Test with specific files
claude-hooks run my-custom-hook --files "src/index.js,src/utils.js"

# Test with custom config
claude-hooks run my-custom-hook --config '{"maxTodos": 5}'
```

## Best Practices

### 1. Performance

- Process files in parallel when possible
- Cache results for expensive operations
- Exit early on first error (unless collecting all errors)

### 2. Error Handling

```javascript
try {
  // Hook logic
} catch (error) {
  console.error(`Hook error: ${error.message}`);
  // Always exit with non-zero on error
  process.exit(1);
}
```

### 3. User-Friendly Output

```javascript
// Use colors and symbols
console.log('\x1b[32m✓\x1b[0m All checks passed');
console.error('\x1b[31m✗\x1b[0m Validation failed');

// Provide actionable feedback
console.error('To fix: run "npm run format"');
```

### 4. Configuration Validation

```javascript
// Validate configuration
const schema = require('./config-schema.json');
const valid = validateConfig(config, schema);

if (!valid) {
  console.error('Invalid configuration:', validation.errors);
  process.exit(1);
}
```

## Publishing Custom Hooks

### Package Structure

```
my-awesome-hook/
├── package.json
├── index.js
├── hook.json
├── README.md
├── LICENSE
└── test/
    └── test.js
```

### Publishing to npm

1. Create `package.json`:
```json
{
  "name": "claude-hook-awesome",
  "version": "1.0.0",
  "description": "An awesome hook for Claude Hooks Manager",
  "main": "index.js",
  "keywords": ["claude-hooks", "git-hooks"],
  "files": ["index.js", "hook.json", "README.md"],
  "engines": {
    "node": ">=14.0.0"
  }
}
```

2. Publish:
```bash
npm publish
```

3. Users can install:
```bash
npm install -g claude-hook-awesome
claude-hooks register claude-hook-awesome
```

## Troubleshooting Custom Hooks

### Common Issues

1. **Hook not executing**
   - Check file permissions: `chmod +x your-script`
   - Verify hook.json syntax
   - Check registration: `claude-hooks list --custom`

2. **Environment variables not available**
   - Ensure using latest Claude Hooks Manager
   - Check variable names (case-sensitive)

3. **Hook timing out**
   - Add progress output for long operations
   - Consider splitting into multiple hooks
   - Adjust timeout in configuration

### Debug Mode

Enable debug output:

```javascript
const DEBUG = process.env.CLAUDE_HOOK_DEBUG === 'true';

if (DEBUG) {
  console.log('Config:', config);
  console.log('Files:', stagedFiles);
}
```

Run with debug:
```bash
CLAUDE_HOOK_DEBUG=true git commit -m "test"
```

---

[← Hooks Reference](Hooks-Reference.md) | [Home](Home.md) | [Configuration Guide →](Configuration-Guide.md)