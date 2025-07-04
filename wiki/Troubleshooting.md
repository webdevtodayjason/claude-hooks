# Troubleshooting

This guide helps you resolve common issues with Claude Hooks Manager.

## Common Issues

### Installation Issues

#### "command not found" after installation

**Problem**: After installing globally, `claude-hooks` command is not recognized.

**Solutions**:

1. Check npm global bin path:
```bash
npm config get prefix
# Add the bin directory to your PATH
export PATH="$(npm config get prefix)/bin:$PATH"
```

2. Reinstall globally with proper permissions:
```bash
sudo npm install -g claude-hooks-manager
# OR better, configure npm to not require sudo
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

3. Use npx instead:
```bash
npx claude-hooks-manager init
```

#### Permission denied during installation

**Problem**: npm install fails with EACCES error.

**Solution**: Configure npm to install global packages without sudo:
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
npm install -g claude-hooks-manager
```

### Hook Execution Issues

#### Hooks not running on commit

**Problem**: Git commits succeed without running configured hooks.

**Diagnostic steps**:

1. Check hook installation:
```bash
claude-hooks status
ls -la .git/hooks/
```

2. Verify Git hooks are executable:
```bash
chmod +x .git/hooks/*
```

3. Check if hooks are being bypassed:
```bash
# This bypasses hooks - don't use unless necessary
git commit --no-verify
```

4. Reinstall hooks:
```bash
claude-hooks remove --all
claude-hooks install --defaults
```

#### Hook fails with "command not found"

**Problem**: Hook scripts can't find required commands.

**Solutions**:

1. Ensure PATH is set correctly in hooks:
```bash
# Add to .claude-hooks/config.json
{
  "environment": {
    "PATH": "/usr/local/bin:/usr/bin:/bin:./node_modules/.bin"
  }
}
```

2. Use absolute paths in custom hooks:
```javascript
const eslint = path.join(process.cwd(), 'node_modules/.bin/eslint');
```

#### Hooks timing out

**Problem**: Hooks fail with timeout error.

**Solutions**:

1. Increase timeout for specific hooks:
```json
{
  "hooks": {
    "test-suite": {
      "timeout": 300000  // 5 minutes
    }
  }
}
```

2. Disable timeout for debugging:
```bash
claude-hooks run test-suite --no-timeout
```

3. Run hooks in parallel:
```json
{
  "globals": {
    "parallel": true,
    "maxWorkers": 4
  }
}
```

### Configuration Issues

#### Configuration not being applied

**Problem**: Changes to config.json don't take effect.

**Diagnostic steps**:

1. Validate configuration:
```bash
claude-hooks config validate
```

2. Check configuration hierarchy:
```bash
# Show effective configuration
claude-hooks config --effective

# Show where configuration is loaded from
claude-hooks config --show-sources
```

3. Clear configuration cache:
```bash
claude-hooks cache clear
```

#### Invalid configuration error

**Problem**: "Invalid configuration" error when running hooks.

**Solutions**:

1. Check JSON syntax:
```bash
# Validate JSON syntax
jq . .claude-hooks/config.json

# Or use Claude Hooks validator
claude-hooks config validate
```

2. Common JSON errors:
- Trailing commas
- Missing quotes around keys
- Incorrect value types

3. Use configuration schema:
```json
{
  "$schema": "https://claude-hooks.dev/schema/v1/config.json",
  // Your config with IDE validation
}
```

### Performance Issues

#### Hooks running slowly

**Problem**: Hooks take too long to execute.

**Optimization strategies**:

1. Enable parallel execution:
```json
{
  "globals": {
    "parallel": true
  }
}
```

2. Run only on changed files:
```json
{
  "hooks": {
    "lint-check": {
      "config": {
        "changedOnly": true
      }
    }
  }
}
```

3. Use caching:
```json
{
  "cache": {
    "enabled": true,
    "ttl": 3600
  }
}
```

4. Profile hook execution:
```bash
claude-hooks run --profile
```

#### Memory issues with large repositories

**Problem**: Hooks fail with heap out of memory error.

**Solutions**:

1. Increase Node.js memory:
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
```

2. Process files in batches:
```json
{
  "globals": {
    "batchSize": 50
  }
}
```

3. Exclude unnecessary files:
```json
{
  "fileFilters": {
    "exclude": ["node_modules/**", "dist/**", "coverage/**"]
  }
}
```

### Platform-Specific Issues

#### Windows Issues

**Line ending problems**:
```bash
# Configure Git to handle line endings
git config --global core.autocrlf true

