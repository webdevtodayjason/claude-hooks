
# Claude Hooks Manager by Sem

![npm version](https://img.shields.io/npm/v/claude-hooks-manager.svg)
![npm downloads](https://img.shields.io/npm/dm/claude-hooks-manager.svg)
![Version](https://img.shields.io/badge/version-3.1.1-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Hooks](https://img.shields.io/badge/hooks-20-orange.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![Claude](https://img.shields.io/badge/Claude-Compatible-purple.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

![Claude Hooks Manager](img/banner-logo.png)

> **📢 Important Notice for Existing Users**
> 
> This project has been renamed from `claude-code-hooks` to `claude-hooks-manager` to better reflect its purpose as a management tool for Claude hooks.
> 
> **Migration Instructions:**
> ```bash
> # Uninstall old package
> npm uninstall -g claude-code-hooks
> 
> # Install new package
> npm install -g claude-hooks-manager
> ```
> The CLI command `claude-hooks` remains unchanged.

A comprehensive hook management system for [Claude](https://claude.ai) that enforces coding standards, maintains consistency, and automates workflow tasks across all projects.

## 🚀 Game-Changing Feature: Context Forge Integration

### 🌟 Never Lose Context Again During Multi-Hour Development Sessions!

### 🎉 First to Implement Anthropic's New PreCompact Hook!

We're excited to announce our groundbreaking integration with **[Context Forge](https://github.com/webdevtodayjason/context-forge)** - the industry-leading CLI tool for AI-ready project scaffolding. This integration is **the first implementation of Anthropic's brand new PreCompact hook**, announced in Claude Code v1.0.48, solving one of the biggest challenges in AI-assisted development: **context loss during conversation compaction**.

#### Why This is Revolutionary

**Anthropic's PreCompact hook** is a game-changing new feature that allows developers to:
- 🔍 **Intercept compaction events** before they happen
- 💾 **Preserve critical context** during the compaction process
- 🔄 **Automatically restore state** after compaction completes
- 🚀 **Enable truly continuous workflows** for the first time

We're among the **first to leverage this powerful new capability** from Anthropic, creating an integration that transforms how developers work with AI assistants.

#### What is Context Forge?

[Context Forge](https://github.com/webdevtodayjason/context-forge) is a powerful CLI tool that implements Andre Karpathy's context engineering principles to generate comprehensive documentation structures. It creates AI-optimized project scaffolds with:

- **CLAUDE.md** - Main context file with project rules and conventions
- **Docs/** - Structured implementation plans and documentation
- **PRPs/** - Product Requirement Prompts for detailed specifications
- **Validation Systems** - Built-in quality gates and checks

Install Context Forge:
```bash
npm install -g context-forge
```

Quick start a new project:
```bash
context-forge init
```

#### The Problem We Solve

During extended coding sessions, Claude Code's context window fills up and performs "compaction" to continue. This causes:
- 😰 Loss of project-specific rules and conventions
- 🔄 Forgotten implementation stages and progress
- 📋 Lost track of PRP guidelines and specifications
- 🐛 Forgotten bug tracking and known issues

#### The Solution: Automatic Context Recovery

Our Context Forge hooks provide **automatic context recovery** after compaction using Anthropic's latest hook capabilities:

1. **PreCompact Hook** (New in Claude Code v1.0.48) - Intercepts compaction before it happens
2. **Smart Detection** - Automatically identifies projects with CLAUDE.md, Docs/, and PRPs/
3. **Context Restoration** - Forces Claude to re-read critical project files after compaction
4. **Progress Tracking** - Maintains awareness of current implementation stage

> **Technical Note**: The PreCompact hook is a brand new feature from Anthropic that was just released. It's the missing piece that finally makes multi-hour AI development sessions practical. By intercepting the compaction event *before* it happens, we can prepare instructions that ensure context is restored immediately after.

#### Benefits for Developers

- ✅ **Multi-Hour Workflows** - Work on complex projects for 8+ hours without context loss
- ✅ **Consistent Quality** - Maintain project standards throughout entire sessions
- ✅ **Zero Manual Intervention** - Automatic context refresh, no reminders needed
- ✅ **PRP Compliance** - Continuous adherence to Product Requirement Prompts
- ✅ **Stage Awareness** - Always knows which implementation phase you're in

#### Setup Context Forge Integration

```bash
# Install Context Forge hooks
cd hooks/context-forge
./install-context-forge-hooks.sh

# Or manually add to ~/.claude/settings.json
```

[Learn more about Context Forge integration →](hooks/context-forge/README.md)

### 🎯 The Perfect AI Development Workflow

Combine Context Forge and Claude Hooks Manager for the ultimate AI-assisted development experience:

1. **Start with Context Forge**
   ```bash
   npm install -g context-forge
   context-forge init
   ```
   - Creates AI-optimized project structure
   - Generates CLAUDE.md with project rules
   - Sets up implementation stages and PRPs

2. **Install Claude Hooks Manager**
   ```bash
   npm install -g claude-hooks-manager
   claude-hooks install
   ```
   - Enforces coding standards
   - Maintains consistency
   - Automates workflows

3. **Enable Context Forge Integration**
   ```bash
   cd hooks/context-forge
   ./install-context-forge-hooks.sh
   ```
   - Enables multi-hour workflows
   - Automatic context recovery
   - Maintains project awareness

4. **Develop with Confidence**
   - Work for 8+ hours without context loss
   - Automatic quality enforcement
   - Consistent code standards
   - PRP compliance throughout

This powerful combination transforms AI-assisted development from a novelty into a production-ready workflow that maintains quality and consistency across extended development sessions.

## 📚 Documentation

### 🛠️ Guides
- **[Context Forge Integration Guide](hooks/context-forge/README.md)** - Enable multi-hour workflows with automatic context recovery
- **[Developing Custom Hooks](docs/developing-custom-hooks.md)** - Create your own hooks with examples and best practices
- [Project-Aware Hooks](docs/project-aware-hooks.md) - Configure hooks for multi-project environments

### 📖 Official Claude Resources
- [Claude Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Claude Setup Guide](https://docs.anthropic.com/en/docs/claude-code/setup)
- [Model Context Protocol (MCP)](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [Claude SDK](https://docs.anthropic.com/en/docs/claude-code/sdk)

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

### 🆕 New Advanced Hooks
- **No mock code** - Prevents placeholder data (Lorem ipsum, test users, static returns)
- **Secret scanner** - Detects API keys, passwords, tokens before they're committed
- **Environment sync** - Keeps .env and .env.example synchronized
- **Gitignore enforcer** - Prevents committing sensitive files and test scripts
- **README validator** - Reminds to update documentation when features change
- **Timestamp validator** - Ensures accurate dates in documentation and changelogs

## Installation

### Install from npm

```bash
# Install the package globally
npm install -g claude-hooks-manager

# Run the installation script to copy hooks to Claude directory
claude-hooks-install
```

### Install from Source

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
   cp hooks/*.py ~/.claude/hooks/
   chmod +x ~/.claude/hooks/*.py
   ```

3. Update your Claude settings:
   - If `~/.claude/settings.json` exists, merge the hooks configuration from `settings.example.json`
   - If not, copy `settings.example.json` to `~/.claude/settings.json`

4. Restart Claude for the hooks to take effect

## CLI Usage

When installed via npm, you get access to the powerful `claude-hooks` CLI:

### Available Commands

```bash
# Launch interactive menu (NEW!)
claude-hooks

# Install hooks to Claude directory
claude-hooks install
claude-hooks-install  # Also available as separate command

# List all available hooks with descriptions
claude-hooks list

# Get detailed information about a specific hook
claude-hooks info <hook-name>
# Example: claude-hooks info secret-scanner

# Check installation status (NEW!)
claude-hooks status

# Run diagnostics to check setup (NEW!)
claude-hooks doctor

# Initialize hooks for current project (NEW!)
claude-hooks init

# Hook Management Commands (NEW!)
claude-hooks enable <hook-name>    # Enable a disabled hook
claude-hooks disable <hook-name>   # Disable a hook temporarily
claude-hooks create <hook-name>    # Create a new custom hook
claude-hooks edit <hook-name>      # Edit an existing hook
claude-hooks remove <hook-name>    # Remove a hook permanently
claude-hooks config                # Edit Claude Code settings

# Run the comprehensive test suite
claude-hooks test

# Show version information
claude-hooks --version

# Display help and usage information
claude-hooks --help

# Dart Integration Commands (NEW!)
claude-hooks dart init     # Initialize Dart workspace configuration
claude-hooks dart edit     # Edit existing .dart configuration
```

### Interactive Menu (NEW!)

Running `claude-hooks` without any arguments launches an interactive menu:

```bash
$ claude-hooks

🪝 Claude Hooks Manager Interactive Menu

? What would you like to do? (Use arrow keys)
❯ 📦 Install hooks to Claude
  📋 List all available hooks
  🔍 Get info about a specific hook
  ✅ Check installation status
  🧪 Run tests
  🩺 Run diagnostics (doctor)
  🚀 Initialize project hooks
  ──────────────
  ❌ Exit
```

### Examples

```bash
# See what hooks are available
$ claude-hooks list
Available Claude Hooks:

  pre-commit-validator.py        Enforces coding standards before commits
  validate-git-commit.py         Validates commit message format
  secret-scanner.py              Detects and blocks secrets
  no-mock-code.py               Prevents placeholder/mock code
  ... and more

# Check if everything is set up correctly
$ claude-hooks doctor

🩺 Running Claude Hooks Manager Diagnostics...

✅ No issues found! Everything looks good.

# Check installation status
$ claude-hooks status

🔍 Checking Claude Hooks Manager Status...

✅ Hooks directory exists
   17 hooks installed
✅ Settings file exists

# Get details about a specific hook
$ claude-hooks info secret-scanner
Hook: secret-scanner.py
Description: Detects and blocks secrets
Event: before_tool_call
Tools: Write, MultiEdit, Edit

# Run tests to ensure hooks are working
$ claude-hooks test
Running Claude Hooks Manager Tests...
==================================
✅ All hooks are executable
✅ All 17 hooks passed tests!
```

## 🎯 Dart Integration

Claude Hooks Manager now includes seamless integration with Dart MCP for project management. This feature enables automatic task tracking and documentation synchronization.

### What is Dart Integration?

Dart integration allows Claude to:
- Automatically suggest creating tasks in your Dart workspace
- Sync documentation between your local project and Dart
- Validate task creation with project-specific rules
- Generate CLAUDE.md files with workspace configuration

### Setting Up Dart Integration

#### Method 1: During Project Init
```bash
claude-hooks init
# When prompted, choose to set up Dart integration
```

#### Method 2: Direct Dart Setup
```bash
claude-hooks dart init
```

This will:
1. Create a `.dart` configuration file in your project root
2. Configure your Dart workspace, tasks folder, and docs folder
3. Optionally create a CLAUDE.md file with project instructions

### The .dart Configuration File

The `.dart` file stores your project's Dart workspace configuration:

```json
{
  "workspace": "MCP Forge",
  "tasksFolder": "MCP Forge/Tasks",
  "docsFolder": "MCP Forge/Docs",
  "syncEnabled": true,
  "syncRules": {
    "include": ["README.md", "docs/**/*.md", "wiki/**/*.md"],
    "exclude": [".github/**/*.md", "node_modules/**/*.md", "test/**/*.md"]
  }
}
```

### CLAUDE.md - Project Instructions

The `claude-hooks dart init` command can also generate a CLAUDE.md file that provides Claude with:
- Project-specific instructions
- Dart workspace configuration
- Task management rules
- Git workflow guidelines
- Development best practices

### Disabling Dart Features

If you're not using Dart, you can:

1. **Skip during setup**: Choose "No" when asked about Dart integration
2. **Disable sync**: Set `"syncEnabled": false` in your `.dart` file
3. **Remove configuration**: Delete the `.dart` file from your project
4. **Disable hooks**: Run `claude-hooks disable sync-docs-to-dart` and `claude-hooks disable validate-dart-task`

### How It Works

1. **sync-docs-to-dart hook**: 
   - Triggers when you create/edit markdown files
   - Checks for `.dart` configuration
   - If no config exists, prompts you to run `claude-hooks dart init`
   - If configured, suggests syncing to your Dart docs folder

2. **validate-dart-task hook**:
   - Triggers when creating Dart tasks
   - Suggests using your project's configured dartboard
   - Validates task priorities and statuses

### Customizing CLAUDE.md

See [CLAUDE.md.template](./CLAUDE.md.template) for a complete guide on customizing your project instructions. The template includes:
- Variable references
- Common customizations
- Best practices
- Example configurations

## Hooks Overview

| Hook | Trigger | Purpose |
|------|---------|---------|
| **Context Forge Hooks** | | |
| `precompact-context-refresh.py` | Before compaction | Detects Context Forge projects and prepares context recovery |
| `stop-context-refresh.py` | After compaction | Enforces re-reading of CLAUDE.md, PRPs, and Implementation.md |
| **Standard Hooks** | | |
| `pre-commit-validator.py` | Before git commit/push | Runs tests, linting, TypeScript checks |
| `validate-git-commit.py` | Before git commit | Enforces commit message standards |
| `database-extension-check.py` | When editing schemas | Prevents unnecessary table creation |
| `duplicate-detector.py` | When creating files | Prevents duplicate code/routes |
| `style-consistency.py` | When editing TSX/CSS | Enforces theme-aware styling |
| `api-endpoint-verifier.py` | When editing API routes | Validates endpoint configuration |
| `api-docs-enforcer.py` | Before commits & API edits | Enforces Swagger docs, Postman collections, API security |
| `no-mock-code.py` | Before commits & file edits | Prevents placeholder/mock code in production |
| `secret-scanner.py` | Before commits & file edits | Detects and prevents committing secrets |
| `env-sync-validator.py` | When editing .env files | Keeps .env and .env.example in sync |
| `gitignore-enforcer.py` | Before git add/commit | Ensures .gitignore exists and blocks forbidden files |
| `readme-update-validator.py` | Before commits | Reminds to update README when features change |
| `validate-dart-task.py` | Creating Dart tasks | Ensures proper task hierarchy |
| `sync-docs-to-dart.py` | After creating .md files | Reminds to sync docs |
| `log-commands.py` | Before bash commands | Logs all commands |
| `mcp-tool-enforcer.py` | Various operations | Suggests MCP tool usage |
| `session-end-summary.py` | Session end | Provides reminders |

## 📋 Detailed Hook Documentation

Click on any hook below to see detailed information about what it does and how it helps your development workflow.

<details>
<summary><strong>🚀 precompact-context-refresh.py</strong> - First Implementation of Anthropic's PreCompact Hook</summary>

### What it does:
This groundbreaking hook is the **first implementation of Anthropic's new PreCompact hook event** (released in Claude Code v1.0.48), enabling multi-hour AI development sessions:
- 🎯 **Uses Anthropic's PreCompact event** to intercept before compaction occurs
- 🔍 Detects Context Forge projects (CLAUDE.md, Docs/, PRPs/)
- 📊 Tracks current implementation stage from transcript
- 💾 Creates marker for post-compaction recovery
- 📝 Prepares detailed refresh instructions

### Why it's revolutionary:
Before Anthropic released the PreCompact hook, there was no way to prepare for compaction events. Now, for the first time, we can:
- **Intercept compaction before it happens** (impossible before v1.0.48)
- **Preserve critical state information** during the compaction process
- **Ensure immediate context recovery** after compaction completes

This is a game-changer for AI-assisted development, finally making 8+ hour coding sessions practical and productive.

### Technical implementation:
```python
# This hook receives the new PreCompact event from Claude Code
# Event data includes: session_id, transcript_path, trigger, custom_instructions
def main():
    input_data = json.load(sys.stdin)  # PreCompact event from Anthropic
    # ... detect Context Forge project and prepare recovery
```
</details>

<details>
<summary><strong>🔄 stop-context-refresh.py</strong> - Automatic Context Restoration</summary>

### What it does:
Works in tandem with the PreCompact hook to restore context after compaction:
- ✅ Detects when compaction has occurred
- 📚 Forces Claude to re-read all critical project files
- 🎯 Maintains awareness of current implementation stage
- 💡 Provides specific instructions based on project structure

### Why it's helpful:
Eliminates the frustrating need to manually remind Claude about your project after each compaction. Your workflow continues seamlessly, maintaining quality and consistency throughout extended development sessions.

### Integration with Context Forge:
This hook specifically looks for Context Forge project structures and customizes the refresh instructions based on what files exist in your project, ensuring maximum context recovery with minimum overhead.
</details>

<details>
<summary><strong>🔍 pre-commit-validator.py</strong> - Your Safety Net Before Commits</summary>

### What it does:
This hook acts as your personal quality assurance assistant. Before any code gets committed, it automatically:
- ✅ Runs your test suite to catch broken functionality
- ✅ Executes linting tools to ensure code style consistency
- ✅ Performs TypeScript type checking to prevent type errors
- ✅ Validates that your code meets project standards

### Why it's helpful:
Imagine pushing code only to find out later that tests are failing or there are linting errors. This hook prevents that embarrassment by catching issues before they reach the repository. It's like having a careful reviewer check your work every time.

### Example output:
```
🔍 Running pre-commit validation...
✅ Tests passed (42 tests, 0 failures)
✅ Linting passed (0 errors, 0 warnings)
✅ TypeScript check passed
✨ All checks passed! Ready to commit.
```
</details>

<details>
<summary><strong>✏️ validate-git-commit.py</strong> - Commit Message Police</summary>

### What it does:
This hook ensures all commit messages follow a consistent format:
- 📏 Enforces minimum message length (10+ characters)
- 🔤 Requires capitalized first letter
- 🚫 Blocks co-authored commits (no auto-generated attributions)
- 📝 Ensures conventional commit format when configured

### Why it's helpful:
Good commit messages make project history readable and searchable. This hook ensures everyone on the team writes clear, consistent commit messages that explain what changed and why.

### Example:
```
❌ Bad: "fix bug"
✅ Good: "Fix navigation menu overflow on mobile devices"
```
</details>

<details>
<summary><strong>🗄️ database-extension-check.py</strong> - Database Schema Guardian</summary>

### What it does:
Prevents developers from creating unnecessary new database tables when they could extend existing ones:
- 🔍 Detects when you're creating new migration files
- 💡 Suggests existing tables that might be extended instead
- 📊 Encourages proper database normalization
- 🚫 Blocks creation of duplicate or redundant tables

### Why it's helpful:
Keeps your database clean and maintainable by preventing table sprawl. Instead of having users, user_profiles, user_settings, and user_preferences as separate tables, it encourages you to use a single users table with appropriate columns.

### Example:
```
⚠️  Creating new table 'user_settings'
💡 Consider extending the existing 'users' table instead
   You could add a 'settings' JSON column or related fields
```
</details>

<details>
<summary><strong>🔁 duplicate-detector.py</strong> - Code Duplication Police</summary>

### What it does:
Scans your codebase to prevent creating duplicate:
- 🛣️ API routes (e.g., two `/api/users` endpoints)
- 🧩 React/Vue components with the same name
- 📦 Utility functions that already exist
- 📄 Similar file names that might cause confusion

### Why it's helpful:
Duplication leads to maintenance nightmares. This hook helps maintain the DRY (Don't Repeat Yourself) principle by alerting you when similar code already exists.

### Example:
```
❌ Duplicate detected!
   You're creating: components/UserCard.tsx
   Already exists: components/user/UserCard.tsx
💡 Consider using the existing component or choosing a different name
```
</details>

<details>
<summary><strong>🎨 style-consistency.py</strong> - Style & Theme Enforcer</summary>

### What it does:
Ensures consistent styling across your application:
- 🌓 Enforces dark mode support (checks for dark: variants)
- 🎨 Prevents hardcoded colors (use theme variables instead)
- 🧩 Suggests ShadCN UI components over raw HTML elements
- 📏 Validates spacing uses consistent scale (2, 4, 6, 8, etc.)

### Why it's helpful:
Maintains a professional, consistent look across your entire application. No more random colors or inconsistent spacing that makes your app look unprofessional.

### Example:
```
⚠️  Style issues found:
   Line 23: Missing dark mode variant for bg-blue-500
   Line 45: Use ShadCN Button component instead of <button>
   Line 67: Hardcoded color #3B82F6 - use theme variables
```
</details>

<details>
<summary><strong>🌐 api-endpoint-verifier.py</strong> - API Standards Enforcer</summary>

### What it does:
Validates that all API endpoints follow best practices:
- 🔐 Ensures authentication is implemented
- 📝 Checks for proper input validation
- 🏷️ Enforces consistent naming conventions
- ⚡ Validates error handling is in place

### Why it's helpful:
Prevents security vulnerabilities and ensures a consistent API experience for consumers. No more endpoints that work differently or have security holes.

### Example:
```
❌ API endpoint issues:
   /api/getUser - Should use REST convention: GET /api/users/:id
   Missing authentication check
   No input validation for user ID
```
</details>

<details>
<summary><strong>📚 api-docs-enforcer.py</strong> - API Documentation Guardian</summary>

### What it does:
Ensures every API endpoint is properly documented:
- 📋 Requires Swagger/OpenAPI documentation for all endpoints
- 📮 Enforces Postman collection updates
- 🔐 Validates security documentation for internal APIs
- 🔗 Ensures documentation links between Swagger and Postman

### Why it's helpful:
Good API documentation is crucial for team collaboration and API consumers. This hook ensures no endpoint goes undocumented, making your API easy to understand and use.

### Example:
```
❌ API Documentation Required:
   New endpoint: POST /api/users/bulk-import
   Missing from swagger.json
   No Postman collection entry
   
💡 Run 'npm run generate-api-docs' to auto-generate documentation
```
</details>

<details>
<summary><strong>🚫 no-mock-code.py</strong> - Real Code Enforcer</summary>

### What it does:
Prevents placeholder or mock code from entering production:
- 📝 Detects Lorem ipsum text
- 👤 Flags test users (John Doe, test@example.com)
- 🔄 Identifies functions that always return the same value
- 📌 Catches TODO comments without implementation
- 💾 Finds hardcoded test data

### Why it's helpful:
Ensures your production code uses real, dynamic data. No more embarrassing moments where "John Doe" appears in production or where a function always returns the same test data.

### Example:
```
❌ Mock/Placeholder Code Detected!
   Line 45: Found "Lorem ipsum" - Replace with real content
   Line 67: Static user data - Implement database query
   Line 89: TODO without implementation - Complete the function
```
</details>

<details>
<summary><strong>🔒 secret-scanner.py</strong> - Security Guardian</summary>

### What it does:
Scans code for accidentally exposed secrets:
- 🔑 Detects API keys and tokens
- 🔐 Finds passwords and credentials
- 📧 Identifies private keys and certificates
- 🚨 Checks .gitignore includes sensitive files

### Why it's helpful:
Prevents the #1 security mistake: committing secrets to version control. Once a secret is in Git history, it's compromised forever. This hook is your last line of defense.

### Example:
```
🚨 CRITICAL: Attempting to commit secrets!
   Line 23: API key detected: sk_test_abc...
   Line 45: Hardcoded password found
   
❌ Commit blocked - remove secrets and use environment variables
```
</details>

<details>
<summary><strong>🔄 env-sync-validator.py</strong> - Environment Config Keeper</summary>

### What it does:
Keeps your environment configuration files synchronized:
- 📋 Ensures .env.example is updated when .env changes
- 💡 Suggests safe placeholder values for examples
- 🚫 Prevents real secrets in .env.example
- 📝 Validates all team members know required variables

### Why it's helpful:
When team members pull your code, they need to know what environment variables to set. This hook ensures .env.example always reflects the current requirements.

### Example:
```
❌ Environment sync issues:
   New variable DATABASE_URL in .env
   Missing from .env.example
   
💡 Add to .env.example:
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```
</details>

<details>
<summary><strong>🚮 gitignore-enforcer.py</strong> - Repository Cleanliness Guard</summary>

### What it does:
Ensures .gitignore is properly configured:
- 📁 Verifies .gitignore exists
- 🚫 Blocks commits of sensitive files (.env, *.key, *.pem)
- 🧪 Prevents test scripts and temporary files
- 💾 Stops large files and backups from being committed

### Why it's helpful:
Keeps your repository clean and secure. Prevents accidentally committing files that should never be in version control, like private keys, large binaries, or temporary files.

### Example:
```
🚨 FORBIDDEN FILES detected:
   • .env (environment file)
   • private-key.pem (private key)
   • test-script.sh (test script)
   
💡 Add these patterns to .gitignore:
   .env
   *.pem
   *test-script*
```
</details>

<details>
<summary><strong>📝 readme-update-validator.py</strong> - Documentation Reminder</summary>

### What it does:
Reminds you to update documentation when code changes:
- 🆕 Detects new features and APIs
- 📚 Suggests README sections to update
- 🔧 Identifies configuration changes
- 📦 Notices new dependencies

### Why it's helpful:
Documentation often becomes outdated because developers forget to update it. This hook provides gentle reminders to keep your README current with your code.

### Example:
```
📚 README Update Reminder:
   
🆕 New files detected:
   • api/users/bulk-import.js (API endpoint)
   • components/UserBulkUpload.tsx (Component)
   
💡 Consider updating these README sections:
   • API Documentation
   • Features
   • Usage Examples
```
</details>

<details>
<summary><strong>✅ validate-dart-task.py</strong> - Task Hierarchy Enforcer</summary>

### What it does:
Ensures proper task management in Dart:
- 📊 Requires all tasks have a Phase parent
- 🏷️ Validates task categorization
- 🔗 Maintains project hierarchy
- 📝 Enforces task metadata

### Why it's helpful:
Keeps project management organized by ensuring all tasks are properly categorized and tracked within the correct project phase.
</details>

<details>
<summary><strong>📄 sync-docs-to-dart.py</strong> - Documentation Sync Reminder</summary>

### What it does:
Tracks when markdown files are created and reminds to sync with Dart:
- 📝 Detects new .md file creation
- 🔄 Tracks pending syncs
- 📊 Maintains documentation consistency
- 💾 Stores sync status

### Why it's helpful:
Ensures documentation stays synchronized across different systems, preventing information silos.
</details>

<details>
<summary><strong>📊 log-commands.py</strong> - Command Historian</summary>

### What it does:
Logs all bash commands for audit and learning:
- 🕒 Timestamps every command
- 📁 Organizes logs by date
- 📈 Tracks command frequency
- 🔍 Enables command history search

### Why it's helpful:
Creates an audit trail of all commands run, useful for debugging, learning patterns, and security auditing.
</details>

<details>
<summary><strong>🛠️ mcp-tool-enforcer.py</strong> - Tool Usage Optimizer</summary>

### What it does:
Suggests MCP tools when better alternatives exist:
- 🔄 Detects suboptimal tool usage
- 💡 Recommends MCP alternatives
- ⚡ Improves workflow efficiency
- 🎯 Promotes best practices

### Why it's helpful:
Helps developers use the most efficient tools available, improving productivity and code quality.
</details>

<details>
<summary><strong>👋 session-end-summary.py</strong> - Session Wrap-up Assistant</summary>

### What it does:
Provides helpful reminders at session end:
- 💾 Reminds about uncommitted changes
- 📋 Lists pending tasks
- 🔧 Shows workflow reminders
- ✅ Ensures nothing is forgotten

### Why it's helpful:
Acts like a helpful assistant making sure you don't forget important tasks before ending your coding session.
</details>

<details>
<summary><strong>⏰ timestamp-validator.py</strong> - Date and Time Accuracy</summary>

### What it does:
Validates timestamps and dates in your documentation:
- 📅 Checks dates in CHANGELOG entries
- ⚠️ Warns about future dates or dates from wrong months
- 🕐 Provides current timestamp in multiple formats
- 🔍 Detects hardcoded dates that might be incorrect
- 📝 Validates dates in commits and documentation

### Why it's helpful:
Prevents common date mistakes like using January dates in July, future dates in changelogs, or outdated timestamps. Ensures your documentation always has accurate temporal information.
</details>

## Configuration

### Global Hook Configuration

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

### Project-Specific Configuration

Some hooks now support project-specific configuration to avoid cross-project interference:

#### Session End Summary Hook
Create `.claude/session-summary.json` in your project:
```json
{
  "show_dart_reminders": true,
  "show_git_reminders": true,
  "custom_reminders": [
    "Run tests before committing",
    "Update documentation"
  ]
}
```

#### Documentation Sync Hook
Create `.claude/dart-config.json` in your project:
```json
{
  "enable_doc_sync": true,
  "default_docs_folder": "workspace/Docs",
  "workspace": "your-workspace",
  "dartboard": "workspace/Tasks"
}
```

See [Project-Aware Hooks Documentation](docs/project-aware-hooks.md) for detailed configuration options.

## Customization

### Disable a Hook
Edit `~/.claude/settings.json` and remove or comment out the specific hook entry.

### Add Custom Hooks
See our comprehensive [Developing Custom Hooks Guide](docs/developing-custom-hooks.md) for detailed instructions.

Quick start:
1. Create a Python script in `~/.claude/hooks/`
2. Make it executable: `chmod +x your-hook.py`
3. Add it to the appropriate section in `settings.json`

### Hook Exit Codes
- `0` - Success, continue normally
- `2` - Blocking error, prevents tool execution
- Other - Non-blocking error, shows message but continues

## Best Practices

1. **Performance** - Keep hooks fast to avoid slowing down Claude
2. **Error Handling** - Always handle exceptions gracefully
3. **Clear Messages** - Provide actionable feedback
4. **Non-Blocking** - Use warnings for suggestions, only block on critical issues

## Troubleshooting

### Hooks Not Running
1. Restart Claude after installation
2. Check `~/.claude/settings.json` is valid JSON
3. Verify hook files are executable

### Disabled Hook Errors
If you're seeing "No such file or directory" errors for disabled hooks:

**Problem**: When hooks are disabled using older versions, Claude still tries to execute them, causing errors.

**Solution**: Run the migration script to update disabled hooks to the new format:
```bash
node migrate-disabled-hooks.js
```

This converts disabled hooks to use stub files that exit cleanly, preventing errors while keeping hooks disabled.

**How it works**:
- Instead of renaming hooks to `.disabled`, the new system:
  - Moves the original hook to `.py.original`
  - Creates a stub `.py` file that exits cleanly
  - Claude can still find and execute the hook, but it does nothing

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

Created for the Claude community to enhance productivity and maintain code quality.

## Resources

- **[Developing Custom Hooks Guide](docs/developing-custom-hooks.md)** - Complete tutorial for creating your own hooks
- [Claude Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [MCP Tools](https://docs.anthropic.com/en/docs/claude-code/mcp)

---

<p align="center">Made with ❤️ by Sem</p>

---

<p align="center">
  <img src="img/sem-logo-hooks-150x150.png" alt="Sem Hooks Logo" />
</p>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=webdevtodayjason/claude-hooks&type=Date)](https://star-history.com/#webdevtodayjason/claude-hooks&Date)