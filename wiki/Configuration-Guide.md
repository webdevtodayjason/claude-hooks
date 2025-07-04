# Configuration Guide

Comprehensive guide to configuring Claude Hooks Manager for your projects.

## Configuration Overview

Claude Hooks Manager uses a layered configuration system:

1. **Default Configuration** - Built-in defaults
2. **Global Configuration** - User-level settings
3. **Project Configuration** - Project-specific settings
4. **Hook Configuration** - Individual hook settings
5. **Runtime Configuration** - Command-line overrides

## Configuration Files

### Project Configuration

Located at `.claude-hooks/config.json`:

```json
{
  "version": "1.0.0",
  "extends": "@company/claude-hooks-config",
  "globals": {
    "colorOutput": true,
    "verbose": false,
    "parallel": true,
    "skipCI": true
  },
  "hooks": {
    "format-check": {
      "enabled": true,
      "config": {
        "prettier": true,
        "eslint": true
      }
    }
  }
}
```

### Global Configuration

Located at `~/.claude-hooks/config.json`:

```json
{
  "defaultHooks": ["format-check", "lint-check", "commit-format"],
  "autoUpdate": true,
  "telemetry": false,
  "notifications": {
    "onError": true,
    "onSuccess": false
  }
}
```

## Configuration Properties

### Global Settings

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `colorOutput` | boolean | true | Enable colored terminal output |
| `verbose` | boolean | false | Show detailed execution logs |
| `parallel` | boolean | true | Run independent hooks in parallel |
| `skipCI` | boolean | true | Skip hooks in CI environment |
| `timeout` | number | 60000 | Global timeout in milliseconds |
| `interactive` | boolean | true | Allow interactive prompts |
| `failFast` | boolean | false | Stop on first hook failure |

### Hook-Specific Settings

Each hook can be configured individually:

```json
{
  "hooks": {
    "hook-name": {
      "enabled": true,
      "stage": "pre-commit",
      "priority": 10,
      "timeout": 30000,
      "skipCI": false,
      "config": {
        // Hook-specific configuration
      }
    }
  }
}
```

## Common Configuration Patterns

### JavaScript/TypeScript Project

```json
{
  "globals": {
    "parallel": true,
    "failFast": false
  },
  "hooks": {
    "format-check": {
      "enabled": true,
      "config": {
        "prettier": {
          "configFile": ".prettierrc",
          "ignorePath": ".prettierignore"
        },
        "extensions": ["js", "jsx", "ts", "tsx", "json", "css"]
      }
    },
    "lint-check": {
      "enabled": true,
      "config": {
        "eslint": {
          "configFile": ".eslintrc.js",
          "fix": false,
          "maxWarnings": 0
        }
      }
    },
    "type-check": {
      "enabled": true,
      "config": {
        "tsconfig": "tsconfig.json",
        "skipLibCheck": true
      }
    },
    "test-check": {
      "enabled": true,
      "config": {
        "pattern": "**/__tests__/**/*.test.{js,jsx,ts,tsx}",
        "coverage": true,
        "updateSnapshot": false
      }
    }
  }
}
```

### Python Project

```json
{
  "hooks": {
    "format-check": {
      "enabled": true,
      "config": {
        "black": {
          "lineLength": 88,
          "targetVersion": ["py38", "py39"]
        },
        "isort": {
          "profile": "black"
        }
      }
    },
    "lint-check": {
      "enabled": true,
      "config": {
        "pylint": {
          "rcfile": ".pylintrc"
        },
        "flake8": {
          "maxLineLength": 88,
          "ignore": ["E203", "W503"]
        }
      }
    }
  }
}
```

### Monorepo Configuration

```json
{
  "globals": {
    "monorepo": true,
    "workspaces": ["packages/*", "apps/*"]
  },
  "hooks": {
    "format-check": {
      "enabled": true,
      "config": {
        "respectWorkspaceConfig": true,
        "aggregateResults": true
      }
    },
    "test-check": {
      "enabled": true,
      "config": {
        "affectedOnly": true,
        "baseRef": "main"
      }
    }
  },
  "workspaceOverrides": {
    "packages/ui": {
      "hooks": {
        "visual-test": {
          "enabled": true
        }
      }
    }
  }
}
```

## Environment-Specific Configuration

### Development vs Production

```json
{
  "environments": {
    "development": {
      "globals": {
        "verbose": true,
        "failFast": false
      },
      "hooks": {
        "test-check": {
          "config": {
            "watch": true
          }
        }
      }
    },
    "production": {
      "globals": {
        "verbose": false,
        "failFast": true
      },
      "hooks": {
        "test-suite": {
          "enabled": true
        }
      }
    }
  }
}
```

