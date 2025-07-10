#!/bin/bash

# Context Forge Hooks Installation Script
# This script installs the Context Forge integration hooks for Claude Code

set -e

echo "Context Forge Hooks Installer"
echo "============================"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Determine the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Claude hooks directory
CLAUDE_HOOKS_DIR="$HOME/.claude/hooks"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"

# Create Claude directories if they don't exist
mkdir -p "$CLAUDE_HOOKS_DIR/context-forge"
mkdir -p "$HOME/.claude"

echo "Installing Context Forge hooks..."

# Copy hook scripts
cp "$SCRIPT_DIR/precompact-context-refresh.py" "$CLAUDE_HOOKS_DIR/context-forge/" && \
    echo -e "${GREEN}✓${NC} Installed PreCompact hook"

cp "$SCRIPT_DIR/stop-context-refresh.py" "$CLAUDE_HOOKS_DIR/context-forge/" && \
    echo -e "${GREEN}✓${NC} Installed Stop hook"

cp "$SCRIPT_DIR/context-forge-utils.py" "$CLAUDE_HOOKS_DIR/context-forge/" && \
    echo -e "${GREEN}✓${NC} Installed utility functions"

# Make scripts executable
chmod +x "$CLAUDE_HOOKS_DIR/context-forge/"*.py

echo
echo "Updating Claude settings..."

# Check if settings.json exists
if [ -f "$CLAUDE_SETTINGS" ]; then
    # Backup existing settings
    cp "$CLAUDE_SETTINGS" "$CLAUDE_SETTINGS.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}⚠${NC}  Backed up existing settings.json"
    
    # Check if hooks are already configured
    if grep -q "context-forge" "$CLAUDE_SETTINGS"; then
        echo -e "${YELLOW}⚠${NC}  Context Forge hooks already configured in settings.json"
        echo "    Please check your settings to ensure they're up to date"
    else
        # We need to merge the hooks configuration
        # This is a simplified approach - in production, use jq or similar
        echo -e "${YELLOW}⚠${NC}  Please manually add the following to your settings.json:"
        echo
        cat << 'EOF'
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
EOF
    fi
else
    # Create new settings.json with our hooks
    cat > "$CLAUDE_SETTINGS" << 'EOF'
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
EOF
    echo -e "${GREEN}✓${NC} Created new settings.json with Context Forge hooks"
fi

echo
echo -e "${GREEN}Installation complete!${NC}"
echo
echo "What the hooks do:"
echo "- PreCompact: Detects Context Forge projects and prepares refresh instructions"
echo "- Stop: After compaction, enforces re-reading of CLAUDE.md, PRPs, and Implementation.md"
echo
echo "To test:"
echo "1. Navigate to a Context Forge project (has CLAUDE.md, Docs/, PRPs/)"
echo "2. Work until auto-compaction occurs or use /compact"
echo "3. The hooks will ensure context is maintained"
echo
echo "Log file: ~/.claude/context-forge-hook.log"
echo

# Optional: Test the installation
read -p "Would you like to test the hooks? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing Context Forge detection..."
    python3 "$CLAUDE_HOOKS_DIR/context-forge/context-forge-utils.py"
fi