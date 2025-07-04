#!/usr/bin/env node

/**
 * Claude Hooks Manager - Enhanced CLI with interactive features
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
  },
  'timestamp-validator': {
    description: 'Validates dates and timestamps for accuracy',
    event: 'before_tool_call',
    tools: ['Write', 'Edit', 'MultiEdit', 'Bash']
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
    case 'create':
      if (args[1]) {
        await createHook(args[1]);
      } else {
        console.error(chalk.red('Please specify a hook name'));
        process.exit(1);
      }
      break;
    case 'edit':
      if (args[1]) {
        await editHook(args[1]);
      } else {
        console.error(chalk.red('Please specify a hook name'));
        process.exit(1);
      }
      break;
    case 'remove':
      if (args[1]) {
        await removeHook(args[1]);
      } else {
        console.error(chalk.red('Please specify a hook name'));
        process.exit(1);
      }
      break;
    case 'config':
      await configureSettings();
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
  console.log(chalk.cyan('\n🪝 Claude Hooks Manager Interactive Menu\n'));

  const { action } = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: 'What would you like to do?',
      choices: [
        { name: '📦 Install hooks to Claude', value: 'install' },
        { name: '📋 List all available hooks', value: 'list' },
        { name: '🔍 Get info about a specific hook', value: 'info' },
        { name: '✅ Check installation status', value: 'status' },
        new inquirer.Separator('─── Hook Management ───'),
        { name: '🟢 Enable a hook', value: 'enable' },
        { name: '🔴 Disable a hook', value: 'disable' },
        { name: '➕ Create new hook', value: 'create' },
        { name: '✏️  Edit existing hook', value: 'edit' },
        { name: '🗑️  Remove a hook', value: 'remove' },
        new inquirer.Separator('─── Configuration ───'),
        { name: '⚙️  Configure settings', value: 'config' },
        { name: '🚀 Initialize project hooks', value: 'init' },
        { name: '🩺 Run diagnostics (doctor)', value: 'doctor' },
        { name: '🧪 Run tests', value: 'test' },
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
    case 'enable':
      await selectAndEnableHook();
      break;
    case 'disable':
      await selectAndDisableHook();
      break;
    case 'create':
      await promptAndCreateHook();
      break;
    case 'edit':
      await selectAndEditHook();
      break;
    case 'remove':
      await selectAndRemoveHook();
      break;
    case 'config':
      await configureSettings();
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
      console.log(chalk.green('\nThanks for using Claude Hooks Manager! 👋\n'));
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
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  
  const { hookName } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookName',
      message: 'Select a hook to learn more:',
      choices: Object.keys(hooks).map(name => {
        // Check status
        const hookPath = path.join(hooksDir, `${name}.py`);
        const disabledPath = path.join(hooksDir, `${name}.py.disabled`);
        
        let status = '';
        if (fs.existsSync(hookPath)) {
          status = chalk.green('●') + ' ';
        } else if (fs.existsSync(disabledPath)) {
          status = chalk.red('●') + ' ';
        } else {
          status = chalk.gray('○') + ' ';
        }
        
        return {
          name: `${status}${name} - ${hooks[name].description}`,
          value: name
        };
      })
    }
  ]);

  showHookInfo(hookName);
  await promptToContinue();
}

async function selectAndEnableHook() {
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  const disabledHooks = fs.readdirSync(hooksDir)
    .filter(f => f.endsWith('.py.disabled'))
    .map(f => f.replace('.py.disabled', ''));
  
  if (disabledHooks.length === 0) {
    console.log(chalk.yellow('\nNo disabled hooks found.'));
    await promptToContinue();
    return;
  }
  
  const { hookName } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookName',
      message: 'Select a hook to enable:',
      choices: disabledHooks
    }
  ]);
  
  await enableHook(hookName);
  await promptToContinue();
}

async function selectAndDisableHook() {
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  const enabledHooks = fs.readdirSync(hooksDir)
    .filter(f => f.endsWith('.py') && !f.endsWith('.disabled'))
    .map(f => f.replace('.py', ''));
  
  if (enabledHooks.length === 0) {
    console.log(chalk.yellow('\nNo enabled hooks found.'));
    await promptToContinue();
    return;
  }
  
  const { hookName } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookName',
      message: 'Select a hook to disable:',
      choices: enabledHooks
    }
  ]);
  
  await disableHook(hookName);
  await promptToContinue();
}

async function promptAndCreateHook() {
  const { hookName } = await inquirer.prompt([
    {
      type: 'input',
      name: 'hookName',
      message: 'Enter name for new hook (without .py):',
      validate: (input) => {
        if (!input) return 'Hook name is required';
        if (!/^[a-z0-9-_]+$/.test(input)) return 'Use only lowercase letters, numbers, hyphens, and underscores';
        return true;
      }
    }
  ]);
  
  await createHook(hookName);
  await promptToContinue();
}

async function selectAndEditHook() {
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  const allHooks = fs.readdirSync(hooksDir)
    .filter(f => f.endsWith('.py'))
    .map(f => f.replace('.py', ''));
  
  if (allHooks.length === 0) {
    console.log(chalk.yellow('\nNo hooks found to edit.'));
    await promptToContinue();
    return;
  }
  
  const { hookName } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookName',
      message: 'Select a hook to edit:',
      choices: allHooks
    }
  ]);
  
  await editHook(hookName);
  await promptToContinue();
}

async function selectAndRemoveHook() {
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  const allHooks = fs.readdirSync(hooksDir)
    .filter(f => f.endsWith('.py') || f.endsWith('.py.disabled'))
    .map(f => f.replace(/\.py(\.disabled)?$/, ''));
  
  // Remove duplicates
  const uniqueHooks = [...new Set(allHooks)];
  
  if (uniqueHooks.length === 0) {
    console.log(chalk.yellow('\nNo hooks found to remove.'));
    await promptToContinue();
    return;
  }
  
  const { hookName } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookName',
      message: 'Select a hook to remove:',
      choices: uniqueHooks
    }
  ]);
  
  await removeHook(hookName);
  await promptToContinue();
}

function listHooks() {
  console.log(chalk.cyan('\nAvailable Claude Hooks:\n'));
  
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  
  Object.entries(hooks).forEach(([name, info]) => {
    // Check if hook is enabled or disabled
    const hookPath = path.join(hooksDir, `${name}.py`);
    const disabledPath = path.join(hooksDir, `${name}.py.disabled`);
    
    let status = '';
    if (fs.existsSync(hookPath)) {
      status = chalk.green('●') + ' '; // Green dot for enabled
    } else if (fs.existsSync(disabledPath)) {
      status = chalk.red('●') + ' '; // Red dot for disabled
    } else {
      status = chalk.gray('○') + ' '; // Gray circle for not installed
    }
    
    console.log(`  ${status}${chalk.yellow(`${name}.py`.padEnd(33))} ${chalk.gray(info.description)}`);
  });
  
  console.log('\n' + chalk.gray('  ● Enabled  ● Disabled  ○ Not Installed'));
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
  const spinner = ora('Installing hooks to Claude directory...').start();
  
  try {
    // Hide spinner output during install script
    spinner.stop();
    execSync('./install.sh', { stdio: 'inherit' });
    spinner.succeed('Hooks installed successfully!');
    console.log(chalk.green('\n✅ All hooks have been copied to ~/.claude/hooks/'));
    console.log(chalk.gray('Restart Claude for the hooks to take effect.\n'));
  } catch (error) {
    spinner.fail('Installation failed');
    console.error(chalk.red('Error during installation:'), error.message);
    process.exit(1);
  }
}

async function showStatus() {
  console.log(chalk.cyan('\n🔍 Checking Claude Hooks Manager Status...\n'));
  
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  const settingsFile = path.join(process.env.HOME, '.claude', 'settings.json');
  
  // Check hooks directory
  if (fs.existsSync(hooksDir)) {
    console.log(chalk.green('✅ Hooks directory exists'));
    
    // Count hooks by status
    const allFiles = fs.readdirSync(hooksDir);
    const enabledHooks = allFiles.filter(f => f.endsWith('.py') && !f.endsWith('.disabled'));
    const disabledHooks = allFiles.filter(f => f.endsWith('.py.disabled'));
    
    console.log(chalk.gray(`   ${chalk.green('●')} ${enabledHooks.length} hooks enabled`));
    console.log(chalk.gray(`   ${chalk.red('●')} ${disabledHooks.length} hooks disabled`));
    console.log(chalk.gray(`   ${enabledHooks.length + disabledHooks.length} total hooks installed`));
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
  const hookPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py`);
  const disabledPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.disabled`);
  
  if (fs.existsSync(hookPath)) {
    console.log(chalk.yellow(`Hook ${hookName} is already enabled`));
    return;
  }
  
  if (fs.existsSync(disabledPath)) {
    try {
      fs.renameSync(disabledPath, hookPath);
      console.log(chalk.green(`✅ Enabled ${hookName}`));
    } catch (error) {
      console.error(chalk.red(`Failed to enable ${hookName}:`), error.message);
    }
  } else {
    console.error(chalk.red(`Hook ${hookName} not found`));
    console.log(chalk.gray('Run "claude-hooks list" to see available hooks'));
  }
}

async function disableHook(hookName) {
  const hookPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py`);
  const disabledPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.disabled`);
  
  if (!fs.existsSync(hookPath)) {
    if (fs.existsSync(disabledPath)) {
      console.log(chalk.yellow(`Hook ${hookName} is already disabled`));
    } else {
      console.error(chalk.red(`Hook ${hookName} not found`));
    }
    return;
  }
  
  try {
    fs.renameSync(hookPath, disabledPath);
    console.log(chalk.green(`✅ Disabled ${hookName}`));
    console.log(chalk.gray('The hook will not run until re-enabled'));
  } catch (error) {
    console.error(chalk.red(`Failed to disable ${hookName}:`), error.message);
  }
}

async function initProject() {
  console.log(chalk.cyan('\n🚀 Initializing Claude Hooks Manager for this project...\n'));
  
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
  console.log(chalk.cyan('\n🩺 Running Claude Hooks Manager Diagnostics...\n'));
  
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
    issues.push('Claude settings file not found');
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

async function createHook(hookName) {
  console.log(chalk.cyan(`\n🔨 Creating new hook: ${hookName}.py\n`));
  
  const { hookType } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookType',
      message: 'Select hook event type:',
      choices: [
        { name: 'before_tool_call - Run before a tool is called', value: 'before_tool_call' },
        { name: 'after_tool_call - Run after a tool is called', value: 'after_tool_call' },
        { name: 'on_exit - Run when session ends', value: 'on_exit' }
      ]
    }
  ]);
  
  const { tools } = await inquirer.prompt([
    {
      type: 'checkbox',
      name: 'tools',
      message: 'Select tools to monitor (leave empty for all):',
      choices: ['Bash', 'Write', 'Edit', 'MultiEdit', 'Read', 'Task', 'WebFetch', 'WebSearch']
    }
  ]);
  
  const template = `#!/usr/bin/env python3
"""
${hookName} hook for Claude.
Created: ${new Date().toISOString().split('T')[0]}
"""
import json
import sys

def main():
    try:
        # Read input from Claude
        input_data = json.load(sys.stdin)
        
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        
        # Add your hook logic here
        # Example: Check something and provide feedback
        
        # Exit code 0 = continue (with optional warning)
        # Exit code 2 = block the operation
        sys.exit(0)
        
    except json.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
`;

  const hookPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py`);
  
  try {
    fs.writeFileSync(hookPath, template);
    fs.chmodSync(hookPath, 0o755);
    console.log(chalk.green(`✅ Created ${hookPath}`));
    console.log(chalk.gray('\nNext steps:'));
    console.log(chalk.gray(`1. Edit the hook: claude-hooks edit ${hookName}`));
    console.log(chalk.gray(`2. Update ~/.claude/settings.json to register the hook`));
  } catch (error) {
    console.error(chalk.red('Failed to create hook:'), error.message);
  }
}

async function editHook(hookName) {
  const hookPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py`);
  
  if (!fs.existsSync(hookPath)) {
    console.error(chalk.red(`Hook ${hookName} not found`));
    return;
  }
  
  const editor = process.env.EDITOR || 'nano';
  console.log(chalk.cyan(`Opening ${hookName}.py in ${editor}...`));
  
  try {
    execSync(`${editor} "${hookPath}"`, { stdio: 'inherit' });
  } catch (error) {
    console.error(chalk.red('Failed to open editor:'), error.message);
    console.log(chalk.gray(`You can manually edit: ${hookPath}`));
  }
}

async function removeHook(hookName) {
  const hookPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py`);
  const disabledPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.disabled`);
  
  if (!fs.existsSync(hookPath) && !fs.existsSync(disabledPath)) {
    console.error(chalk.red(`Hook ${hookName} not found`));
    return;
  }
  
  const { confirm } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'confirm',
      message: `Are you sure you want to remove ${hookName}?`,
      default: false
    }
  ]);
  
  if (!confirm) {
    console.log(chalk.yellow('Cancelled'));
    return;
  }
  
  try {
    if (fs.existsSync(hookPath)) fs.unlinkSync(hookPath);
    if (fs.existsSync(disabledPath)) fs.unlinkSync(disabledPath);
    console.log(chalk.green(`✅ Removed ${hookName}`));
  } catch (error) {
    console.error(chalk.red('Failed to remove hook:'), error.message);
  }
}

async function configureSettings() {
  const settingsPath = path.join(process.env.HOME, '.claude', 'settings.json');
  
  if (!fs.existsSync(settingsPath)) {
    console.log(chalk.yellow('Settings file not found. Creating from template...'));
    try {
      const templatePath = path.join(__dirname, 'settings.example.json');
      fs.copyFileSync(templatePath, settingsPath);
      console.log(chalk.green('✅ Created settings.json'));
    } catch (error) {
      console.error(chalk.red('Failed to create settings:'), error.message);
      return;
    }
  }
  
  const editor = process.env.EDITOR || 'nano';
  console.log(chalk.cyan(`Opening settings.json in ${editor}...`));
  
  try {
    execSync(`${editor} "${settingsPath}"`, { stdio: 'inherit' });
  } catch (error) {
    console.error(chalk.red('Failed to open editor:'), error.message);
    console.log(chalk.gray(`You can manually edit: ${settingsPath}`));
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
${chalk.cyan('Claude Hooks Manager')} - Enhance your Claude workflow

${chalk.bold('Usage:')} claude-hooks [command] [options]

${chalk.bold('Commands:')}
  ${chalk.yellow('(no command)')}      Launch interactive menu
  ${chalk.yellow('list')}              List all available hooks
  ${chalk.yellow('info <hook>')}       Show detailed information about a specific hook
  ${chalk.yellow('install')}           Install hooks to Claude directory
  ${chalk.yellow('status')}            Check installation status
  ${chalk.yellow('enable <hook>')}     Enable a disabled hook
  ${chalk.yellow('disable <hook>')}    Disable a hook temporarily
  ${chalk.yellow('create <name>')}     Create a new custom hook
  ${chalk.yellow('edit <hook>')}       Edit an existing hook
  ${chalk.yellow('remove <hook>')}     Remove a hook permanently
  ${chalk.yellow('config')}            Edit Claude Hooks Manager settings
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