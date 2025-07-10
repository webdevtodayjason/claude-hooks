#!/bin/bash

# NPM Publish Script for Claude Hooks Manager
# Version 3.1.1

echo "🚀 Publishing Claude Hooks Manager v3.1.1"
echo "========================================"
echo

# Check if logged into npm
echo "Checking npm login status..."
npm whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "❌ Not logged into npm. Please run 'npm login' first."
    exit 1
fi

echo "✅ Logged in as: $(npm whoami)"
echo

# Run tests
echo "Running tests..."
npm test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please fix tests before publishing."
    exit 1
fi
echo "✅ Tests passed"
echo

# Check git status
echo "Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "It's recommended to commit all changes before publishing."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Confirm version
echo "Current version in package.json: $(node -p "require('./package.json').version")"
read -p "Is this the correct version? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please update the version in package.json"
    exit 1
fi

# Dry run first
echo "Running npm publish --dry-run..."
npm publish --dry-run

echo
read -p "Everything looks good? Publish to npm? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Publishing cancelled."
    exit 1
fi

# Publish to npm
echo "Publishing to npm..."
npm publish

if [ $? -eq 0 ]; then
    echo
    echo "✅ Successfully published claude-hooks-manager@3.1.1"
    echo
    echo "Next steps:"
    echo "1. Create a git tag: git tag v3.1.1"
    echo "2. Push the tag: git push origin v3.1.1"
    echo "3. Create a GitHub release with RELEASE_NOTES_3.1.1.md"
    echo
    echo "📦 View on npm: https://www.npmjs.com/package/claude-hooks-manager"
else
    echo "❌ Publishing failed. Please check the error above."
    exit 1
fi