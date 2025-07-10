# Context Forge Hooks for Claude Code

This integration enables Claude Code to maintain project context across compaction events, enabling reliable multi-hour development workflows for Context Forge projects.

## Overview

When Claude Code's context window fills up, it performs "compaction" to continue the conversation. During this process, Claude can lose important project context, forcing you to remind it about project rules, current tasks, and implementation details.

These hooks solve this problem by:
1. Detecting Context Forge projects automatically
2. Capturing project state before compaction
3. Enforcing context refresh after compaction
4. Maintaining awareness of implementation stages and PRPs

## How It Works

### PreCompact Hook
- Runs before Claude Code compacts the conversation
- Detects if the current project uses Context Forge (has CLAUDE.md, Docs/, PRPs/)
- Creates a marker file for the Stop hook
- Prepares refresh instructions that will be shown after compaction

### Stop Hook  
- Runs when Claude finishes responding
- Checks for the compaction marker
- If compaction occurred, blocks Claude and provides instructions to:
  - Re-read CLAUDE.md for project rules
  - Check Implementation.md for current stage
  - Review relevant PRP files
  - Resume the interrupted task

## Installation

### Quick Install
```bash
./install-context-forge-hooks.sh
```

### Manual Installation

1. Copy hook scripts to Claude hooks directory:
```bash
mkdir -p ~/.claude/hooks/context-forge
cp precompact-context-refresh.py ~/.claude/hooks/context-forge/
cp stop-context-refresh.py ~/.claude/hooks/context-forge/
cp context-forge-utils.py ~/.claude/hooks/context-forge/
chmod +x ~/.claude/hooks/context-forge/*.py
```

2. Add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/context-forge/precompact-context-refresh.py",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/context-forge/stop-context-refresh.py",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## Usage

Once installed, the hooks work automatically:

1. **Start Claude Code** in a Context Forge project
2. **Work normally** - the hooks only activate for Context Forge projects
3. **When compaction occurs** (auto or manual), Claude will:
   - Be reminded to re-read project documentation
   - Know which implementation stage you're on
   - Continue with the correct context

## Context Forge Project Structure

The hooks detect these Context Forge files:
```
project-root/
├── CLAUDE.md                 # Main project rules and context
├── Docs/
│   ├── Implementation.md    # Staged development plan
│   ├── project_structure.md # File organization
│   ├── UI_UX_doc.md        # Design specs
│   └── Bug_tracking.md     # Known issues
├── PRPs/                   # Product Requirement Prompts
│   ├── base.md
│   ├── planning.md
│   └── validation-gate.md
└── .context-forge/
    └── config.json         # Context Forge configuration
```

## Features

### Intelligent Detection
- Only activates for Context Forge projects
- Checks for CLAUDE.md and other marker files
- Gracefully skips non-Context Forge projects

### Stage Awareness
- Tracks which Implementation.md stage is active
- Maintains progress through multi-stage projects
- Reminds Claude of current tasks

### PRP Integration
- Identifies relevant PRP files
- Ensures adherence to implementation guidelines
- Maintains quality standards

### Debug Logging
- Logs to `~/.claude/context-forge-hook.log`
- Helps troubleshoot hook behavior
- Track compaction events

## Troubleshooting

### Hooks Not Running
1. Check if hooks are registered: `/hooks` in Claude Code
2. Verify scripts are executable: `ls -la ~/.claude/hooks/context-forge/`
3. Check settings.json syntax: `cat ~/.claude/settings.json`

### Context Not Refreshing
1. Check log file: `tail -f ~/.claude/context-forge-hook.log`
2. Verify project has Context Forge files
3. Ensure Python 3 is available

### Manual Testing
```bash
# Test Context Forge detection
python3 ~/.claude/hooks/context-forge/context-forge-utils.py

# Check hook configuration
claude --debug
```

## Benefits

1. **Multi-Hour Workflows**: Work on complex projects without context loss
2. **Consistent Quality**: Maintain project standards across sessions
3. **Reduced Friction**: No need to manually remind Claude about context
4. **Better Compliance**: Automatic PRP and validation enforcement
5. **Progress Tracking**: Always know which implementation stage is active

## Contributing

To improve these hooks:
1. Fork the claude-hooks repository
2. Create a feature branch
3. Test with real Context Forge projects
4. Submit a pull request

## Credits

Created by the Claude Hooks and Context Forge communities to enable better AI-assisted development workflows.