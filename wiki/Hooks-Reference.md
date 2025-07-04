# Hooks Reference

Complete reference for all available hooks in Claude Hooks Manager.

## Pre-commit Hooks

Pre-commit hooks run before a commit is created. They can prevent commits that don't meet quality standards.

### format-check

**Purpose**: Ensures consistent code formatting across the project.

**Supported Tools**:
- Prettier
- ESLint (with --fix)
- Black (Python)
- rustfmt (Rust)

**Configuration**:
```json
{
  "format-check": {
    "prettier": true,
    "eslint": true,
    "extensions": ["js", "jsx", "ts", "tsx", "json", "css", "md"]
  }
}
```

**Example**:
```bash
claude-hooks install format-check
```

### lint-check

**Purpose**: Runs linting tools on staged files to catch potential issues.

**Supported Tools**:
- ESLint
- TSLint
- Pylint
- RuboCop

**Configuration**:
```json
{
  "lint-check": {
    "eslint": {
      "fix": false,
      "maxWarnings": 10
    },
    "failOnWarning": false
  }
}
```

### test-check

**Purpose**: Runs tests related to changed files before committing.

**Features**:
- Only runs tests for modified files
- Supports watch mode integration
- Configurable test patterns

**Configuration**:
```json
{
  "test-check": {
    "pattern": "**/*.test.{js,jsx,ts,tsx}",
    "coverage": true,
    "bail": true
  }
}
```

### type-check

**Purpose**: Performs TypeScript or Flow type checking on staged files.

**Configuration**:
```json
{
  "type-check": {
    "typescript": true,
    "strict": true,
    "skipLibCheck": true
  }
}
```

### security-check

**Purpose**: Scans for security vulnerabilities in dependencies and code.

**Features**:
- Dependency vulnerability scanning
- Secret detection
- Security best practices checking

**Configuration**:
```json
{
  "security-check": {
    "auditLevel": "moderate",
    "scanSecrets": true,
    "excludePaths": ["test/", "docs/"]
  }
}
```

## Commit Message Hooks

These hooks run after you write a commit message but before the commit is finalized.

### commit-format

**Purpose**: Enforces conventional commit message format.

**Format**: `type(scope): subject`

**Valid Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test updates
- `chore`: Maintenance tasks

**Configuration**:
```json
{
  "commit-format": {
    "types": ["feat", "fix", "docs", "style", "refactor", "test", "chore"],
    "maxLength": 72,
    "requireScope": false
  }
}
```

### ai-commit-msg

**Purpose**: Enhances commit messages using Claude AI.

**Features**:
- Analyzes staged changes
- Suggests improved commit messages
- Maintains conventional format
- Adds context and clarity

**Configuration**:
```json
{
  "ai-commit-msg": {
    "style": "conventional",
    "maxLength": 72,
    "includeContext": true,
    "interactive": true
  }
}
```

### spell-check-msg

**Purpose**: Checks commit messages for spelling errors.

**Configuration**:
```json
{
  "spell-check-msg": {
    "language": "en-US",
    "customDictionary": [".claude-hooks/dictionary.txt"],
    "ignoreUrls": true
  }
}
```

## Pre-push Hooks

Pre-push hooks run before code is pushed to a remote repository.

### test-suite

**Purpose**: Runs the full test suite before pushing.

**Features**:
- Parallel test execution
- Coverage reporting
- Performance benchmarks

**Configuration**:
```json
{
  "test-suite": {
    "parallel": true,
    "coverage": {
      "threshold": 80,
      "reportDir": "coverage/"
    },
    "timeout": 300000
  }
}
```

### build-check

**Purpose**: Ensures the project builds successfully before pushing.

**Configuration**:
```json
{
  "build-check": {
    "command": "npm run build",
    "checkSize": true,
    "maxSize": "500kb",
    "failOnWarning": true
  }
}
```

### doc-check

**Purpose**: Validates documentation before pushing.

**Features**:
- Checks for broken links
- Validates markdown syntax
- Ensures API docs are updated

**Configuration**:
```json
{
  "doc-check": {
    "checkLinks": true,
    "validateMarkdown": true,
    "requiredFiles": ["README.md", "CHANGELOG.md"]
  }
}
```

## Post-commit Hooks

These hooks run after a commit is created.

### notify-team

**Purpose**: Sends notifications about commits to team channels.

**Configuration**:
```json
{
  "notify-team": {
    "slack": {
      "webhook": "https://hooks.slack.com/...",
      "channel": "#commits"
    },
    "includeStats": true
  }
}
```

### update-changelog

**Purpose**: Automatically updates CHANGELOG.md based on commits.

**Configuration**:
```json
{
  "update-changelog": {
    "file": "CHANGELOG.md",
    "format": "keepachangelog",
    "unreleased": true
  }
}
```

## Custom Hook Support

### script-runner

**Purpose**: Runs custom scripts as hooks.

**Configuration**:
```json
{
  "script-runner": {
    "pre-commit": "./scripts/pre-commit.sh",
    "commit-msg": "node ./scripts/validate-commit.js"
  }
}
```

## Hook Combinations

### Recommended Combinations

#### For JavaScript/TypeScript Projects
```bash
claude-hooks install format-check lint-check type-check test-check commit-format
```

#### For Python Projects
```bash
claude-hooks install format-check lint-check test-check commit-format
```

#### For Documentation Projects
```bash
claude-hooks install spell-check-msg doc-check commit-format
```

## Advanced Configuration

### Global Hook Settings

```json
{
  "global": {
    "skipCI": true,
    "verbose": false,
    "parallel": true,
    "timeout": 60000
  }
}
```

### Per-Hook Overrides

```json
{
  "hooks": {
    "test-check": {
      "enabled": true,
      "skipCI": false,
      "timeout": 120000
    }
  }
}
```

## Performance Tips

1. **Use Parallel Execution**: Enable for hooks that support it
2. **Configure Timeouts**: Set appropriate timeouts for long-running hooks
3. **Skip in CI**: Use `skipCI` for hooks that duplicate CI checks
4. **Selective Running**: Configure hooks to only check relevant files

---

[← Getting Started](Getting-Started.md) | [Home](Home.md) | [Creating Custom Hooks →](Creating-Custom-Hooks.md)