#!/bin/bash
# Example script to set up project-specific hook configuration

echo "Setting up project-specific Claude hook configuration..."

# Create .claude directory if it doesn't exist
mkdir -p .claude

# Option 1: Enable Dart integration for this project
setup_dart_project() {
    cat > .claude/dart-config.json << EOF
{
  "enable_doc_sync": true,
  "default_docs_folder": "your-workspace/Docs",
  "workspace": "your-workspace",
  "dartboard": "your-workspace/Tasks"
}
EOF
    
    cat > .claude/session-summary.json << EOF
{
  "show_dart_reminders": true,
  "show_git_reminders": true,
  "custom_reminders": [
    "Update task status in Dart",
    "Sync documentation to Dart",
    "Run tests before committing"
  ]
}
EOF
    
    echo "✓ Dart integration enabled for this project"
}

# Option 2: Disable Dart for a non-Dart project
disable_dart_project() {
    cat > .claude/sync-config.json << EOF
{
  "dart_sync_enabled": false
}
EOF
    
    cat > .claude/session-summary.json << EOF
{
  "show_dart_reminders": false,
  "show_git_reminders": true,
  "custom_reminders": []
}
EOF
    
    echo "✓ Dart integration disabled for this project"
}

# Option 3: Custom reminders only
custom_reminders_only() {
    cat > .claude/session-summary.json << EOF
{
  "show_dart_reminders": false,
  "show_git_reminders": true,
  "custom_reminders": [
    "Check code coverage",
    "Update CHANGELOG.md",
    "Review security best practices",
    "Verify API documentation is up to date"
  ]
}
EOF
    
    echo "✓ Custom reminders configured for this project"
}

# Ask user what to configure
echo ""
echo "Choose configuration option:"
echo "1. Enable Dart integration"
echo "2. Disable Dart (non-Dart project)"
echo "3. Custom reminders only"
echo "4. Exit without changes"
echo ""

read -p "Enter option (1-4): " option

case $option in
    1)
        setup_dart_project
        ;;
    2)
        disable_dart_project
        ;;
    3)
        custom_reminders_only
        ;;
    4)
        echo "No changes made."
        exit 0
        ;;
    *)
        echo "Invalid option. No changes made."
        exit 1
        ;;
esac

# Add .claude config files to .gitignore if not already there
if [ -f .gitignore ]; then
    if ! grep -q "^.claude/dart-config.json" .gitignore; then
        echo "" >> .gitignore
        echo "# Claude hook configuration (project-specific)" >> .gitignore
        echo ".claude/dart-config.json" >> .gitignore
        echo ".claude/session-summary.json" >> .gitignore
        echo ".claude/sync-config.json" >> .gitignore
        echo ".claude/pending-dart-syncs.json" >> .gitignore
        echo "" >> .gitignore
        echo "✓ Added Claude config files to .gitignore"
    fi
fi

echo ""
echo "Configuration complete! The hooks will now use project-specific settings."
echo "Files created in .claude/ directory."