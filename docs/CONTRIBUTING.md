# Contributing to Claude Code Hooks

Thank you for your interest in contributing to Claude Code Hooks! This project aims to help developers maintain high-quality code through automated hooks.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps to reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed and what you expected
* Include your system details (OS, Python version, Claude Code version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

* Use a clear and descriptive title
* Provide a detailed description of the suggested enhancement
* Provide specific examples to demonstrate how it would work
* Explain why this enhancement would be useful

### Creating New Hooks

We welcome new hook contributions! When creating a new hook:

1. **Follow the Pattern**: Look at existing hooks for the structure
2. **Document Your Hook**: Include a docstring explaining what it does
3. **Add Tests**: Create tests in `test_hooks.py`
4. **Update Documentation**: Add your hook to the README.md

#### Hook Guidelines

* Exit code 0: Success/warning (non-blocking)
* Exit code 2: Error (blocks operation)
* Output messages to stderr
* Be helpful in error messages - explain how to fix issues
* Keep performance in mind - hooks run frequently

### Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-hook`)
3. Make your changes
4. Run tests (`npm test`)
5. Commit your changes using a descriptive commit message
6. Push to your branch
7. Open a Pull Request

#### Pull Request Guidelines

* Include a clear description of the changes
* Reference any related issues
* Update tests as needed
* Update documentation if you're changing functionality
* Ensure all tests pass

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/your-username/claude-hooks.git
   cd claude-hooks
   ```

2. Install the hooks locally for testing:
   ```bash
   ./install.sh
   ```

3. Run tests:
   ```bash
   npm test
   # or for detailed output
   python3 test_hooks.py
   ```

## Testing Your Hook

1. Create a test case in `test_hooks.py`
2. Test manually with sample input:
   ```bash
   echo '{"tool_name":"Write","tool_input":{"file_path":"test.js","content":"test"}}' | python3 your-hook.py
   ```
3. Ensure it handles edge cases gracefully

## Style Guide

* Use Python 3.6+ compatible code
* Follow PEP 8 style guidelines
* Use descriptive variable names
* Add comments for complex logic
* Keep functions focused and small

## Questions?

Feel free to open an issue for any questions about contributing!