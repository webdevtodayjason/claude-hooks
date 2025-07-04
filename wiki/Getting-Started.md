# Getting Started

This guide will help you get up and running with Claude Hooks Manager quickly.

## Basic Concepts

### What are Git Hooks?

Git hooks are scripts that run automatically when certain Git events occur, such as:
- Before a commit (`pre-commit`)
- After writing a commit message (`commit-msg`)
- Before pushing (`pre-push`)

### Why Use Claude Hooks Manager?

- **Consistency**: Ensure all team members use the same hooks
- **Automation**: Automate repetitive tasks
- **Quality**: Catch issues before they reach the repository
- **AI-Enhanced**: Leverage Claude AI for better development workflows

## Quick Start

### Step 1: Initialize in Your Project

Navigate to your Git repository and initialize Claude Hooks Manager:

```bash
cd your-project
claude-hooks init
```

This creates a `.claude-hooks` directory in your project with configuration files.

### Step 2: Install Your First Hook

Let's install a pre-commit formatting hook:

```bash
claude-hooks install format-check
```

### Step 3: Test the Hook

Make a change to a file and try to commit:

```bash
echo "const x=1" > test.js
git add test.js
git commit -m "Test commit"
```

The hook will run and check formatting before allowing the commit.

## Essential Commands

### Installing Hooks

```bash
# Install a specific hook
claude-hooks install <hook-name>

# Install multiple hooks
claude-hooks install format-check lint-check

# Install all recommended hooks
claude-hooks install --defaults
```

### Managing Hooks

```bash
# List all available hooks
claude-hooks list

# Show installed hooks status
claude-hooks status

# Remove a hook
claude-hooks remove <hook-name>

# Disable a hook temporarily
claude-hooks disable <hook-name>

# Enable a disabled hook
claude-hooks enable <hook-name>
```

### Running Hooks Manually

```bash
# Run a specific hook
claude-hooks run <hook-name>

# Run all installed hooks
claude-hooks run --all
```

## Common Workflows

### Setting Up a New Project

```bash
# Initialize Claude Hooks Manager
claude-hooks init

# Install recommended hooks for your project type
claude-hooks install --defaults --type node

# Verify installation
claude-hooks status
```

### Adding to an Existing Project

```bash
# Initialize without overwriting existing hooks
claude-hooks init --preserve-existing

# Gradually add hooks
claude-hooks install format-check
claude-hooks install lint-check
```

### Team Collaboration

1. Commit the `.claude-hooks` directory to your repository
2. Team members run:
   ```bash
   claude-hooks sync
   ```
3. This ensures everyone has the same hooks configured

## Hook Categories

### Code Quality Hooks

- **format-check**: Ensures consistent code formatting
- **lint-check**: Catches potential issues and style violations
- **type-check**: TypeScript/Flow type checking

### Testing Hooks

- **test-check**: Runs relevant tests for changed files
- **test-suite**: Runs full test suite (pre-push)

### Commit Hooks

- **commit-format**: Enforces conventional commit format
- **ai-commit-msg**: Enhances commit messages with AI

### Build Hooks

- **build-check**: Ensures project builds successfully
- **bundle-size**: Checks bundle size limits

## Configuration Basics

Claude Hooks Manager uses a `.claude-hooks/config.json` file:

```json
{
  "hooks": {
    "format-check": {
      "enabled": true,
      "config": {
        "prettier": true,
        "eslint": true
      }
    }
  },
  "global": {
    "autoUpdate": true,
    "colorOutput": true
  }
}
```

Learn more in the [Configuration Guide](Configuration-Guide.md).

## Best Practices

1. **Start Small**: Begin with one or two hooks and add more gradually
2. **Use Defaults**: The default hooks are well-tested and cover common needs
3. **Customize Carefully**: Test custom hooks thoroughly before sharing
4. **Document Custom Hooks**: Help your team understand any custom hooks
5. **Regular Updates**: Keep Claude Hooks Manager updated for new features

## Troubleshooting Quick Fixes

### Hook Not Running

```bash
# Check if hook is installed and enabled
claude-hooks status

# Reinstall the hook
claude-hooks remove <hook-name>
claude-hooks install <hook-name>
```

### Hook Failing Incorrectly

```bash
# Run hook with debug output
claude-hooks run <hook-name> --debug

# Check hook configuration
claude-hooks config <hook-name>
```

## Next Steps

- Explore all available hooks in the [Hooks Reference](Hooks-Reference.md)
- Learn to create your own in [Creating Custom Hooks](Creating-Custom-Hooks.md)
- Deep dive into [Configuration](Configuration-Guide.md)
- Check out [API Reference](API-Reference.md) for advanced usage

---

[← Installation Guide](Installation-Guide.md) | [Home](Home.md) | [Hooks Reference →](Hooks-Reference.md)