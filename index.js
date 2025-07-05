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
        new inquirer.Separator('─── Dart Integration ───'),
        { name: '🎯 Initialize Dart config', value: 'dart-init' },
        { name: '📝 Edit Dart config', value: 'dart-edit' },
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
    case 'dart-init':
      await initDartConfig();
      break;
    case 'dart-edit':
      await editDartConfig();
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
    .filter(f => f.endsWith('.py.disabled') || f.endsWith('.py.original'))
    .map(f => f.replace(/\.py\.(disabled|original)$/, ''));
  
  // Remove duplicates
  const uniqueDisabledHooks = [...new Set(disabledHooks)];
  
  if (uniqueDisabledHooks.length === 0) {
    console.log(chalk.yellow('\nNo disabled hooks found.'));
    await promptToContinue();
    return;
  }
  
  const { hookName } = await inquirer.prompt([
    {
      type: 'list',
      name: 'hookName',
      message: 'Select a hook to enable:',
      choices: uniqueDisabledHooks
    }
  ]);
  
  await enableHook(hookName);
  await promptToContinue();
}

async function selectAndDisableHook() {
  const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');
  const pyFiles = fs.readdirSync(hooksDir)
    .filter(f => f.endsWith('.py') && !f.endsWith('.disabled') && !f.endsWith('.original'));
  
  // Filter out stub files
  const enabledHooks = [];
  for (const file of pyFiles) {
    const hookName = file.replace('.py', '');
    const hookPath = path.join(hooksDir, file);
    
    // Check if there's an .original file (which means it's disabled)
    if (!fs.existsSync(path.join(hooksDir, `${hookName}.py.original`))) {
      try {
        const content = fs.readFileSync(hookPath, 'utf8');
        // Skip if it's a stub file
        if (!content.includes('Stub for disabled hook:')) {
          enabledHooks.push(hookName);
        }
      } catch {
        // If we can't read the file, assume it's enabled
        enabledHooks.push(hookName);
      }
    }
  }
  
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
    .filter(f => f.endsWith('.py') || f.endsWith('.py.disabled') || f.endsWith('.py.original'))
    .map(f => f.replace(/\.py(\.disabled|\.original)?$/, ''));
  
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
    const originalPath = path.join(hooksDir, `${name}.py.original`);
    const disabledPath = path.join(hooksDir, `${name}.py.disabled`);
    
    let status = '';
    if (fs.existsSync(originalPath)) {
      // New disable mechanism - hook is disabled with stub in place
      status = chalk.red('●') + ' '; // Red dot for disabled
    } else if (fs.existsSync(disabledPath)) {
      // Old disable mechanism - backward compatibility
      status = chalk.red('●') + ' '; // Red dot for disabled
    } else if (fs.existsSync(hookPath)) {
      // Check if it's a stub file
      try {
        const content = fs.readFileSync(hookPath, 'utf8');
        if (content.includes('Stub for disabled hook:')) {
          status = chalk.red('●') + ' '; // Red dot for disabled (stub)
        } else {
          status = chalk.green('●') + ' '; // Green dot for enabled
        }
      } catch {
        status = chalk.green('●') + ' '; // Green dot for enabled
      }
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
  const originalPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.original`);
  const disabledPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.disabled`);
  
  // Check if we have an .original file (new disable mechanism)
  if (fs.existsSync(originalPath)) {
    try {
      // Read the stub to check if it's our stub
      const currentContent = fs.readFileSync(hookPath, 'utf8');
      if (currentContent.includes('Stub for disabled hook:')) {
        // Delete the stub
        fs.unlinkSync(hookPath);
      }
      
      // Restore the original
      fs.renameSync(originalPath, hookPath);
      console.log(chalk.green(`✅ Enabled ${hookName}`));
    } catch (error) {
      console.error(chalk.red(`Failed to enable ${hookName}:`), error.message);
    }
    return;
  }
  
  // Check for old .disabled file format (backward compatibility)
  if (fs.existsSync(disabledPath)) {
    try {
      fs.renameSync(disabledPath, hookPath);
      console.log(chalk.green(`✅ Enabled ${hookName}`));
    } catch (error) {
      console.error(chalk.red(`Failed to enable ${hookName}:`), error.message);
    }
    return;
  }
  
  // Check if already enabled
  if (fs.existsSync(hookPath)) {
    const content = fs.readFileSync(hookPath, 'utf8');
    if (content.includes('Stub for disabled hook:')) {
      console.log(chalk.yellow(`Hook ${hookName} is disabled (stub file present)`));
      console.log(chalk.gray('This indicates an error in the disable/enable process'));
    } else {
      console.log(chalk.yellow(`Hook ${hookName} is already enabled`));
    }
    return;
  }
  
  console.error(chalk.red(`Hook ${hookName} not found`));
  console.log(chalk.gray('Run "claude-hooks list" to see available hooks'));
}

