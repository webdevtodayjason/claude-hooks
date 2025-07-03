# Changelog

All notable changes to Claude Code Hooks will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-03

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

## [1.0.0] - 2024-12-15

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