Set environment:
```bash
CLAUDE_HOOKS_ENV=production git commit -m "Release"
```

### CI Configuration

```json
{
  "ci": {
    "provider": "auto", // auto-detect CI environment
    "config": {
      "parallel": true,
      "maxWorkers": 4,
      "bail": true,
      "coverage": {
        "threshold": {
          "global": {
            "branches": 80,
            "functions": 80,
            "lines": 80,
            "statements": 80
          }
        }
      }
    }
  }
}
```

## Advanced Configuration

### Hook Priorities

Control execution order with priorities (lower numbers run first):

```json
{
  "hooks": {
    "security-check": {
      "priority": 1
    },
    "format-check": {
      "priority": 10
    },
    "test-check": {
      "priority": 20
    }
  }
}
```

### Conditional Hooks

Enable hooks based on conditions:

```json
{
  "hooks": {
    "expensive-check": {
      "enabled": "${!CI && ENABLE_EXPENSIVE_CHECKS}",
      "conditions": {
        "branches": ["main", "develop"],
        "filePatterns": ["src/**/*.js"]
      }
    }
  }
}
```

### Custom Variables

Define reusable variables:

```json
{
  "variables": {
    "srcDir": "src",
    "testDir": "__tests__",
    "buildDir": "dist"
  },
  "hooks": {
    "test-check": {
      "config": {
        "testMatch": ["${testDir}/**/*.test.js"]
      }
    }
  }
}
```

### Extending Configurations

Share configurations across projects:

```json
{
  "extends": [
    "@company/claude-hooks-base",
    "@company/claude-hooks-javascript"
  ],
  "hooks": {
    // Override or add to extended configuration
  }
}
```

## Configuration Commands

### View Configuration

```bash
# Show effective configuration
claude-hooks config

# Show specific hook configuration
claude-hooks config format-check

# Show global configuration
claude-hooks config --global
```

### Set Configuration

```bash
# Set project configuration
claude-hooks config set hooks.format-check.enabled true

# Set global configuration
claude-hooks config set --global autoUpdate false

# Set hook-specific configuration
claude-hooks config set hooks.lint-check.config.maxWarnings 10
```

### Reset Configuration

```bash
# Reset to defaults
claude-hooks config reset

# Reset specific hook
claude-hooks config reset format-check
```

## Configuration Schema Validation

Claude Hooks Manager validates configuration against JSON schemas:

```json
{
  "$schema": "https://claude-hooks.dev/schema/v1/config.json",
  "hooks": {
    // Your configuration with IDE support
  }
}
```

## Performance Optimization

### Parallel Execution

```json
{
  "globals": {
    "parallel": true,
    "maxWorkers": 4
  },
  "parallelGroups": [
    ["format-check", "lint-check"],
    ["type-check", "test-check"]
  ]
}
```

### Caching

```json
{
  "cache": {
    "enabled": true,
    "directory": ".claude-hooks/cache",
    "ttl": 3600,
    "hashFiles": ["package-lock.json", "yarn.lock"]
  }
}
```

### File Filtering

```json
{
  "fileFilters": {
    "javascript": {
      "include": ["src/**/*.{js,jsx,ts,tsx}"],
      "exclude": ["**/*.test.js", "**/__mocks__/**"]
    }
  },
  "hooks": {
    "lint-check": {
      "fileFilter": "javascript"
    }
  }
}
```

## Troubleshooting Configuration

### Configuration Not Loading

1. Check file syntax:
```bash
claude-hooks config validate
```

2. Verify file location:
```bash
claude-hooks config --show-path
```

### Debugging Configuration

Enable debug mode:
```bash
CLAUDE_HOOKS_DEBUG=config git commit -m "test"
```

### Common Issues

1. **Conflicting configurations**
   - Project config overrides global
   - CLI flags override all configs

2. **Invalid JSON**
   - Use a JSON validator
   - Check for trailing commas

3. **Path resolution**
   - Use absolute paths or relative to project root
   - Environment variables are expanded

## Migration Guide

### From v1 to v2

```bash
# Automatic migration
claude-hooks migrate

# Manual migration
claude-hooks config upgrade
```

### From Other Hook Managers

```bash
# Import from Husky
claude-hooks import --from husky

# Import from Pre-commit
claude-hooks import --from pre-commit
```

---

[← Creating Custom Hooks](Creating-Custom-Hooks.md) | [Home](Home.md) | [Troubleshooting →](Troubleshooting.md)