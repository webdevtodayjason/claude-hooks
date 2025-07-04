# Frequently Asked Questions

Common questions about Claude Hooks Manager.

## General Questions

### What is Claude Hooks Manager?

Claude Hooks Manager is a tool that simplifies the installation and management of Git hooks, specifically optimized for AI-assisted development with Claude. It provides pre-configured hooks for common development tasks and allows you to create custom hooks.

### How is this different from Husky or other hook managers?

Key differences:

1. **AI-Optimized**: Includes hooks specifically designed for AI-assisted development
2. **Zero Configuration**: Works out of the box with sensible defaults
3. **Language Agnostic**: Supports multiple languages and frameworks
4. **Interactive**: Provides interactive prompts and AI-enhanced features
5. **Modular**: Easy to enable/disable individual hooks

### Is Claude Hooks Manager free?

Yes, Claude Hooks Manager is open source and free to use under the MIT license.

### What are the system requirements?

- Node.js 14 or higher
- Git 2.9 or higher
- npm, yarn, pnpm, or bun package manager

## Installation Questions

### Can I use Claude Hooks Manager with existing Git hooks?

Yes! Claude Hooks Manager can:
- Preserve existing hooks during installation
- Chain with existing hooks
- Import hooks from other managers

```bash
claude-hooks init --preserve-existing
```

### Do I need to install globally or locally?

Both options are supported:

- **Global**: Recommended for ease of use across projects
- **Local**: Better for project-specific configurations

### How do I update Claude Hooks Manager?

```bash
# Global update
npm update -g claude-hooks-manager

# Local update
npm update claude-hooks-manager

# Check for updates
claude-hooks update --check
```

## Usage Questions

### How do I temporarily skip hooks?

Several methods:

```bash
# Skip all hooks for one commit
git commit --no-verify -m "Emergency fix"

# Disable specific hook temporarily
claude-hooks disable format-check

# Set environment variable
CLAUDE_HOOKS_SKIP=true git commit -m "Skip hooks"
```

### Can I run hooks manually?

Yes, you can run any hook manually:

```bash
# Run specific hook
claude-hooks run format-check

# Run all hooks
claude-hooks run --all

# Test run without side effects
claude-hooks run lint-check --dry-run
```

### How do I share hooks with my team?

1. Commit the `.claude-hooks` directory to your repository
2. Team members run:
```bash
claude-hooks sync
```

### Can I use different hooks for different branches?

Yes, using branch-specific configuration:

```json
{
  "branchConfigs": {
    "main": {
      "hooks": {
        "test-suite": { "enabled": true }
      }
    },
    "develop": {
      "hooks": {
        "test-check": { "enabled": true }
      }
    }
  }
}
```

## Configuration Questions

### Where are configuration files stored?

- **Project config**: `.claude-hooks/config.json`
- **Global config**: `~/.claude-hooks/config.json`
- **Cache**: `~/.claude-hooks/cache/`

### How do I configure hooks for a monorepo?

```json
{
  "globals": {
    "monorepo": true,
    "workspaces": ["packages/*", "apps/*"]
  },
  "workspaceOverrides": {
    "packages/ui": {
      "hooks": {
        "visual-test": { "enabled": true }
      }
    }
  }
}
```

### Can I use environment variables in configuration?

Yes, environment variables are expanded:

```json
{
  "hooks": {
    "deploy-check": {
      "config": {
        "apiKey": "${DEPLOY_API_KEY}",
        "environment": "${NODE_ENV:-development}"
      }
    }
  }
}
```

## Hook-Specific Questions

### Why is my format-check hook not working?

Common issues:

1. **Missing formatter**: Install prettier/eslint
2. **Configuration conflict**: Check `.prettierrc` and `.eslintrc`
3. **File not staged**: Only staged files are checked

Debug:
```bash
claude-hooks run format-check --debug
```

### How do I make commit-format less strict?

Customize the configuration:

