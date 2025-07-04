# API Reference

Complete API reference for Claude Hooks Manager hook development.

## Hook Interface

### Hook Definition

Every hook must export an object conforming to this interface:

```typescript
interface Hook {
  // Required properties
  name: string;
  description: string;
  type: HookType;
  
  // Optional properties
  version?: string;
  author?: string;
  configSchema?: ConfigSchema;
  defaultConfig?: HookConfig;
  dependencies?: string[];
  
  // Required methods
  run(context: HookContext): Promise<HookResult>;
  
  // Optional methods
  install?(context: InstallContext): Promise<void>;
  uninstall?(context: UninstallContext): Promise<void>;
  validate?(config: HookConfig): ValidationResult;
}
```

### Hook Types

```typescript
type HookType = 
  | 'pre-commit'
  | 'commit-msg'
  | 'pre-push'
  | 'post-commit'
  | 'pre-rebase'
  | 'post-merge'
  | 'post-checkout';
```

## Hook Context

The context object passed to the `run` method:

```typescript
interface HookContext {
  // File information
  files: string[];           // Affected files
  stagedFiles: string[];     // Staged files (pre-commit)
  
  // Configuration
  config: HookConfig;        // Hook-specific config
  globalConfig: GlobalConfig; // Global configuration
  
  // Utilities
  utils: HookUtils;          // Utility functions
  logger: Logger;            // Logging interface
  
  // Git information
  git: GitContext;           // Git-related info
  
  // Environment
  env: ProcessEnv;           // Environment variables
  cwd: string;               // Current working directory
  
  // Hook metadata
  hookName: string;          // Name of current hook
  hookType: HookType;        // Type of current hook
}
```

## Utility Functions

### HookUtils

```typescript
interface HookUtils {
  // File operations
  readFile(path: string): Promise<string>;
  writeFile(path: string, content: string): Promise<void>;
  fileExists(path: string): Promise<boolean>;
  glob(pattern: string, options?: GlobOptions): Promise<string[]>;
  
  // Process execution
  exec(command: string, options?: ExecOptions): Promise<ExecResult>;
  spawn(command: string, args: string[], options?: SpawnOptions): ChildProcess;
  
  // Git operations
  getStagedFiles(): Promise<string[]>;
  getChangedFiles(): Promise<string[]>;
  stageFiles(files: string[]): Promise<void>;
  
  // Formatting
  formatBytes(bytes: number): string;
  formatDuration(ms: number): string;
  
  // Interactive
  prompt(questions: Question[]): Promise<Answers>;
  confirm(message: string): Promise<boolean>;
  
  // Caching
  cache: CacheInterface;
}
```

### Logger

```typescript
interface Logger {
  // Log levels
  debug(message: string, ...args: any[]): void;
  info(message: string, ...args: any[]): void;
  warn(message: string, ...args: any[]): void;
  error(message: string, ...args: any[]): void;
  
  // Formatted output
  success(message: string): void;
  failure(message: string): void;
  
  // Progress
  progress(current: number, total: number, message?: string): void;
  spinner(message: string): Spinner;
  
  // Tables and lists
  table(data: any[], options?: TableOptions): void;
  list(items: string[]): void;
  
  // Grouping
  group(label: string): void;
  groupEnd(): void;
}
```

## Hook Results

### HookResult

```typescript
interface HookResult {
  // Required
  success: boolean;
  
  // Optional
  message?: string;
  details?: string;
  modifiedFiles?: string[];
  warnings?: string[];
  errors?: HookError[];
  
  // Statistics
  stats?: {
    filesProcessed?: number;
    duration?: number;
    [key: string]: any;
  };
}
```

### HookError

```typescript
interface HookError {
  file?: string;
  line?: number;
  column?: number;
  message: string;
  severity?: 'error' | 'warning' | 'info';
  rule?: string;
}
```

## Configuration

### ConfigSchema

Define configuration options for your hook:

```typescript
interface ConfigSchema {
  [key: string]: {
    type: 'string' | 'number' | 'boolean' | 'array' | 'object';
    default?: any;
    required?: boolean;
    description?: string;
    enum?: any[];
    minimum?: number;
    maximum?: number;
    pattern?: string;
  };
}
```