# Configure hooks to handle CRLF
{
  "globals": {
    "lineEndings": "auto"
  }
}
```

**Path separator issues**:
- Use forward slashes in configurations
- Use `path.join()` in custom hooks

**Script execution policy**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### macOS Issues

**Xcode command line tools required**:
```bash
xcode-select --install
```

**File watching limits**:
```bash
# Increase file descriptor limit
ulimit -n 2048
```

#### Linux Issues

**Permissions on CI**:
```bash
# In CI configuration
before_script:
  - chmod +x .git/hooks/*
```

### Integration Issues

#### Conflicts with existing hooks

**Problem**: Existing Git hooks conflict with Claude Hooks Manager.

**Solutions**:

1. Backup and migrate existing hooks:
```bash
claude-hooks init --preserve-existing
claude-hooks migrate-hooks
```

2. Chain existing hooks:
```json
{
  "hooks": {
    "custom-wrapper": {
      "type": "pre-commit",
      "command": "sh .git/hooks/pre-commit.old && claude-hooks run pre-commit"
    }
  }
}
```

#### CI/CD pipeline failures

**Problem**: Hooks fail in CI but work locally.

**Common causes and solutions**:

1. Missing dependencies:
```yaml
# .github/workflows/ci.yml
- name: Install dependencies
  run: |
    npm ci
    npm install -g claude-hooks-manager
```

2. Skip certain hooks in CI:
```json
{
  "globals": {
    "skipCI": true
  },
  "hooks": {
    "interactive-hook": {
      "skipCI": true
    }
  }
}
```

3. CI-specific configuration:
```bash
# Set CI environment
export CI=true
export CLAUDE_HOOKS_ENV=ci
```

## Debugging Techniques

### Enable Debug Mode

```bash
# Debug all hooks
export CLAUDE_HOOKS_DEBUG=*
git commit -m "test"

# Debug specific hook
export CLAUDE_HOOKS_DEBUG=format-check
git commit -m "test"

# Debug configuration loading
export CLAUDE_HOOKS_DEBUG=config
claude-hooks status
```

### Verbose Output

```bash
# Run with verbose output
claude-hooks run format-check --verbose

# Or set in configuration
{
  "globals": {
    "verbose": true
  }
}
```

### Test Hooks Individually

```bash
# Test hook without committing
claude-hooks run format-check --test

# Test with specific files
claude-hooks run lint-check --files "src/index.js,src/utils.js"

# Test with custom configuration
claude-hooks run test-check --config '{"coverage": false}'
```

### Check Hook Environment

```bash
# Create a debug hook
cat > .claude-hooks/custom/debug-env/index.js << 'EOF'
#!/usr/bin/env node
console.log('Environment Variables:');
Object.keys(process.env).filter(key => key.startsWith('CLAUDE_')).forEach(key => {
  console.log(`${key}=${process.env[key]}`);
});
EOF

chmod +x .claude-hooks/custom/debug-env/index.js
claude-hooks run debug-env
```

## Getting Help

### Self-Help Resources

1. **Check the logs**:
```bash
# View recent hook execution logs
claude-hooks logs

# View logs for specific hook
claude-hooks logs format-check
```

2. **Validate your setup**:
```bash
# Run diagnostic checks
claude-hooks doctor

# Check specific subsystems
claude-hooks doctor --hooks
claude-hooks doctor --config
claude-hooks doctor --git
```

3. **Search documentation**:
```bash
# Search CLI help
claude-hooks help search <term>

# Search online docs
claude-hooks docs search <term>
```

### Community Support

1. **GitHub Issues**: Search existing issues or create new ones
2. **Discord Community**: Join our Discord for real-time help
3. **Stack Overflow**: Tag questions with `claude-hooks-manager`

### Reporting Bugs

When reporting issues, include:

1. **System information**:
```bash
claude-hooks info --system
```

2. **Configuration**:
```bash
claude-hooks config --show
```

3. **Debug output**:
```bash
CLAUDE_HOOKS_DEBUG=* claude-hooks run <failing-hook> 2> debug.log
```

4. **Minimal reproduction**:
- Steps to reproduce
- Expected behavior
- Actual behavior

## Emergency Procedures

### Disable All Hooks Temporarily

```bash
# Disable all hooks
claude-hooks disable --all

# Re-enable when fixed
claude-hooks enable --all
```

### Remove Claude Hooks Manager

```bash
# Remove from project
claude-hooks uninstall

# Remove globally
npm uninstall -g claude-hooks-manager
```

### Reset to Defaults

```bash
# Reset configuration
claude-hooks config reset

# Reinstall default hooks
claude-hooks install --defaults --force
```

---

[← Configuration Guide](Configuration-Guide.md) | [Home](Home.md) | [FAQ →](FAQ.md)