async function disableHook(hookName) {
  const hookPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py`);
  const originalPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.original`);
  
  // Check if already disabled
  if (fs.existsSync(originalPath)) {
    console.log(chalk.yellow(`Hook ${hookName} is already disabled`));
    return;
  }
  
  if (!fs.existsSync(hookPath)) {
    console.error(chalk.red(`Hook ${hookName} not found`));
    return;
  }
  
  try {
    // Move the actual hook to .original
    fs.renameSync(hookPath, originalPath);
    
    // Create a stub that exits cleanly
    const stubContent = `#!/usr/bin/env python3
"""
Stub for disabled hook: ${hookName}
This hook has been disabled but remains in place to prevent errors.
To re-enable, use: claude-hooks enable ${hookName}
"""
import json
import sys

# Read input to prevent broken pipe errors
try:
    json.load(sys.stdin)
except:
    pass

# Exit cleanly with a message
print(f"Hook '${hookName}' is currently disabled", file=sys.stderr)
sys.exit(0)
`;
    
    fs.writeFileSync(hookPath, stubContent);
    fs.chmodSync(hookPath, '755');
    
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
  
  // Ask about Dart integration
  const { setupDart } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'setupDart',
      message: 'Would you like to set up Dart integration for this project?',
      default: true
    }
  ]);
  
  if (setupDart) {
    await initDartConfig();
  } else {
    // Ask about CLAUDE.md without Dart
    const { createClaudeMd } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'createClaudeMd',
        message: 'Would you like to create a CLAUDE.md file with project instructions?',
        default: true
      }
    ]);
    
    if (createClaudeMd) {
      await createClaudeInstructions({}, process.cwd());
    }
  }
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
  const originalPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.original`);
  const disabledPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.disabled`);
  
  let pathToEdit = hookPath;
  
  // Check if the hook is disabled
  if (fs.existsSync(originalPath)) {
    console.log(chalk.yellow(`Note: ${hookName} is currently disabled`));
    pathToEdit = originalPath;
  } else if (fs.existsSync(disabledPath)) {
    console.log(chalk.yellow(`Note: ${hookName} is currently disabled (old format)`));
    pathToEdit = disabledPath;
  } else if (fs.existsSync(hookPath)) {
    // Check if it's a stub
    try {
      const content = fs.readFileSync(hookPath, 'utf8');
      if (content.includes('Stub for disabled hook:')) {
        console.log(chalk.yellow(`Note: ${hookName} is currently disabled (stub)`));
        console.log(chalk.gray('Enable the hook first to edit the actual code'));
        return;
      }
    } catch {
      // Continue with normal edit
    }
  } else {
    console.error(chalk.red(`Hook ${hookName} not found`));
    return;
  }
  
  const editor = process.env.EDITOR || 'nano';
  console.log(chalk.cyan(`Opening ${path.basename(pathToEdit)} in ${editor}...`));
  
  try {
    execSync(`${editor} "${pathToEdit}"`, { stdio: 'inherit' });
  } catch (error) {
    console.error(chalk.red('Failed to open editor:'), error.message);
    console.log(chalk.gray(`You can manually edit: ${pathToEdit}`));
  }
}