```json
{
  "hooks": {
    "commit-format": {
      "config": {
        "types": ["feat", "fix", "docs", "style", "refactor", "test", "chore", "wip"],
        "requireScope": false,
        "maxLength": 100
      }
    }
  }
}
```

### Can I skip hooks for certain file types?

Yes, use file filters:

```json
{
  "hooks": {
    "lint-check": {
      "config": {
        "include": ["src/**/*.js"],
        "exclude": ["**/*.test.js", "**/*.spec.js"]
      }
    }
  }
}
```

## Performance Questions

### Why are hooks running slowly?

Common causes and solutions:

1. **Large repository**: Enable changed-only mode
2. **Sequential execution**: Enable parallel mode
3. **No caching**: Enable cache
4. **Too many files**: Add exclusion patterns

### How can I speed up test hooks?

```json
{
  "hooks": {
    "test-check": {
      "config": {
        "changedOnly": true,
        "parallel": true,
        "cache": true,
        "bail": true
      }
    }
  }
}
```

### Do hooks run in CI/CD pipelines?

By default, hooks skip in CI to avoid duplication. Override:

```json
{
  "globals": {
    "skipCI": false
  }
}
```

## Troubleshooting Questions

### How do I debug a failing hook?

1. Run with debug flag:
```bash
claude-hooks run failing-hook --debug
```

2. Check logs:
```bash
claude-hooks logs failing-hook
```

3. Run diagnostic:
```bash
claude-hooks doctor
```

### What does "hook not found" mean?

This error occurs when:
- Hook is not installed: `claude-hooks install hook-name`
- Hook name is misspelled: `claude-hooks list`
- Custom hook not registered: `claude-hooks register hook-name`

### How do I report a bug?

1. Check existing issues on GitHub
2. Run `claude-hooks info --system`
3. Create issue with:
   - System information
   - Steps to reproduce
   - Error messages
   - Configuration

## Advanced Questions

### Can I create hooks in languages other than JavaScript?

Yes! Hooks can be written in any language:

```json
{
  "name": "python-hook",
  "executable": "check.py",
  "interpreter": "python3"
}
```

### How do I create a company-wide hook preset?

1. Create npm package with hooks
2. Publish to registry
3. Teams install:
```bash
npm install -g @company/claude-hooks-preset
claude-hooks use @company/claude-hooks-preset
```

### Can hooks modify files automatically?

Yes, but use caution:

```json
{
  "hooks": {
    "format-check": {
      "config": {
        "autoFix": true,
        "stageFixed": true
      }
    }
  }
}
```

### How do I integrate with my IDE?

Most IDEs respect Git hooks automatically. For specific integrations:

- **VS Code**: Install Claude Hooks extension
- **WebStorm**: Configure Git hooks in settings
- **Vim**: Use fugitive.vim or similar

## Security Questions

### Are hooks safe to use?

- Official hooks are reviewed and tested
- Custom hooks run with your permissions
- Always review hooks before installation
- Use `--dry-run` to test safely

### Can hooks access sensitive data?

Hooks run with your user permissions, so:
- Review custom hooks carefully
- Don't commit sensitive data in hook configs
- Use environment variables for secrets

### How do I audit installed hooks?

```bash
# List all hooks and their sources
claude-hooks audit

# Verify hook integrity
claude-hooks verify

# Show hook permissions
claude-hooks permissions
```

## Contributing Questions

### How can I contribute to Claude Hooks Manager?

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

See [Contributing Guide](Contributing.md) for details.

### Can I submit my custom hooks?

Yes! We welcome hook contributions:

1. Ensure hook is well-tested
2. Add documentation
3. Submit PR to the community hooks repository

### How do I become a maintainer?

Active contributors may be invited to become maintainers. Contribute regularly and engage with the community.

---

[← Troubleshooting](Troubleshooting.md) | [Home](Home.md) | [Contributing →](Contributing.md)