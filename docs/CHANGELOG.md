# Changelog

All notable changes to Claude Code Hooks will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.1] - 2025-07-03

### 🎨 UI Enhancements

### Added
- Visual status indicators in `list` command showing enabled/disabled/not installed hooks
  - 🟢 Green dot for enabled hooks
  - 🔴 Red dot for disabled hooks  
  - ⚪ Gray circle for not installed hooks
- Enhanced `status` command with detailed hook counts by state
- Status indicators in interactive menu selections

### Improved
- Better visual feedback for hook management
- Clearer understanding of which hooks are active

## [2.2.0] - 2025-07-03

### 🛠️ Complete Hook Management Suite

This release adds comprehensive hook management capabilities to the CLI.

### Added

#### 🎯 Hook Management Commands
- **Enable/Disable** - `claude-hooks enable/disable <hook>` toggles hooks on/off
- **Create** - `claude-hooks create <name>` generates new custom hooks with templates
- **Edit** - `claude-hooks edit <hook>` opens hooks in your preferred editor
- **Remove** - `claude-hooks remove <hook>` permanently deletes hooks
- **Config** - `claude-hooks config` edits Claude Code settings.json

#### 🎨 Enhanced Interactive Menu
- Added "Hook Management" section with all new commands
- Added "Configuration" section for settings and project setup
- Better organization with separators

### Changed
- Enable/disable commands now fully functional (no longer "coming soon")
- Interactive menu now includes all management options
- Better error handling for all commands

## [2.1.0] - 2025-07-03

### 🎨 Enhanced CLI Experience

This release transforms the CLI into a powerful, interactive tool with beautiful UI and helpful diagnostics.

### Added

#### 🆕 Interactive Features
- **Interactive Menu** - Run `claude-hooks` without arguments to launch a beautiful menu
- **Status Command** - `claude-hooks status` checks installation and configuration
- **Doctor Command** - `claude-hooks doctor` runs diagnostics and suggests fixes
- **Init Command** - `claude-hooks init` helps set up project-specific hooks

#### 🎨 UI Enhancements
- Colored output with chalk for better readability
- Loading spinners with ora for long operations
- Interactive prompts with inquirer for user input
- Emojis and icons for visual feedback

#### 📚 Documentation
- Expanded CLI usage documentation
- Interactive menu examples
- npm badges for version and downloads

### Changed
- Enhanced error messages with helpful suggestions
- Improved command help with examples
- Better formatting for list and info commands

### Dependencies
- chalk ^4.1.2 - Terminal string styling
- inquirer ^8.2.6 - Interactive command line prompts
- ora ^5.4.1 - Elegant terminal spinners

## [2.0.0] - 2025-07-03

### 🎉 Major Release - Comprehensive Hook Collection

This release introduces a complete set of 16 production-ready hooks for Claude Code, designed to enforce coding standards, maintain consistency, and automate workflow tasks.

### Added

#### 🆕 New Advanced Hooks
- **api-docs-enforcer.py** - Ensures API documentation completeness with Swagger/OpenAPI
- **no-mock-code.py** - Prevents placeholder/mock code in production
- **secret-scanner.py** - Detects and blocks secrets from being committed
- **env-sync-validator.py** - Keeps .env and .env.example synchronized
- **gitignore-enforcer.py** - Ensures proper .gitignore configuration
- **readme-update-validator.py** - Reminds to update docs when features change

#### 🧪 Testing Infrastructure
- Comprehensive test suite (`test_hooks.py`)
- Simple test runner (`run_tests.sh`)
- npm test support via `package.json`
- All hooks have automated tests

#### 📚 Documentation
- Enhanced README with badges and status indicators
- Detailed accordion sections for each hook
- User-friendly explanations in plain English
- Practical examples for every hook
- Professional banner images

### Changed
- Made `validate-dart-task.py` generic and customizable
- Made `sync-docs-to-dart.py` project-agnostic
- Improved error messages across all hooks
- Enhanced hook output formatting

### Fixed
- Removed project-specific references
- Fixed missing imports in various hooks
- Improved hook reliability and error handling

### Security
- Added comprehensive secret scanning
- Enforced .gitignore best practices
- API security validation for internal endpoints

## [1.0.0] - 2025-07-1

### Added
- Initial set of 10 core hooks:
  - pre-commit-validator.py
  - validate-git-commit.py
  - database-extension-check.py
  - duplicate-detector.py
  - style-consistency.py
  - api-endpoint-verifier.py
  - validate-dart-task.py
  - sync-docs-to-dart.py
  - log-commands.py
  - mcp-tool-enforcer.py
  - session-end-summary.py
- Basic installation script
- Initial documentation