Example:
```javascript
const configSchema = {
  extensions: {
    type: 'array',
    default: ['js', 'jsx', 'ts', 'tsx'],
    description: 'File extensions to process'
  },
  maxWarnings: {
    type: 'number',
    default: 10,
    minimum: 0,
    description: 'Maximum number of warnings allowed'
  },
  autoFix: {
    type: 'boolean',
    default: false,
    description: 'Automatically fix issues'
  }
};
```

## Git Context

### GitContext

```typescript
interface GitContext {
  // Repository info
  rootDir: string;
  branch: string;
  remotes: Remote[];
  
  // Commit info
  lastCommit: CommitInfo;
  commitMessage?: string;  // For commit-msg hooks
  
  // Methods
  getFileStatus(file: string): Promise<FileStatus>;
  getDiff(file?: string): Promise<string>;
  getBlame(file: string, line: number): Promise<BlameInfo>;
}
```

## Example Implementations

### Basic Pre-commit Hook

```javascript
module.exports = {
  name: 'example-hook',
  description: 'An example pre-commit hook',
  type: 'pre-commit',
  
  defaultConfig: {
    checkTodos: true,
    maxTodos: 10
  },
  
  async run(context) {
    const { files, config, utils, logger } = context;
    
    logger.info('Checking files...');
    
    let todoCount = 0;
    const errors = [];
    
    for (const file of files) {
      if (!file.endsWith('.js')) continue;
      
      const content = await utils.readFile(file);
      const lines = content.split('\n');
      
      lines.forEach((line, index) => {
        if (line.includes('TODO')) {
          todoCount++;
          if (config.checkTodos) {
            errors.push({
              file,
              line: index + 1,
              message: 'Found TODO comment'
            });
          }
        }
      });
    }
    
    if (todoCount > config.maxTodos) {
      return {
        success: false,
        message: `Too many TODOs (${todoCount}/${config.maxTodos})`,
        errors
      };
    }
    
    return {
      success: true,
      message: `Check complete (${todoCount} TODOs found)`,
      stats: { todoCount }
    };
  }
};
```

### Advanced Hook with Utilities

```javascript
module.exports = {
  name: 'advanced-hook',
  description: 'Advanced hook example',
  type: 'pre-commit',
  
  configSchema: {
    prettier: {
      type: 'boolean',
      default: true,
      description: 'Run prettier'
    },
    eslint: {
      type: 'boolean',
      default: true,
      description: 'Run eslint'
    }
  },
  
  async run(context) {
    const { stagedFiles, config, utils, logger } = context;
    
    // Filter JavaScript files
    const jsFiles = stagedFiles.filter(f => /\.[jt]sx?$/.test(f));
    
    if (jsFiles.length === 0) {
      return { success: true, message: 'No JavaScript files to check' };
    }
    
    const spinner = logger.spinner('Running checks...');
    
    try {
      // Run prettier
      if (config.prettier) {
        spinner.text = 'Running prettier...';
        const result = await utils.exec(`npx prettier --check ${jsFiles.join(' ')}`);
        
        if (result.exitCode !== 0) {
          spinner.fail('Prettier check failed');
          
          // Offer to fix
          const fix = await utils.confirm('Would you like to fix formatting issues?');
          if (fix) {
            await utils.exec(`npx prettier --write ${jsFiles.join(' ')}`);
            await utils.stageFiles(jsFiles);
            spinner.succeed('Files formatted and staged');
          } else {
            return {
              success: false,
              message: 'Formatting issues found',
              details: result.stderr
            };
          }
        }
      }
      
      // Run ESLint
      if (config.eslint) {
        spinner.text = 'Running ESLint...';
        const result = await utils.exec(`npx eslint ${jsFiles.join(' ')}`);
        
        if (result.exitCode !== 0) {
          spinner.fail('ESLint check failed');
          return {
            success: false,
            message: 'Linting errors found',
            details: result.stdout
          };
        }
      }
      
      spinner.succeed('All checks passed');
      
      return {
        success: true,
        message: 'Code quality checks passed',
        stats: {
          filesChecked: jsFiles.length
        }
      };
      
    } catch (error) {
      spinner.fail('Check failed');
      throw error;
    }
  }
};
```

