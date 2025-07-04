#!/bin/bash

# GitHub Wiki Setup Script for Claude Hooks Manager
# This script helps copy wiki content to GitHub Wiki repository

echo "🚀 GitHub Wiki Setup for Claude Hooks Manager"
echo "============================================"
echo ""

# Check if wiki directory exists
if [ ! -d "wiki" ]; then
    echo "❌ Error: wiki/ directory not found!"
    echo "Please run this script from the root of claude-hooks-repo"
    exit 1
fi

# Get the wiki repo URL
REPO_URL="https://github.com/webdevtodayjason/claude-hooks.wiki.git"
WIKI_DIR="../claude-hooks.wiki"

echo "📋 Prerequisites:"
echo "1. Enable Wiki in your GitHub repository settings"
echo "2. Create at least one page in the wiki (to initialize it)"
echo ""
read -p "Have you completed these steps? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please enable Wiki in your repository settings first:"
    echo "https://github.com/webdevtodayjason/claude-hooks/settings"
    exit 1
fi

# Clone or pull the wiki repository
if [ -d "$WIKI_DIR" ]; then
    echo "📂 Wiki repository already exists, pulling latest changes..."
    cd "$WIKI_DIR"
    git pull
    cd - > /dev/null
else
    echo "📥 Cloning wiki repository..."
    git clone "$REPO_URL" "$WIKI_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to clone wiki repository"
        echo "Make sure you have:"
        echo "1. Enabled Wiki in repository settings"
        echo "2. Created at least one page to initialize the wiki"
        exit 1
    fi
fi

echo ""
echo "📄 Copying wiki pages..."

# Copy all markdown files
cp wiki/*.md "$WIKI_DIR/"

# Create a _Sidebar.md for navigation
cat > "$WIKI_DIR/_Sidebar.md" << 'EOF'
## Claude Hooks Manager

### Getting Started
* [[Home]]
* [[Installation Guide]]
* [[Getting Started]]

### Usage
* [[Hooks Reference]]
* [[Configuration Guide]]
* [[Creating Custom Hooks]]

### Reference
* [[API Reference]]
* [[Troubleshooting]]
* [[FAQ]]

### Community
* [[Contributing]]
* [GitHub Repository](https://github.com/webdevtodayjason/claude-hooks)
* [Report Issues](https://github.com/webdevtodayjason/claude-hooks/issues)
EOF

echo "✅ Created _Sidebar.md for navigation"

# Create a _Footer.md
cat > "$WIKI_DIR/_Footer.md" << 'EOF'
---
Claude Hooks Manager v3.0.0 | [GitHub](https://github.com/webdevtodayjason/claude-hooks) | [npm](https://www.npmjs.com/package/claude-hooks-manager) | [Issues](https://github.com/webdevtodayjason/claude-hooks/issues)
EOF

echo "✅ Created _Footer.md"

# Commit and push
cd "$WIKI_DIR"
git add .
git status

echo ""
echo "📝 Ready to commit and push wiki changes"
read -p "Do you want to commit and push these changes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Add comprehensive wiki documentation

- Home page with project overview
- Installation and Getting Started guides
- Complete hooks reference
- Custom hooks creation guide
- Configuration and troubleshooting
- FAQ and Contributing guidelines
- API reference for developers"
    
    echo ""
    echo "🚀 Pushing to GitHub Wiki..."
    git push
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Wiki successfully updated!"
        echo ""
        echo "🎉 Your wiki is now live at:"
        echo "https://github.com/webdevtodayjason/claude-hooks/wiki"
    else
        echo "❌ Failed to push changes"
        echo "You may need to pull first or resolve conflicts"
    fi
else
    echo "Changes not pushed. You can manually commit and push from $WIKI_DIR"
fi

echo ""
echo "💡 Tips:"
echo "- The wiki includes a sidebar for easy navigation"
echo "- You can edit pages directly on GitHub"
echo "- Consider adding images to make the wiki more visual"
echo "- Link to the wiki from your main README.md"