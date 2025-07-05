# Changelog

All notable changes to Claude Hooks Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2025-07-05

### Fixed
- Fixed "No such file or directory" errors when hooks are disabled
- Implemented stub file system for disabled hooks to prevent Claude execution errors
- Updated enable/disable mechanism to use `.original` files instead of `.disabled`
- Added migration script for converting old disabled hooks to new format

### Changed
- Disabled hooks now use stub files that exit cleanly instead of being renamed
- Hook status detection now properly identifies stub files as disabled
- Edit command can now edit disabled hook's original code

### Added
- `migrate-disabled-hooks.js` script to convert old `.disabled` hooks to new format
- Troubleshooting section in README for disabled hook errors

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