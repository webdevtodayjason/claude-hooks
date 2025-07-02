#!/bin/bash

# Claude Code Hooks Installation Script

echo "Installing Claude Code Hooks..."

# Create hooks directory if it doesn't exist
mkdir -p ~/.claude/hooks

# Copy all Python hook files
echo "Copying hook files..."
cp *.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.py

# Copy documentation
cp README.md ~/.claude/hooks/

# Check if settings.json exists
if [ -f ~/.claude/settings.json ]; then
    echo ""
    echo "⚠️  Warning: ~/.claude/settings.json already exists"
    echo "Please manually merge the hooks configuration from settings.example.json"
    echo ""
    echo "You can view the example configuration with:"
    echo "cat settings.example.json"
else
    # Copy settings.json
    echo "Creating settings.json..."
    cp settings.example.json ~/.claude/settings.json
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Hooks installed to: ~/.claude/hooks/"
echo ""
echo "Next steps:"
echo "1. Restart Claude Code for the hooks to take effect"
echo "2. Review ~/.claude/settings.json to ensure hooks are configured"
echo "3. Customize hooks as needed for your workflow"
echo ""
echo "For more information, see: ~/.claude/hooks/README.md"