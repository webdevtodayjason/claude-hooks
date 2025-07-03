#!/usr/bin/env node

/**
 * Claude Code Hooks - Enhanced CLI with interactive features
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const chalk = require('chalk');
const inquirer = require('inquirer');
const ora = require('ora');

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
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  // If no command, show interactive menu
  if (!command) {
    return showInteractiveMenu();
  }

  switch (command) {
    case 'list':
      listHooks();
      break;
    case 'info':
      if (args[1]) {
        showHookInfo(args[1]);
      } else {
        console.error(chalk.red('Please specify a hook name'));
        process.exit(1);
      }
      break;
    case 'install':
      await installHooks();
      break;
    case 'test':
      runTests();
      break;
    case 'status':
      await showStatus();
      break;
    case 'enable':
      if (args[1]) {
        await enableHook(args[1]);
      } else {
        console.error(chalk.red('Please specify a hook name'));
        process.exit(1);
      }
      break;
    case 'disable':
      if (args[1]) {
        await disableHook(args[1]);
      } else {
        console.error(chalk.red('Please specify a hook name'));
        process.exit(1);
      }
      break;
    case 'init':
      await initProject();
      break;
    case 'doctor':
      await runDoctor();
      break;
    case '--version':
    case '-v':
      showVersion();
      break;
    case '--help':
    case '-h':
      showHelp();
      break;
    default:
      console.error(chalk.red(`Unknown command: ${command}`));
      showHelp();
      process.exit(1);
  }
}

// Interactive menu
async function showInteractiveMenu() {
  console.log(chalk.cyan('\n🪝 Claude Code Hooks Interactive Menu\n'));

  const { action } = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: 'What would you like to do?',
      choices: [
        { name: '📦 Install hooks to Claude Code', value: 'install' },
        { name: '📋 List all available hooks', value: 'list' },
        { name: '🔍 Get info about a specific hook', value: 'info' },
        { name: '✅ Check installation status', value: 'status' },
        { name: '🧪 Run tests', value: 'test' },
        { name: '🩺 Run diagnostics (doctor)', value: 'doctor' },
        { name: '🚀 Initialize project hooks', value: 'init' },
        new inquirer.Separator(),
        { name: '❌ Exit', value: 'exit' }
      ]
    }
  ]);

  switch (action) {
    case 'install':
      await installHooks();
      break;
    case 'list':
      listHooks();
      await promptToContinue();
      break;
    case 'info':
      await selectAndShowHookInfo();
      break;
    case 'status':
      await showStatus();
      await promptToContinue();
      break;
    case 'test':
      runTests();
      break;
    case 'doctor':
      await runDoctor();
      await promptToContinue();
      break;
    case 'init':
      await initProject();
      break;
    case 'exit':
      console.log(chalk.green('\nThanks for using Claude Code Hooks! 👋\n'));
      process.exit(0);
  }

  // Return to menu unless exited
  if (action !== 'exit') {
    await showInteractiveMenu();
  }
}

async function promptToContinue() {
  await inquirer.prompt([
    {
      type: 'input',
      name: 'continue',
      message: 'Press Enter to continue...'
    }
  ]);
}

async function selectAndShowHookInfo() {
  const { hookName } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookName',
      message: 'Select a hook to learn more:',
      choices: Object.keys(hooks).map(name => ({
        name: `${name} - ${hooks[name].description}`,
        value: name
      }))
    }
  ]);

  showHookInfo(hookName);
  await promptToContinue();
}

function listHooks() {
  console.log(chalk.cyan('\nAvailable Claude Code Hooks:\n'));
  Object.entries(hooks).forEach(([name, info]) => {
    console.log(chalk.yellow(`  ${name}.py`.padEnd(35)) + chalk.gray(info.description));
  });
  console.log();
}

function showHookInfo(hookName) {
  const hook = hooks[hookName];
  if (!hook) {
    console.error(chalk.red(`Hook not found: ${hookName}`));
    console.log(chalk.gray('Run "claude-hooks list" to see available hooks'));
    return;
  }

  console.log(chalk.cyan(`\nHook: ${hookName}.py`));
  console.log(chalk.gray('─'.repeat(50)));
  console.log(`${chalk.bold('Description:')} ${hook.description}`);
  console.log(`${chalk.bold('Event:')} ${hook.event}`);
  console.log(`${chalk.bold('Tools:')} ${hook.tools.length > 0 ? hook.tools.join(', ') : 'All tools'}`);
  
  const hookPath = path.join(__dirname, 'hooks', `${hookName}.py`);
  if (fs.existsSync(hookPath)) {
    console.log(`${chalk.bold('Location:')} ${hookPath}`);
  }
  console.log();
}

async function installHooks() {
  const spinner = ora('Installing hooks to Claude Code directory...').start();
  
  try {
    // Hide spinner output during install script
    spinner.stop();
    execSync('./install.sh', { stdio: 'inherit' });
    spinner.succeed('Hooks installed successfully!');
    console.log(chalk.green('\n✅ All hooks have been copied to ~/.claude/hooks/'));
    console.log(chalk.gray('Restart Claude Code for the hooks to take effect.\n'));
  } catch (error) {
    spinner.fail('Installation failed');
    console.error(chalk.red('Error during installation:'), error.message);
    process.exit(1);
  }
}

async function showStatus() {
  console.log(chalk.cyan('\n🔍 Checking Claude Code Hooks Status...\n'));
  
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  const settingsFile = path.join(process.env.HOME, '.claude', 'settings.json');
  
  // Check hooks directory
  if (fs.existsSync(hooksDir)) {
    console.log(chalk.green('✅ Hooks directory exists'));
    
    // Count installed hooks
    const installedHooks = fs.readdirSync(hooksDir).filter(f => f.endsWith('.py'));
    console.log(chalk.gray(`   ${installedHooks.length} hooks installed`));
  } else {
    console.log(chalk.red('❌ Hooks directory not found'));
    console.log(chalk.gray('   Run "claude-hooks install" to set up'));
  }
  
  // Check settings file
  if (fs.existsSync(settingsFile)) {
    console.log(chalk.green('✅ Settings file exists'));
  } else {
    console.log(chalk.yellow('⚠️  Settings file not found'));
    console.log(chalk.gray('   Hooks may not be configured'));
  }
  
  console.log();
}

async function enableHook(hookName) {
  // TODO: Implement hook enable functionality
  console.log(chalk.yellow(`Enabling ${hookName}... (Feature coming soon)`));
}

async function disableHook(hookName) {
  // TODO: Implement hook disable functionality
  console.log(chalk.yellow(`Disabling ${hookName}... (Feature coming soon)`));
}

async function initProject() {
  console.log(chalk.cyan('\n🚀 Initializing Claude Code Hooks for this project...\n'));
  
  const { setupType } = await inquirer.prompt([
    {
      type: 'list',
      name: 'setupType',
      message: 'How would you like to configure hooks for this project?',
      choices: [
        { name: 'Use recommended hooks for general development', value: 'general' },
        { name: 'Use strict hooks for production code', value: 'strict' },
        { name: 'Select hooks manually', value: 'manual' },
        { name: 'Skip project configuration', value: 'skip' }
      ]
    }
  ]);
  
  if (setupType === 'skip') {
    return;
  }
  
  // Create .claude directory in project
  const projectClaudeDir = path.join(process.cwd(), '.claude');
  if (!fs.existsSync(projectClaudeDir)) {
    fs.mkdirSync(projectClaudeDir, { recursive: true });
  }
  
  console.log(chalk.green(`\n✅ Created ${projectClaudeDir}`));
  console.log(chalk.gray('Add project-specific configuration here.\n'));
}

async function runDoctor() {
  console.log(chalk.cyan('\n🩺 Running Claude Code Hooks Diagnostics...\n'));
  
  const spinner = ora('Checking installation...').start();
  
  const issues = [];
  const suggestions = [];
  
  // Check Node.js version
  const nodeVersion = process.version;
  if (nodeVersion < 'v14.0.0') {
    issues.push('Node.js version is below v14.0.0');
    suggestions.push('Update Node.js to v14.0.0 or higher');
  }
  
  // Check hooks directory
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  if (!fs.existsSync(hooksDir)) {
    issues.push('Hooks directory not found');
    suggestions.push('Run "claude-hooks install" to create it');
  }
  
  // Check Python
  try {
    execSync('python3 --version', { stdio: 'pipe' });
  } catch {
    issues.push('Python 3 not found');
    suggestions.push('Install Python 3.6 or higher');
  }
  
  // Check for settings.json
  const settingsFile = path.join(process.env.HOME, '.claude', 'settings.json');
  if (!fs.existsSync(settingsFile)) {
    issues.push('Claude Code settings file not found');
    suggestions.push('Copy settings.example.json to ~/.claude/settings.json');
  }
  
  spinner.stop();
  
  if (issues.length === 0) {
    console.log(chalk.green('✅ No issues found! Everything looks good.\n'));
  } else {
    console.log(chalk.red(`❌ Found ${issues.length} issue(s):\n`));
    issues.forEach((issue, i) => {
      console.log(chalk.red(`  ${i + 1}. ${issue}`));
      console.log(chalk.gray(`     → ${suggestions[i]}`));
    });
    console.log();
  }
}

function runTests() {
  console.log(chalk.cyan('\nRunning tests...\n'));
  try {
    execSync('./tests/run_tests.sh', { stdio: 'inherit' });
  } catch (error) {
    console.error(chalk.red('Tests failed'));
    process.exit(1);
  }
}

function showVersion() {
  const packageJson = require('./package.json');
  console.log(chalk.cyan(`claude-code-hooks v${packageJson.version}`));
}

function showHelp() {
  console.log(`
${chalk.cyan('Claude Code Hooks')} - Enhance your Claude Code workflow

${chalk.bold('Usage:')} claude-hooks [command] [options]

${chalk.bold('Commands:')}
  ${chalk.yellow('(no command)')}      Launch interactive menu
  ${chalk.yellow('list')}              List all available hooks
  ${chalk.yellow('info <hook>')}       Show detailed information about a specific hook
  ${chalk.yellow('install')}           Install hooks to Claude Code directory
  ${chalk.yellow('status')}            Check installation status
  ${chalk.yellow('enable <hook>')}     Enable a specific hook (coming soon)
  ${chalk.yellow('disable <hook>')}    Disable a specific hook (coming soon)
  ${chalk.yellow('init')}              Initialize hooks for current project
  ${chalk.yellow('doctor')}            Run diagnostics to check setup
  ${chalk.yellow('test')}              Run the test suite

${chalk.bold('Options:')}
  ${chalk.yellow('-h, --help')}        Show this help message
  ${chalk.yellow('-v, --version')}     Show version number

${chalk.bold('Examples:')}
  ${chalk.gray('# Launch interactive menu')}
  claude-hooks

  ${chalk.gray('# Install hooks')}
  claude-hooks install

  ${chalk.gray('# Get info about a hook')}
  claude-hooks info secret-scanner

  ${chalk.gray('# Check if everything is set up correctly')}
  claude-hooks doctor

${chalk.gray('For more information, visit:')}
${chalk.cyan('https://github.com/webdevtodayjason/claude-hooks')}
`);
}

// Run main function if executed directly
if (require.main === module) {
  main().catch(err => {
    console.error(chalk.red('Error:'), err.message);
    process.exit(1);
  });
}

// Export for programmatic use
module.exports = {
  hooks,
  listHooks,
  showHookInfo
};