async function removeHook(hookName) {
  const hookPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py`);
  const disabledPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.disabled`);
  const originalPath = path.join(process.env.HOME, '.claude', 'hooks', `${hookName}.py.original`);
  
  if (!fs.existsSync(hookPath) && !fs.existsSync(disabledPath) && !fs.existsSync(originalPath)) {
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
    if (fs.existsSync(originalPath)) fs.unlinkSync(originalPath);
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

async function initDartConfig() {
  console.log(chalk.cyan('\n🎯 Initializing Dart Configuration\n'));
  
  const projectRoot = process.cwd();
  const projectName = path.basename(projectRoot);
  const dartFile = path.join(projectRoot, '.dart');
  
  // Check if .dart already exists
  if (fs.existsSync(dartFile)) {
    console.log(chalk.yellow('⚠️  .dart file already exists in this project'));
    const { overwrite } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'overwrite',
        message: 'Do you want to overwrite it?',
        default: false
      }
    ]);
    
    if (!overwrite) {
      console.log(chalk.gray('Cancelled'));
      await promptToContinue();
      return;
    }
  }
  
  // Prompt for configuration
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'workspace',
      message: 'Enter Dart workspace name:',
      default: projectName,
      validate: input => input.trim() ? true : 'Workspace name is required'
    },
    {
      type: 'input',
      name: 'tasksFolder',
      message: 'Enter tasks dartboard (e.g., workspace/Tasks):',
      default: answers => `${answers.workspace}/Tasks`,
      validate: input => input.includes('/') ? true : 'Format should be workspace/board'
    },
    {
      type: 'input',
      name: 'docsFolder',
      message: 'Enter documentation folder (e.g., workspace/Docs):',
      default: answers => `${answers.workspace}/Docs`,
      validate: input => input.includes('/') ? true : 'Format should be workspace/folder'
    },
    {
      type: 'confirm',
      name: 'syncEnabled',
      message: 'Enable automatic documentation sync suggestions?',
      default: true
    }
  ]);
  
  // Create configuration
  const dartConfig = {
    workspace: answers.workspace,
    tasksFolder: answers.tasksFolder,
    docsFolder: answers.docsFolder,
    syncEnabled: answers.syncEnabled,
    syncRules: {
      include: ['README.md', 'docs/**/*.md'],
      exclude: ['.github/**/*.md', 'node_modules/**/*.md', 'test/**/*.md']
    }
  };
  
  // Ask about CLAUDE.md
  const { createClaudeMd } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'createClaudeMd',
      message: 'Would you like to create a CLAUDE.md file with project instructions?',
      default: true
    }
  ]);
  
  // Write .dart file
  try {
    fs.writeFileSync(dartFile, JSON.stringify(dartConfig, null, 2));
    console.log(chalk.green(`\n✅ Created .dart configuration file`));
    console.log(chalk.gray(`Location: ${dartFile}`));
    console.log('\nConfiguration:');
    console.log(chalk.gray(JSON.stringify(dartConfig, null, 2)));
    
    // Add to .gitignore
    const gitignorePath = path.join(projectRoot, '.gitignore');
    if (fs.existsSync(gitignorePath)) {
      const gitignore = fs.readFileSync(gitignorePath, 'utf8');
      if (!gitignore.includes('.dart')) {
        fs.appendFileSync(gitignorePath, '\n# Dart workspace configuration\n.dart\n');
        console.log(chalk.gray('\n✅ Added .dart to .gitignore'));
      }
    }
    
    // Create CLAUDE.md if requested
    if (createClaudeMd) {
      await createClaudeInstructions(dartConfig, projectRoot);
    }
    
  } catch (error) {
    console.error(chalk.red('Failed to create .dart file:'), error.message);
  }
  
  await promptToContinue();
}

