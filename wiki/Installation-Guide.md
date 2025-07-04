# Installation Guide

This guide will walk you through installing Claude Hooks Manager on your system.

## Prerequisites

Before installing Claude Hooks Manager, ensure you have:

- **Node.js** (version 14 or higher)
- **npm** or **yarn** package manager
- **Git** (version 2.9 or higher)

### Checking Prerequisites

```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Check Git version
git --version
```

## Installation Methods

### Method 1: Global Installation (Recommended)

Install Claude Hooks Manager globally to use it across all your projects:

```bash
npm install -g claude-hooks-manager
```

Or with yarn:

```bash
yarn global add claude-hooks-manager
```

### Method 2: Local Installation

For project-specific installation:

```bash
npm install --save-dev claude-hooks-manager
```

Or with yarn:

```bash
yarn add --dev claude-hooks-manager
```

### Method 3: Install from Source

Clone and install from the repository:

```bash
# Clone the repository
git clone https://github.com/your-repo/claude-hooks-manager.git
cd claude-hooks-manager

# Install dependencies
npm install

# Link globally
npm link
```

## Verifying Installation

After installation, verify that Claude Hooks Manager is properly installed:

```bash
claude-hooks --version
```

You should see the version number displayed.

## Post-Installation Setup

### 1. Initialize in Your Project

Navigate to your project directory and initialize:

```bash
cd your-project
claude-hooks init
```

### 2. Install Default Hooks

Install the recommended default hooks:

```bash
claude-hooks install --defaults
```

### 3. Verify Installation

Check the status of installed hooks:

```bash
claude-hooks status
```

## Platform-Specific Notes

### macOS

No additional setup required. If you encounter permission issues:

```bash
sudo npm install -g claude-hooks-manager
```

### Windows

1. Run the installation in an Administrator command prompt
2. If using Git Bash, ensure it's in your PATH
3. You may need to enable script execution:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Linux

If you encounter permission issues:

```bash
sudo npm install -g claude-hooks-manager
```

Or configure npm to install global packages without sudo:

```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## Troubleshooting Installation

### Common Issues

1. **"command not found" after global installation**
   - Ensure npm's global bin directory is in your PATH
   - Run `npm config get prefix` to find the installation location

2. **Permission denied errors**
   - Use sudo (not recommended) or configure npm properly
   - See platform-specific notes above

3. **Node version too old**
   - Update Node.js to version 14 or higher
   - Use a version manager like nvm or n

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](Troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/your-repo/claude-hooks-manager/issues)
3. Create a new issue with your error details

## Next Steps

Now that you have Claude Hooks Manager installed:

- Read the [Getting Started Guide](Getting-Started.md)
- Explore available [Hooks Reference](Hooks-Reference.md)
- Learn about [Configuration](Configuration-Guide.md)

---

[← Back to Home](Home.md) | [Getting Started →](Getting-Started.md)