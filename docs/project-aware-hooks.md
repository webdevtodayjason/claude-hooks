# Project-Aware Hooks Configuration

The `session-end-summary.py` and `sync-docs-to-dart.py` hooks are now project-aware and store data locally within each project instead of globally.

## Configuration Files

### `.claude/dart-config.json`

Controls Dart integration features:

```json
{
  "enable_doc_sync": true,
  "default_docs_folder": "holace/Docs",
  "workspace": "holace",
  "dartboard": "holace/Tasks"
}
```

- `enable_doc_sync`: Whether to enable automatic reminders for syncing .md files to Dart
- `default_docs_folder`: Default folder suggestion for Dart document creation
- `workspace`: Your Dart workspace name
- `dartboard`: Default dartboard for task creation

### `.claude/session-summary.json`

Controls session end summary behavior:

```json
{
  "show_dart_reminders": true,
  "show_git_reminders": true,
  "custom_reminders": [
    "All new tasks must have a Phase parent",
    "Run tests before committing",
    "Use theme-aware CSS classes"
  ]
}
```

- `show_dart_reminders`: Show Dart-specific reminders (auto-detected if not set)
- `show_git_reminders`: Show git-related reminders
- `custom_reminders`: Project-specific reminder messages

### `.claude/sync-config.json` (Alternative)

For projects that want to control sync behavior without full Dart config:

```json
{
  "dart_sync_enabled": false
}
```

## Data Storage

### Pending Syncs

Pending document syncs are now stored in:
- Primary: `<project-root>/.claude/pending-dart-syncs.json`
- Fallback: `~/.claude/hooks/pending-dart-syncs.json` (if project directory is not writable)

The sync file stores up to 50 recent pending syncs with timestamps.

## Auto-Detection

If no configuration files exist, the hooks will:

1. Check for `.claude/dart-config.json` in the project
2. Check for Dart-related content in `~/.claude/CLAUDE.md`
3. Look for `mcp__dart__` or `Dart MCP` mentions

## Migration from Global Storage

To migrate existing global data to project-specific storage:

1. Copy `~/.claude/hooks/pending-dart-syncs.json` to `<project>/.claude/pending-dart-syncs.json`
2. Create appropriate configuration files in your project's `.claude` directory
3. The hooks will automatically use project-local storage going forward

## Disabling Features

To disable Dart sync for a specific project:

1. Create `.claude/dart-config.json` with `"enable_doc_sync": false`
2. Or create `.claude/sync-config.json` with `"dart_sync_enabled": false`

To disable all session summaries:

1. Remove the `session-end-summary.py` hook from your hooks configuration
2. Or configure the hook to show minimal reminders

## Example Setup

For a project using Dart integration:

```bash
mkdir -p .claude
cp /path/to/claude-hooks-repo/.claude/dart-config.example.json .claude/dart-config.json
cp /path/to/claude-hooks-repo/.claude/session-summary.example.json .claude/session-summary.json
# Edit the files to match your project settings
```

For a project without Dart:

```bash
mkdir -p .claude
echo '{"dart_sync_enabled": false}' > .claude/sync-config.json
echo '{"show_dart_reminders": false, "show_git_reminders": true}' > .claude/session-summary.json
```