#!/usr/bin/env node

/**
 * Migration script to convert old .disabled hooks to new stub format
 * This prevents "file not found" errors when Claude tries to execute disabled hooks
 */

const fs = require('fs');
const path = require('path');
const chalk = require('chalk');

const hooksDir = path.join(process.env.HOME, '.claude', 'hooks');

console.log(chalk.cyan('\n🔄 Migrating disabled hooks to new format...\n'));

if (!fs.existsSync(hooksDir)) {
  console.log(chalk.yellow('No hooks directory found. Nothing to migrate.'));
  process.exit(0);
}

const files = fs.readdirSync(hooksDir);
const disabledHooks = files.filter(f => f.endsWith('.py.disabled'));

if (disabledHooks.length === 0) {
  console.log(chalk.green('✅ No disabled hooks found to migrate.'));
  process.exit(0);
}

console.log(`Found ${disabledHooks.length} disabled hook(s) to migrate:\n`);

let migrated = 0;
let failed = 0;

for (const file of disabledHooks) {
  const hookName = file.replace('.py.disabled', '');
  const disabledPath = path.join(hooksDir, file);
  const hookPath = path.join(hooksDir, `${hookName}.py`);
  const originalPath = path.join(hooksDir, `${hookName}.py.original`);
  
  console.log(`  • ${hookName}...`);
  
  try {
    // Move .disabled to .original
    fs.renameSync(disabledPath, originalPath);
    
    // Create stub file
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
    
    console.log(chalk.green(`    ✅ Migrated successfully`));
    migrated++;
  } catch (error) {
    console.log(chalk.red(`    ❌ Failed: ${error.message}`));
    failed++;
  }
}

console.log('\n' + chalk.gray('─'.repeat(50)));
console.log(chalk.green(`✅ Successfully migrated: ${migrated}`));
if (failed > 0) {
  console.log(chalk.red(`❌ Failed to migrate: ${failed}`));
}

console.log(chalk.gray('\nDisabled hooks will now exit cleanly without errors.'));
console.log(chalk.gray('Use "claude-hooks enable <hook-name>" to re-enable hooks.\n'));