### Commit Message Hook

```javascript
module.exports = {
  name: 'commit-msg-validator',
  description: 'Validates commit message format',
  type: 'commit-msg',
  
  configSchema: {
    pattern: {
      type: 'string',
      default: '^(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?: .+',
      description: 'Regex pattern for commit message'
    },
    maxLength: {
      type: 'number',
      default: 72,
      description: 'Maximum length of commit message'
    }
  },
  
  async run(context) {
    const { git, config, utils, logger } = context;
    
    const message = git.commitMessage;
    
    // Check pattern
    const regex = new RegExp(config.pattern);
    if (!regex.test(message)) {
      logger.error('Invalid commit message format');
      logger.info('Expected format: type(scope): subject');
      logger.info('Example: feat(api): add user authentication');
      
      return {
        success: false,
        message: 'Commit message does not match required format',
        details: `Pattern: ${config.pattern}`
      };
    }
    
    // Check length
    const firstLine = message.split('\n')[0];
    if (firstLine.length > config.maxLength) {
      return {
        success: false,
        message: `Commit message too long (${firstLine.length}/${config.maxLength} characters)`
      };
    }
    
    logger.success('Commit message validated');
    
    return {
      success: true,
      message: 'Commit message is valid'
    };
  }
};
```

## Cache Interface

```typescript
interface CacheInterface {
  // Get/Set
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T, ttl?: number): Promise<void>;
  
  // Check existence
  has(key: string): Promise<boolean>;
  
  // Delete
  delete(key: string): Promise<void>;
  clear(): Promise<void>;
  
  // File-based caching
  getFileCache(file: string): Promise<FileCacheEntry | null>;
  setFileCache(file: string, data: any): Promise<void>;
}

interface FileCacheEntry {
  data: any;
  mtime: number;
  hash: string;
}
```

## Testing Hooks

### Test Utilities

```javascript
const { createTestContext } = require('claude-hooks-manager/test-utils');

describe('my-hook', () => {
  it('should process files correctly', async () => {
    const context = createTestContext({
      files: ['test.js'],
      config: { myOption: true }
    });
    
    const result = await myHook.run(context);
    
    expect(result.success).toBe(true);
  });
});
```

### Mock Context

```javascript
const mockContext = {
  files: ['src/index.js', 'src/utils.js'],
  config: { autoFix: true },
  utils: {
    readFile: jest.fn().mockResolvedValue('file content'),
    exec: jest.fn().mockResolvedValue({ exitCode: 0, stdout: '' })
  },
  logger: {
    info: jest.fn(),
    error: jest.fn()
  }
};
```

## Error Handling

### Best Practices

```javascript
async run(context) {
  try {
    // Main logic
  } catch (error) {
    // Log detailed error for debugging
    context.logger.debug('Stack trace:', error.stack);
    
    // Return user-friendly error
    return {
      success: false,
      message: 'Hook failed: ' + error.message,
      details: process.env.DEBUG ? error.stack : undefined
    };
  }
}
```

### Custom Errors

```javascript
class HookError extends Error {
  constructor(message, code, details) {
    super(message);
    this.name = 'HookError';
    this.code = code;
    this.details = details;
  }
}

// Usage
throw new HookError(
  'Configuration invalid',
  'INVALID_CONFIG',
  { missing: ['required-field'] }
);
```

## Performance Considerations

### Parallel Processing

```javascript
async run(context) {
  const { files, utils } = context;
  
  // Process files in parallel
  const results = await Promise.all(
    files.map(file => processFile(file))
  );
  
  // Or with concurrency limit
  const { default: pLimit } = await import('p-limit');
  const limit = pLimit(5); // Max 5 concurrent
  
  const results = await Promise.all(
    files.map(file => limit(() => processFile(file)))
  );
}
```

### Progress Reporting

```javascript
async run(context) {
  const { files, logger } = context;
  
  for (let i = 0; i < files.length; i++) {
    logger.progress(i + 1, files.length, `Processing ${files[i]}`);
    await processFile(files[i]);
  }
}
```

---

[← Contributing](Contributing.md) | [Home](Home.md)