# Contributing Guide

Thank you for your interest in contributing to Claude Hooks Manager! This guide will help you get started.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please help us fix it:

1. Check if the bug is already reported in [GitHub Issues](https://github.com/your-repo/claude-hooks-manager/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (`claude-hooks info --system`)
   - Relevant logs and configuration

### 2. Suggest Features

Have an idea for improvement?

1. Check existing [feature requests](https://github.com/your-repo/claude-hooks-manager/issues?label=enhancement)
2. Create a new issue with:
   - Use case description
   - Proposed solution
   - Alternative solutions considered
   - Mockups or examples (if applicable)

### 3. Improve Documentation

Documentation improvements are always welcome:

- Fix typos and grammar
- Add examples and clarifications
- Translate documentation
- Create tutorials or blog posts

### 4. Submit Code

Ready to code? Great! Here's how:

## Development Setup

### Prerequisites

- Node.js 14+
- Git
- npm or yarn

### Setup Steps

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/claude-hooks-manager.git
cd claude-hooks-manager
```

3. Install dependencies:
```bash
npm install
```

4. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

5. Set up development environment:
```bash
npm run setup:dev
```

## Development Workflow

### Project Structure

```
claude-hooks-manager/
├── src/
│   ├── cli/          # CLI commands
│   ├── hooks/        # Built-in hooks
│   ├── core/         # Core functionality
│   └── utils/        # Utilities
├── tests/
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── fixtures/     # Test fixtures
├── docs/             # Documentation
└── examples/         # Example configurations
```

### Running Tests

```bash
# Run all tests
npm test

# Run unit tests
npm run test:unit

# Run integration tests
npm run test:integration

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Code Style

We use ESLint and Prettier for code formatting:

```bash
# Check code style
npm run lint

# Fix code style issues
npm run lint:fix

# Format code
npm run format
```

### Building

```bash
# Build the project
npm run build

# Build and watch for changes
npm run build:watch
```

## Making Changes

### 1. Writing Code

Follow these guidelines:

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Keep functions small and focused
- Use meaningful variable names

Example:
```javascript
// Good
function validateHookConfiguration(config) {
  if (!config || typeof config !== 'object') {
    throw new Error('Hook configuration must be an object');
  }
  
  // Validate required fields
  const requiredFields = ['name', 'type', 'executable'];
  for (const field of requiredFields) {
    if (!config[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  return true;
}

// Avoid
function validate(c) {
  if (!c) throw new Error('bad config');
  // ...
}
```

### 2. Writing Tests

All new features must include tests:

```javascript
// tests/unit/hooks/format-check.test.js
describe('format-check hook', () => {
  it('should format JavaScript files', async () => {
    const result = await runHook('format-check', {
      files: ['test.js'],
      config: { prettier: true }
    });
    
    expect(result.success).toBe(true);
    expect(result.formatted).toContain('test.js');
  });
  
  it('should skip non-JavaScript files', async () => {
    const result = await runHook('format-check', {
      files: ['image.png'],
      config: { prettier: true }
    });
    
    expect(result.skipped).toContain('image.png');
  });
});
```

### 3. Writing Documentation

Update documentation for new features:

```markdown
### `claude-hooks new-command`

Description of what the command does.

**Usage:**
\```bash
claude-hooks new-command [options]
\```

**Options:**
- `--option` - Description of option

**Examples:**
\```bash
# Example usage
claude-hooks new-command --option value
\```
```

### 4. Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Format: type(scope): subject

# Examples:
git commit -m "feat(hooks): add Python formatting hook"
git commit -m "fix(cli): resolve path resolution issue on Windows"
git commit -m "docs(api): update hook development guide"
git commit -m "test(integration): add monorepo test cases"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

## Creating Built-in Hooks

### Hook Structure

New built-in hooks go in `src/hooks/`:

```javascript
// src/hooks/my-new-hook/index.js
module.exports = {
  name: 'my-new-hook',
  description: 'Description of the hook',
  type: 'pre-commit',
  
  defaultConfig: {
    option1: true,
    option2: 'value'
  },
  
  async run(context) {
    const { files, config, utils } = context;
    
    // Hook implementation
    try {
      // Do something
      return {
        success: true,
        message: 'Hook completed successfully'
      };
    } catch (error) {
      return {
        success: false,
        message: error.message,
        details: error.stack
      };
    }
  }
};
```

### Hook Tests

```javascript
// src/hooks/my-new-hook/my-new-hook.test.js
const hook = require('./index');

describe('my-new-hook', () => {
  it('should have required properties', () => {
    expect(hook.name).toBe('my-new-hook');
    expect(hook.type).toBe('pre-commit');
    expect(typeof hook.run).toBe('function');
  });
  
  // Add specific tests
});
```

### Hook Documentation

Create `src/hooks/my-new-hook/README.md`:

```markdown
# my-new-hook

Description of what this hook does.

## Configuration

\```json
{
  "my-new-hook": {
    "option1": true,
    "option2": "value"
  }
}
\```

## Usage

\```bash
claude-hooks install my-new-hook
\```
```

## Submitting Pull Requests

### Before Submitting

1. Ensure all tests pass:
```bash
npm test
```

2. Check code coverage:
```bash
npm run test:coverage
```

3. Update documentation:
- Add/update relevant wiki pages
- Update README if needed
- Add examples if applicable

4. Test your changes locally:
```bash
# Link your local version
npm link

# Test in another project
cd /path/to/test/project
npm link claude-hooks-manager
claude-hooks install your-new-hook
```

### Pull Request Process

1. Push your branch:
```bash
git push origin feature/your-feature-name
```

2. Create a pull request with:
   - Clear title following commit conventions
   - Description of changes
   - Related issue numbers
   - Screenshots (if UI changes)
   - Testing instructions

3. PR checklist:
   - [ ] Tests pass
   - [ ] Code follows style guide
   - [ ] Documentation updated
   - [ ] Commits follow conventions
   - [ ] Branch is up to date with main

### Review Process

- PRs require at least one review
- Address review feedback
- Keep PRs focused and small
- Be patient and respectful

## Release Process

Maintainers handle releases:

1. Update version:
```bash
npm version minor
```

2. Update CHANGELOG.md

3. Create release:
```bash
npm run release
```

## Community

### Getting Help

- Join our [Discord server](https://discord.gg/claude-hooks)
- Attend community meetings (first Tuesday of each month)
- Check [discussions](https://github.com/your-repo/claude-hooks-manager/discussions)

### Recognition

We recognize contributors in:
- CONTRIBUTORS.md file
- Release notes
- Annual contributor spotlight

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Claude Hooks Manager! Your efforts help make development better for everyone.

[← FAQ](FAQ.md) | [Home](Home.md) | [API Reference →](API-Reference.md)