#!/usr/bin/env node

/**
 * Claude Code Hooks - Main entry point
 * 
 * This package provides a collection of hooks for Claude Code to enforce
 * coding standards, maintain consistency, and automate workflow tasks.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Hook metadata
const hooks = {
  'pre-commit-validator': {
    description: 'Enforces coding standards before commits',
    event: 'before_tool_call',
    tools: ['Bash']
  },
  'validate-git-commit': {
    description: 'Validates commit message format',
    event: 'after_tool_call',
    tools: ['Bash']
  },
  'database-extension-check': {
    description: 'Validates database migration files',
    event: 'before_tool_call',
    tools: ['Write', 'MultiEdit']
  },
  'duplicate-detector': {
    description: 'Detects code duplication',
    event: 'before_tool_call',
    tools: ['Write', 'MultiEdit']
  },
  'style-consistency': {
    description: 'Enforces consistent coding style',
    event: 'after_tool_call',
    tools: ['Write', 'MultiEdit', 'Edit']
  },
  'api-endpoint-verifier': {
    description: 'Validates API endpoints',
    event: 'before_tool_call',
    tools: ['Write', 'MultiEdit']
  },
  'validate-dart-task': {
    description: 'Validates Dart task creation',
    event: 'before_tool_call',
    tools: ['mcp__dart__create_task', 'mcp__dart__update_task']
  },
  'sync-docs-to-dart': {
    description: 'Syncs documentation to Dart',
    event: 'after_tool_call',
    tools: ['Write']
  },
  'log-commands': {
    description: 'Logs all executed commands',
    event: 'after_tool_call',
    tools: ['Bash']
  },
  'mcp-tool-enforcer': {
    description: 'Enforces MCP tool usage policies',
    event: 'before_tool_call',
    tools: ['Task']
  },
  'session-end-summary': {
    description: 'Provides session summary on exit',
    event: 'on_exit',
    tools: []
  },
  'api-docs-enforcer': {
    description: 'Ensures API documentation completeness',
    event: 'before_tool_call',
    tools: ['Write', 'MultiEdit']
  },
  'no-mock-code': {
    description: 'Prevents placeholder/mock code',
    event: 'before_tool_call',
    tools: ['Write', 'MultiEdit', 'Edit']
  },
  'secret-scanner': {
    description: 'Detects and blocks secrets',
    event: 'before_tool_call',
    tools: ['Write', 'MultiEdit', 'Edit']
  },
  'env-sync-validator': {
    description: 'Keeps .env files synchronized',
    event: 'after_tool_call',
    tools: ['Write', 'MultiEdit', 'Edit']
  },
  'gitignore-enforcer': {
    description: 'Ensures proper .gitignore configuration',
    event: 'before_tool_call',
    tools: ['Write', 'MultiEdit']
  },
  'readme-update-validator': {
    description: 'Reminds to update documentation',
    event: 'after_tool_call',
    tools: ['Write', 'MultiEdit', 'Edit']
  }
};

// Main function
function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'list':
      listHooks();
      break;
    case 'info':
      if (args[1]) {
        showHookInfo(args[1]);
      } else {
        console.error('Please specify a hook name');
        process.exit(1);
      }
      break;
    case 'install':
      console.log('To install hooks, run: ./install.sh');
      console.log('Or copy the hooks you want to ~/.claude/hooks/');
      break;
    case 'test':
      runTests();
      break;
    case '--version':
    case '-v':
      showVersion();
      break;
    case '--help':
    case '-h':
    case undefined:
      showHelp();
      break;
    default:
      console.error(`Unknown command: ${command}`);
      showHelp();
      process.exit(1);
  }
}

function listHooks() {
  console.log('Available Claude Code Hooks:\n');
  Object.entries(hooks).forEach(([name, info]) => {
    console.log(`  ${name.padEnd(30)} ${info.description}`);
  });
}

function showHookInfo(hookName) {
  const hook = hooks[hookName];
  if (!hook) {
    console.error(`Hook not found: ${hookName}`);
    console.log('Run "claude-hooks list" to see available hooks');
    process.exit(1);
  }

  console.log(`\nHook: ${hookName}`);
  console.log(`Description: ${hook.description}`);
  console.log(`Event: ${hook.event}`);
  console.log(`Tools: ${hook.tools.length > 0 ? hook.tools.join(', ') : 'All tools'}`);
  
  // Try to read the hook file for more details
  const hookPath = path.join(__dirname, `${hookName}.py`);
  if (fs.existsSync(hookPath)) {
    console.log('\nTo see implementation details, check:');
    console.log(`  ${hookPath}`);
  }
}

function runTests() {
  console.log('Running tests...\n');
  try {
    execSync('./run_tests.sh', { stdio: 'inherit' });
  } catch (error) {
    console.error('Tests failed');
    process.exit(1);
  }
}

function showVersion() {
  const packageJson = require('./package.json');
  console.log(`claude-code-hooks v${packageJson.version}`);
}

function showHelp() {
  console.log(`
Claude Code Hooks - Enhance your Claude Code workflow

Usage: claude-hooks <command> [options]

Commands:
  list              List all available hooks
  info <hook>       Show detailed information about a specific hook
  install           Show installation instructions
  test              Run the test suite

Options:
  -h, --help        Show this help message
  -v, --version     Show version number

Examples:
  claude-hooks list
  claude-hooks info secret-scanner
  claude-hooks test

For more information, visit:
https://github.com/webdevtodayjason/claude-hooks
`);
}

// Run main function if executed directly
if (require.main === module) {
  main();
}

// Export for programmatic use
module.exports = {
  hooks,
  listHooks,
  showHookInfo
};