# Claude Code Hooks

A comprehensive collection of hooks for [Claude Code](https://claude.ai/code) that enforce coding standards, maintain consistency, and automate workflow tasks across all projects.

## 📚 Documentation

- [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Claude Code Setup Guide](https://docs.anthropic.com/en/docs/claude-code/setup)
- [Model Context Protocol (MCP)](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Claude Code SDK](https://docs.anthropic.com/en/docs/claude-code/sdk)

## Features

### 🔒 Quality Gates
- **Pre-commit validation** - Run tests, linting, and TypeScript checks before commits
- **Commit message standards** - Enforce conventional commits and block co-authored commits
- **Code quality checks** - Automatic validation of code style and patterns

### 🛡️ Safety & Consistency
- **Database protection** - Prevent unnecessary table creation, encourage extending existing schemas
- **Duplicate prevention** - Detect duplicate routes, components, and API endpoints
- **Style enforcement** - Ensure theme-aware CSS, ShadCN usage, and consistent styling
- **API verification** - Validate endpoint configuration, authentication, and naming conventions

### 🔄 Workflow Automation
- **Dart integration** - Enforce task hierarchy and documentation sync
- **Command logging** - Track all bash commands with timestamps
- **Session reminders** - End-of-session summaries and pending task reminders
- **MCP tool suggestions** - Recommend MCP tools when alternatives are available

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/webdevtodayjason/claude-hooks.git
cd claude-hooks

# Run the install script
chmod +x install.sh
./install.sh
```

### Manual Installation

1. Create the hooks directory:
   ```bash
   mkdir -p ~/.claude/hooks
   ```

2. Copy all Python hooks:
   ```bash
   cp *.py ~/.claude/hooks/
   chmod +x ~/.claude/hooks/*.py
   ```

3. Update your Claude Code settings:
   - If `~/.claude/settings.json` exists, merge the hooks configuration from `settings.example.json`
   - If not, copy `settings.example.json` to `~/.claude/settings.json`

4. Restart Claude Code for the hooks to take effect

## Hooks Overview

| Hook | Trigger | Purpose |
|------|---------|---------|
| `pre-commit-validator.py` | Before git commit/push | Runs tests, linting, TypeScript checks |
| `validate-git-commit.py` | Before git commit | Enforces commit message standards |
| `database-extension-check.py` | When editing schemas | Prevents unnecessary table creation |
| `duplicate-detector.py` | When creating files | Prevents duplicate code/routes |
| `style-consistency.py` | When editing TSX/CSS | Enforces theme-aware styling |
| `api-endpoint-verifier.py` | When editing API routes | Validates endpoint configuration |
| `validate-dart-task.py` | Creating Dart tasks | Ensures proper task hierarchy |
| `sync-docs-to-dart.py` | After creating .md files | Reminds to sync docs |
| `log-commands.py` | Before bash commands | Logs all commands |
| `mcp-tool-enforcer.py` | Various operations | Suggests MCP tool usage |
| `session-end-summary.py` | Session end | Provides reminders |

## Configuration

Hooks are configured in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

See `settings.example.json` for the complete configuration.

## Customization

### Disable a Hook
Edit `~/.claude/settings.json` and remove or comment out the specific hook entry.

### Add Custom Hooks
1. Create a Python script in `~/.claude/hooks/`
2. Make it executable: `chmod +x your-hook.py`
3. Add it to the appropriate section in `settings.json`

### Hook Exit Codes
- `0` - Success, continue normally
- `2` - Blocking error, prevents tool execution
- Other - Non-blocking error, shows message but continues

## Best Practices

1. **Performance** - Keep hooks fast to avoid slowing down Claude Code
2. **Error Handling** - Always handle exceptions gracefully
3. **Clear Messages** - Provide actionable feedback
4. **Non-Blocking** - Use warnings for suggestions, only block on critical issues

## Troubleshooting

### Hooks Not Running
1. Restart Claude Code after installation
2. Check `~/.claude/settings.json` is valid JSON
3. Verify hook files are executable

### Testing Hooks
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"test"}}' | python3 ~/.claude/hooks/hook-name.py
```

## Log Files

- `~/.claude/bash-command-log.txt` - All bash commands
- `~/.claude/hooks/commands-YYYY-MM-DD.log` - Daily command logs
- `~/.claude/hooks/command-stats.json` - Command frequency stats
- `~/.claude/hooks/pending-dart-syncs.json` - Pending doc syncs

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new hooks
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

Created for the Claude Code community to enhance productivity and maintain code quality.

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [MCP Tools](https://docs.anthropic.com/en/docs/claude-code/mcp)