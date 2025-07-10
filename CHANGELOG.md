# Changelog

All notable changes to Claude Hooks Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.1] - 2025-07-10

### Added
- 🚀 **Context Forge Integration** - Revolutionary feature for multi-hour AI development workflows
- PreCompact hook (`precompact-context-refresh.py`) - Detects Context Forge projects before compaction
- Stop hook (`stop-context-refresh.py`) - Enforces context restoration after compaction
- Context Forge utilities (`context-forge-utils.py`) - Advanced project analysis and stage detection
- Installation script for easy Context Forge hooks setup
- Comprehensive documentation for Context Forge integration

### Changed
- Updated README with prominent Context Forge integration section
- Added "The Perfect AI Development Workflow" combining both tools
- Increased hook count to 20 (added 2 Context Forge hooks)
- Enhanced hooks overview table with Context Forge section

### Documentation
- Added detailed Context Forge integration guide
- Created test examples and integration documentation
- Added benefits and use cases for multi-hour workflows
- Documented automatic context recovery mechanism

## [3.1.0] - 2025-07-05

### Added
- Interactive CLI menu system
- New commands: `status`, `doctor`, `init`, `enable`, `disable`, `create`, `edit`, `remove`, `config`
- Dart integration commands: `dart init`, `dart edit`
- Project-aware hooks configuration
- Migration script for old disabled hooks format

### Changed
- Improved CLI user experience with interactive prompts
- Enhanced error messages and diagnostics
- Better hook management workflow

### Fixed
- Disabled hooks now use stub files to prevent errors
- Improved hook detection and status reporting

## [3.0.0] - 2025-07-05

### Added
- Dart MCP integration with `.dart` configuration files
- `claude-hooks dart init` command to set up Dart workspace
- `claude-hooks dart edit` command to modify Dart configuration
- CLAUDE.md generation with comprehensive project instructions
- CLAUDE.md.template guide for customization
- Workspace-aware sync-docs-to-dart hook
- Workspace-aware validate-dart-task hook
- Interactive prompts for workspace configuration
- Documentation sync rules (include/exclude patterns)
- Integration with project init workflow

### Changed
- sync-docs-to-dart hook now uses `.dart` configuration instead of guessing
- validate-dart-task hook suggests project-specific dartboard
- Project init now offers Dart integration setup
- Hooks prompt for configuration when .dart file is missing

### Fixed
- Fixed "No such file or directory" errors when hooks are disabled
- Implemented stub file system for disabled hooks to prevent Claude execution errors
- Updated enable/disable mechanism to use `.original` files instead of `.disabled`
- Added migration script for converting old disabled hooks to new format

### Documentation
- Added comprehensive Dart Integration section to README
- Created CLAUDE.md.template with customization guide
- Added examples of .dart configuration
- Documented how to disable Dart features

## [2.9.0] - 2025-07-05

### Added
- Dart MCP integration with `.dart` configuration files
- `claude-hooks dart init` command to set up Dart workspace
- `claude-hooks dart edit` command to modify Dart configuration
- CLAUDE.md generation with comprehensive project instructions
- CLAUDE.md.template guide for customization
- Workspace-aware sync-docs-to-dart hook
- Workspace-aware validate-dart-task hook
- Interactive prompts for workspace configuration
- Documentation sync rules (include/exclude patterns)
- Integration with project init workflow

### Changed
- sync-docs-to-dart hook now uses `.dart` configuration instead of guessing
- validate-dart-task hook suggests project-specific dartboard
- Project init now offers Dart integration setup
- Hooks prompt for configuration when .dart file is missing

### Fixed
- Fixed "No such file or directory" errors when hooks are disabled
- Implemented stub file system for disabled hooks to prevent Claude execution errors
- Updated enable/disable mechanism to use `.original` files instead of `.disabled`
- Added migration script for converting old disabled hooks to new format

### Documentation
- Added comprehensive Dart Integration section to README
- Created CLAUDE.md.template with customization guide
- Added examples of .dart configuration
- Documented how to disable Dart features

## [3.0.0] - 2025-07-04

### Changed
- **BREAKING**: Renamed project from `claude-code-hooks` to `claude-hooks-manager`
- Updated all documentation and branding to reflect new name
- Package name on npm changed to `claude-hooks-manager`

### Added
- Migration guide for users upgrading from `claude-code-hooks`
- Comprehensive GitHub wiki documentation

## [2.2.2] - 2025-07-04

### Added
- New `timestamp-validator` hook to prevent date/time errors in documentation
- Hook validates dates are within reasonable ranges (past year to 1 month future)
- Prevents Claude from using incorrect dates in changelogs and documentation

## [2.2.1] - 2025-07-04

### Added
- Visual status indicators for hooks (green/red/gray dots)
- Color-coded hook status in list view
- Clear indication of enabled, disabled, and not installed hooks

## [2.2.0] - 2025-07-03

### Added
- Complete hook management suite in CLI
- Enable/disable hooks commands
- Edit hook functionality with system editor
- Add new custom hooks interactively
- Remove hooks with confirmation
- Hook creation wizard with templates

## [2.1.0] - 2025-07-03

### Added
- Interactive CLI menu system
- Project initialization command
- System doctor for diagnostics
- Configuration editor
- Status command showing hook statistics

### Changed
- Simplified main CLI interface with menu-driven navigation
- Enhanced user experience with spinners and colors

## [2.0.0] - 2025-07-03

### Added
- 7 new advanced hooks for enhanced development workflow
- Comprehensive test suite with 100% hook coverage
- npm package distribution
- GitHub release automation
- Detailed documentation for each hook

### Fixed
- Removed all cross-project contamination issues
- Fixed duplicate line detection in secret scanner
- Added missing imports in various hooks

### Changed
- Complete rewrite of hook system for better maintainability
- Hooks now store data in project-specific directories
- Enhanced error messages and user feedback