async function createClaudeInstructions(dartConfig, projectRoot) {
  const claudeMdPath = path.join(projectRoot, 'CLAUDE.md');
  const projectName = path.basename(projectRoot);
  
  // Check if CLAUDE.md already exists
  if (fs.existsSync(claudeMdPath)) {
    const { overwrite } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'overwrite',
        message: 'CLAUDE.md already exists. Overwrite it?',
        default: false
      }
    ]);
    
    if (!overwrite) {
      return;
    }
  }
  
  // Gather additional project information
  const projectInfo = await inquirer.prompt([
    {
      type: 'input',
      name: 'description',
      message: 'Brief project description:',
      default: `${projectName} project`
    },
    {
      type: 'input',
      name: 'primaryLanguage',
      message: 'Primary programming language:',
      default: 'JavaScript'
    },
    {
      type: 'input',
      name: 'testCommand',
      message: 'Test command (if any):',
      default: 'npm test'
    },
    {
      type: 'input',
      name: 'lintCommand',
      message: 'Lint command (if any):',
      default: 'npm run lint'
    },
    {
      type: 'input',
      name: 'typecheckCommand',
      message: 'Type check command (if any):',
      default: 'npm run typecheck'
    },
    {
      type: 'input',
      name: 'runCommand',
      message: 'How to run the application:',
      default: 'npm start'
    },
    {
      type: 'input',
      name: 'techStack',
      message: 'Technology stack (comma-separated):',
      default: 'Node.js, Express'
    },
    {
      type: 'editor',
      name: 'additionalInstructions',
      message: 'Any additional instructions for Claude (press Enter to open editor):'
    }
  ]);
  
  // Create CLAUDE.md content
  let dartSection = '';
  let taskManagementSection = '';
  let documentationRules = '';
  
  if (dartConfig.workspace) {
    dartSection = `
## Dart MCP Tool Configuration

### MANDATORY: Dart MCP Tool Usage
**ALL project management MUST use the Dart MCP tool. This is NOT optional.**

### ${dartConfig.workspace} Project Configuration
1. **Workspace**: ${dartConfig.workspace}
2. **Dartboard**: \`${dartConfig.tasksFolder}\`
3. **Docs Folder**: \`${dartConfig.docsFolder}\`

**IMPORTANT**: Use the full path format (workspace/folder) when calling Dart MCP functions!
`;

    taskManagementSection = `
## Task Management Rules

1. **Always use Dart MCP for tasks** - No exceptions
2. **Valid Task Status Values**:
   - \`To-do\` - For new tasks
   - \`Doing\` - When actively working on a task
   - \`Done\` - When task is completed
3. **Valid Priority Values**:
   - \`Critical\`
   - \`High\`
   - \`Medium\`
   - \`Low\`
4. **When starting work on a task**:
   - Set status to \`Doing\`
   - Use TodoWrite tool in parallel to track subtasks
5. **When updating a task**:
   - NEVER modify the task details/title
   - ONLY add comments to track progress
6. **When completing a task**:
   - Set status to \`Done\`
   - Update TodoWrite tool accordingly
7. **Task creation**:
   - Create tasks in \`${dartConfig.tasksFolder}\` dartboard
   - Include clear descriptions
   - Set appropriate priority
`;

    documentationRules = `
## Documentation Rules

1. **All .md files created locally MUST be duplicated in Dart**
2. **Documentation goes in \`${dartConfig.docsFolder}\` folder**
3. **Keep documentation synchronized**:
   - When creating local .md files, immediately create in Dart
   - When updating local .md files, update Dart version
4. **Documentation structure**:
   - Mirror local folder structure in Dart where possible
   - Use clear, descriptive titles
`;
  }
  
  const claudeMdContent = `# ${projectName} Project Instructions for Claude

## Project Overview
${projectInfo.description}
${dartSection}${taskManagementSection}
## Git Workflow

- Commit messages should be descriptive
- NO co-authored details in commits
- NO 🤖 Generated with Claude Code
- Use conventional commit format when possible
${documentationRules}
## Development Guidelines

### Detail-Oriented Implementation

**BE DETAIL-ORIENTED AND COMPLETE ALL FUNCTIONALITY**

1. **Forms and Data Flow**:
   - When creating forms, ensure ALL collected data is properly saved
   - Track data flow from frontend through APIs to backend
   - Verify that no form fields are being ignored or lost
   - Map form field values correctly to their types

2. **Dynamic Pages and Features**:
   - Implement all promised functionality, not just UI shells
   - Ensure data is properly fetched, displayed, and can be modified
   - Connect all interactive elements to their backend functionality
   - Test the complete user flow, not just individual components

3. **Before Marking Complete**:
   - Verify data persistence (can create, read, update, delete)
   - Check that all form fields are functional
   - Ensure proper error handling
   - Test the complete feature flow end-to-end

### Testing Commands
${projectInfo.testCommand ? `- Test: \`${projectInfo.testCommand}\`` : ''}
${projectInfo.lintCommand ? `- Lint: \`${projectInfo.lintCommand}\`` : ''}
${projectInfo.typecheckCommand ? `- Type check: \`${projectInfo.typecheckCommand}\`` : ''}

## Project-Specific Context

### Technology Stack
${projectInfo.techStack}

### Running the Application
${projectInfo.runCommand ? `\`${projectInfo.runCommand}\`` : 'See project documentation'}

## Important Reminders
- Focus on complete implementation, not partial features
- Always test features end-to-end before marking complete
- Maintain clean, well-documented code
- Follow the project's established patterns and conventions
${dartConfig.workspace ? '\n- Use Dart MCP for ALL task management without exception' : ''}

${projectInfo.additionalInstructions ? `## Additional Instructions\n\n${projectInfo.additionalInstructions}` : ''}

---
*Generated by Claude Hooks Manager on ${new Date().toISOString().split('T')[0]}*
`;
  
  try {
    fs.writeFileSync(claudeMdPath, claudeMdContent);
    console.log(chalk.green('\n✅ Created CLAUDE.md file'));
    console.log(chalk.gray(`Location: ${claudeMdPath}`));
    console.log(chalk.gray('\nClaude will now have project-specific instructions!'));
  } catch (error) {
    console.error(chalk.red('Failed to create CLAUDE.md:'), error.message);
  }
}

async function editDartConfig() {
  const projectRoot = process.cwd();
  const dartFile = path.join(projectRoot, '.dart');
  
  if (!fs.existsSync(dartFile)) {
    console.log(chalk.yellow('\n⚠️  No .dart file found in this project'));
    const { create } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'create',
        message: 'Would you like to create one?',
        default: true
      }
    ]);
    
    if (create) {
      await initDartConfig();
    }
    return;
  }
  
  const editor = process.env.EDITOR || 'nano';
  console.log(chalk.cyan(`\nOpening .dart in ${editor}...`));
  
  try {
    execSync(`${editor} "${dartFile}"`, { stdio: 'inherit' });
    console.log(chalk.green('\n✅ Dart configuration updated'));
  } catch (error) {
    console.error(chalk.red('Failed to open editor:'), error.message);
    console.log(chalk.gray(`You can manually edit: ${dartFile}`));
  }
  
  await promptToContinue();
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