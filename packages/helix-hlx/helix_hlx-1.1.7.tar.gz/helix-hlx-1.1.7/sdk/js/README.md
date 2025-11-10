# Helix JavaScript SDK

![Helix Language](https://img.shields.io/badge/Helix-Language-blue)
![JavaScript](https://img.shields.io/badge/JavaScript-Node.js-yellow)
![npm](https://img.shields.io/badge/npm-Ready-red)
![Native](https://img.shields.io/badge/Native-Rust%20%2B%20napi--rs-green)
![License](https://img.shields.io/badge/License-MIT-blue)

**Native Node.js CLI** and **SDK** for the **Helix Configuration Language** - **blazingly fast** performance with **zero dependencies** for end users.

**Important**: Helix is **NOT** JSON - it uses its own syntax with `:` and `;` for blocks, or `{` and `}` for named blocks (project/agent/workflow). See syntax examples below.

## 🚀 Features

- **🔥 Native Performance**: Compiled Rust backend with napi-rs bindings
- **📦 Zero Dependencies**: No Rust toolchain required for end users
- **🌍 Cross-Platform**: Universal binaries for Windows, macOS, and Linux
- **⚡ TypeScript Support**: Full type definitions and static analysis
- **🛡️ Memory Safe**: Rust guarantees prevent memory issues
- **🔧 Production Ready**: Enterprise-grade error handling and validation
- **🎯 Complete CLI**: 27+ commands mirroring the Rust `hlx` binary
- **📚 Full API**: High-level JavaScript API for programmatic use

## 📦 Installation

### From npm (Recommended)
```bash
npm install -g helix-hlx
```

### Local Installation (Project Dependency)
```bash
npm install helix-hlx
```

### From Source (Development)
```bash
# Clone the repository
git clone https://github.com/cyber-boost/helix.git
cd helix/sdk/js

# Install dependencies
npm install

# Build native bindings and CLI
npm run build

# Install globally (optional)
npm install -g .
```

## 🔧 Quick Start

**Important**: Helix files use their own syntax (NOT JSON):
- Blocks use `:` and `;` delimiters (e.g., `server : port = 8080 ;`)
- Named blocks can use `{ }` syntax (e.g., `project "name" { ... }`)
- See examples below for proper syntax

### Using the CLI

The Helix CLI (`hlx`) provides a complete command-line interface for working with Helix configurations.

```bash
# Check version
hlx --version

# Initialize a new project
hlx init --name my-project

# Compile Helix files
hlx compile --input src --output dist

# Format code
hlx fmt

# Lint code
hlx lint

# Run tests
hlx test

# Show project info
hlx info --format json

# Parse and validate
hlx validate config.hlx

# Execute Helix expressions
hlx execute "@database.host"

# Launch interactive TUI
hlx tui

# See all available commands
hlx --help
```

### Available Commands (32/33)

**Core Commands:**
- `add` - Add dependencies or files
- `compile`, `build` - Compile Helix project
- `validate` - Validate configuration files
- `parse` - Parse Helix source code
- `execute` - Execute Helix expressions
- `load` - Load configuration from file
- `init` - Initialize new project
- `info` - Show project information

**Development:**
- `fmt` - Format code
- `lint` - Lint code
- `test` - Run tests
- `bench` - Run benchmarks
- `watch` - Watch for file changes
- `serve` - Start development server

**Build & Deploy:**
- `bundle` - Bundle project files
- `optimize` - Optimize code
- `export` - Export project
- `sign` - Sign binaries

**Utilities:**
- `clean` - Clean build artifacts
- `diff` - Show differences
- `search` - Search operations
- `schema` - Generate schemas
- `generate` - Generate code
- `dataset` - Process datasets
- `filter` - Filter operations
- `remove` - Remove files
- `reset` - Reset project
- `import` - Import dependencies

**Terminal UI:**
- `tui` - Launch the interactive Terminal User Interface

**Shell & Utilities:**
- `completions` - Generate shell completions (bash, zsh, fish, powershell)
- `doctor` - Run diagnostics
- `publish` - Publish packages with multiple actions (publish, sign, export)
- `vlt` - Vault version control (new, open, list, save, history, revert, diff, config, gc, tui)

**Pending Implementation:**
- `workflow` - Workflow management

### Using the JavaScript API

```javascript
const { HelixConfig, parse } = require('helix-hlx');

// Create a configuration object
const config = new HelixConfig();

// Set values
config.set('database.host', 'localhost');
config.set('database.port', 5432);
config.set('features', ['auth', 'caching', 'logging']);

// Get values
const host = config.get('database.host');
const port = config.get('database.port') || 3306; // with default
const features = config.get('features') || [];

console.log(`Database: ${host}:${port}`);
console.log(`Features: ${features.join(', ')}`);
```

### Parsing Helix Source Code
```javascript
const { parse } = require('helix-hlx');

// Parse Helix configuration from string
// Note: Helix is NOT JSON - it uses ':' and ';' for blocks, or '{' and '}' for named blocks
// Example 1: Using ':' and ';' syntax
const source = `
database :
    host = "production-db.example.com"
    port = 5432
    credentials :
        username = "admin"
        password = "secret"
    ;
;

features = ["auth", "caching", "metrics"]
debug = false
`;

// Example 2: Alternative syntax with '{' and '}' (for named blocks like project/agent/workflow)
const source2 = `
project "MyApp" {
    version = "1.0.0"
}

server {
    port = 8080
}
`;

const config = parse(source);

// Access parsed values
const dbHost = config.get('database.host');
const dbPort = config.get('database.port');
const username = config.get('database.credentials.username');
```

### Loading from Files
```javascript
const { HelixConfig } = require('helix-hlx');

// Load configuration from a .hlx file
const config = new HelixConfig();
config.loadFile('config.hlx');

// Access configuration values
const appName = config.get('app.name');
const version = config.get('app.version');
```

### Direct Expression Execution
```javascript
const { execute } = require('helix-hlx');

// Execute Helix expressions with context
const context = {
    user: { id: 12345, name: 'John Doe' },
    permissions: ['read', 'write'],
    settings: { maxConnections: 100 }
};

async function runExample() {
    // Execute expressions
    const result = await execute('@user.id == 12345', context);
    const maxConn = await execute('@settings.maxConnections', context);

    console.log(`User authorized: ${result}`);
    console.log(`Max connections: ${maxConn}`);
}

runExample();
```

## 🎯 CLI Usage Examples

### Project Management
```bash
# Initialize a new Helix project
hlx init --name my-app --template minimal

# Add a dependency
hlx add my-dependency@1.0.0

# Build the project
hlx compile --input src --output dist --optimize 3

# Format all files
hlx fmt

# Check formatting without changes
hlx fmt --check

# Lint the project
hlx lint

# Lint specific files
hlx lint src/config.hlx src/app.hlx
```

### Development Workflow
```bash
# Watch for changes and auto-compile
hlx watch --input src --output dist --optimize 2

# Start development server
hlx serve --port 8080

# Run tests
hlx test

# Run benchmarks
hlx bench --pattern "parse*" --iterations 1000
```

### Code Generation & Utilities
```bash
# Generate code from template
hlx generate my-template --output generated/ --force

# Generate schema
hlx schema config.hlx --lang typescript --output types.ts

# Show differences between files
hlx diff file1.hlx file2.hlx --detailed

# Search in project
hlx search "database" --type semantic --limit 10

# Export project
hlx export --format json --output export.json --include-deps
```

### File Operations
```bash
# Parse Helix code from command line
hlx parse 'database { host = "localhost" }'

# Execute expressions
hlx execute "@database.host"

# Validate configuration
hlx validate config.hlx

# Clean build artifacts
hlx clean --all

# Remove files
hlx remove old-file.hlx deprecated.hlx

# Launch interactive TUI for vault management
hlx tui
```

### Shell Completions
```bash
# Generate completions for your shell
hlx completions bash > ~/.local/share/bash-completion/completions/hlx
hlx completions zsh > ~/.zsh_completions/_hlx
hlx completions fish > ~/.config/fish/completions/hlx.fish

# Source in your shell config
# For bash: source ~/.local/share/bash-completion/completions/hlx
# For zsh: fpath=(~/.zsh_completions $fpath) && autoload -U compinit && compinit
# For fish: completions are auto-loaded
```

### Vault Operations
```bash
# List all files in vault
hlx vlt list
hlx vlt list --long

# Save file to vault
hlx vlt save config.hlx --description "Updated config"

# View version history
hlx vlt history config.hlx
hlx vlt history config.hlx --limit 20 --long

# Revert to previous version
hlx vlt revert config.hlx <version-id> --force

# Show differences between versions
hlx vlt diff config.hlx --from v1 --to v2

# Manage vault configuration
hlx vlt config --show
hlx vlt config --compress true --retention-days 30

# Garbage collection
hlx vlt gc --dry-run
hlx vlt gc --force
```

### Publishing
```bash
# Publish project
hlx publish --action publish --registry my-registry --token <token>

# Dry run (test without publishing)
hlx publish --action publish --dry-run --verbose

# Sign binary
hlx publish --action sign --input binary.hlxb --key <key> --output signed.hlxb

# Verify signature
hlx publish --action sign --input signed.hlxb --verify

# Export project
hlx publish --action export --format json --output export.json --include-deps
hlx publish --action export --format docker --output Dockerfile
hlx publish --action export --format k8s --output k8s.yaml
```

## 🏗️ JavaScript API Reference

### HelixConfig Class

The main interface for working with Helix configurations.

#### Constructor
```javascript
new HelixConfig(data?: object | string)
```

#### Methods
- `get(key: string): any`: Get a configuration value
- `set(key: string, value: any): void`: Set a configuration value
- `has(key: string): boolean`: Check if a key exists
- `delete(key: string): boolean`: Delete a key
- `keys(): string[]`: Get all keys
- `entries(): [string, any][]`: Get all key-value pairs
- `size(): number`: Get configuration size
- `clear(): void`: Clear all configuration
- `toObject(): object`: Convert to plain JavaScript object
- `execute(expression: string): Promise<any>`: Execute a Helix expression
- `toJSON(): string`: Convert to JSON string
- `toString(): string`: String representation

### Utility Functions

#### `parse(source: string): HelixConfig`
Parse Helix source code into a configuration object.

#### `execute(expression: string, context?: object): Promise<any>`
Execute a Helix expression with optional context.

#### `loadFile(filePath: string): HelixConfig`
Load a Helix configuration from a file.

#### `createContext(options?: ExecutionContext): ExecutionContext`
Create a new execution context.

#### `createRegistry(context?: ExecutionContext): OperatorRegistry`
Create a new operator registry.

## 🎯 Advanced Usage

### Working with Complex Data Types

```javascript
const { HelixConfig } = require('helix-hlx');

const config = new HelixConfig();

// Set complex nested structures
config.set('servers', [
    { host: 'server1.example.com', port: 8080 },
    { host: 'server2.example.com', port: 8081 }
]);

config.set('database', {
    host: 'localhost',
    port: 5432,
    credentials: {
        username: 'admin',
        password: 'secret123'
    }
});

// Access nested values
const servers = config.get('servers');
const server1Host = servers[0].host;
const dbHost = config.get('database.host');
const username = config.get('database.credentials.username');
```

### Custom Context for Execution

```javascript
const { execute } = require('helix-hlx');

// Create context with custom variables
const context = {
    user: { id: 12345, name: 'John Doe' },
    permissions: ['read', 'write'],
    settings: { maxConnections: 100 }
};

async function runAdvancedExample() {
    // Execute expressions with context
    const userId = await execute('@user.id', context);
    const hasPermission = await execute('@user.id in permissions', context);
    const maxConn = await execute('@settings.maxConnections', context);

    console.log(`User ID: ${userId}`);
    console.log(`Has permission: ${hasPermission}`);
    console.log(`Max connections: ${maxConn}`);
}
```

### Error Handling

```javascript
const { HelixConfig, ParseError, ValidationError } = require('helix-hlx');

try {
    const config = parse('invalid helix syntax {');
} catch (error) {
    if (error instanceof ParseError) {
        console.log(`Parse error at line ${error.line}, column ${error.column}: ${error.message}`);
    } else {
        console.log(`Error: ${error.message}`);
    }
}

try {
    const result = config.get('nonexistent.key');
} catch (error) {
    console.log(`Configuration error: ${error.message}`);
}

// Safe access with defaults
const value = config.get('maybe.key') || 'default_value';
```

## 🧪 Testing

### Unit Tests
```bash
# Run JavaScript tests
npm test

# Run specific test file
npx ava tests/config.test.js

# Run with coverage
npm run test:coverage
```

### Integration Tests
```javascript
const { HelixConfig, parse, execute } = require('helix-hlx');

describe('HelixConfig', () => {
    test('should create empty config', () => {
        const config = new HelixConfig();
        expect(config.size()).toBe(0);
    });

    test('should parse Helix source', () => {
        const source = 'key = "value"';
        const config = parse(source);
        expect(config.get('key')).toBe('value');
    });

    test('should execute expressions', async () => {
        const context = { a: 10, b: 20 };
        const result = await execute('a + b', context);
        expect(result).toBe(30);
    });
});
```

## 🔧 Development

### Prerequisites
- Node.js 10+
- Rust toolchain (for development builds)
- npm or yarn

### Development Build
```bash
# Install dependencies
npm install

# Build in debug mode
npm run build:debug

# Build in release mode
npm run build

# Build for all platforms
npm run universal
```

### Project Structure
```
sdk/js/
├── src/
│   ├── api.ts          # High-level JavaScript API
│   ├── types.ts        # TypeScript definitions
│   └── errors.ts       # Error handling
├── cli.ts              # CLI implementation (compiles to cli.js)
├── index.js            # Native addon loader
├── index.d.ts          # TypeScript definitions
├── index.ts            # Main export file
├── package.json        # npm configuration
├── tsconfig.json       # TypeScript configuration
├── *.node              # Native binaries (platform-specific)
└── README.md           # This file
```

### Adding New CLI Commands

1. **Add Rust napi binding** in `src/dna/ngs/javascript.rs`:
   ```rust
   #[cfg(feature = "js")]
   #[napi]
   pub fn cmd_newcommand(...) -> JsResult<String> {
       // Implementation
   }
   ```

2. **Add handler in `cli.ts`**:
   ```typescript
   async function handleNewCommand(args: string[], options: CliOptions) {
       // Parse arguments and call nativeBinding.cmdNewcommand(...)
   }
   ```

3. **Wire up in main switch statement**:
   ```typescript
   case 'newcommand':
       await handleNewCommand(args, options);
       break;
   ```

### Adding New API Features

1. **Add Rust implementation** in `src/dna/ngs/javascript.rs`
2. **Update TypeScript types** in `src/types.ts` or `index.d.ts`
3. **Add JavaScript API** in `src/api.ts`
4. **Write tests** in `tests/`
5. **Update documentation**

## 📋 Configuration Examples

### Application Configuration
```javascript
const { parse } = require('helix-hlx');

// Helix syntax uses ':' and ';' for block definitions
const source = `
app :
    name = "MyApp"
    version = "1.0.0"
    environment = "production"
;

database :
    host = "db.example.com"
    port = 5432
    name = "myapp_db"
;

redis :
    host = "redis.example.com"
    port = 6379
;

features = ["auth", "caching", "metrics"]
debug = false
`;

const config = parse(source);

// Access configuration
const appName = config.get('app.name');
const dbHost = config.get('database.host');
const features = config.get('features');
```

### Environment-Based Configuration
```javascript
const { HelixConfig } = require('helix-hlx');
const config = new HelixConfig();

// Load configuration based on environment
// Helix files use ':' and ';' or '{' and '}' for blocks
const env = process.env.NODE_ENV || 'development';
config.loadFile(`config.${env}.hlx`);

// Override with environment variables
config.set('database.host', process.env.DB_HOST || config.get('database.host'));
config.set('database.port', parseInt(process.env.DB_PORT) || config.get('database.port'));
```

### Feature Flags
```javascript
const { execute } = require('helix-hlx');

const context = {
    user: { id: 12345, role: 'admin' },
    features: {
        auth: true,
        caching: true,
        metrics: false,
        experimental: { enabled: true, percentage: 10 }
    }
};

async function checkFeatureAccess() {
    const canAccessFeature = await execute('@features.auth == true', context);
    const isInPercentage = await execute('@user.id % 100 < @features.experimental.percentage', context);

    return canAccessFeature && isInPercentage;
}
```

## 🚀 Performance Tips

### Caching Configuration Objects
```javascript
const configCache = new Map();

function getConfig(env) {
    if (!configCache.has(env)) {
        configCache.set(env, parseFile(`config.${env}.hlx`));
    }
    return configCache.get(env);
}
```

### Batch Operations
```javascript
// Better: batch multiple operations
const config = new HelixConfig();
const batchData = {
    'key1': 'value1',
    'key2': 'value2',
    'key3': 'value3'
};

Object.entries(batchData).forEach(([key, value]) => {
    config.set(key, value);
});

// Avoid: individual operations (creates intermediate objects)
```

### Expression Optimization
```javascript
// Pre-compile frequently used expressions
const frequentlyUsed = {
    userAuthorized: '@user.id == 12345',
    hasPermission: '@user.permissions.contains("admin")',
    debugEnabled: '@config.debug == true'
};

async function batchExecute(expressions, context) {
    const results = {};
    for (const [name, expr] of Object.entries(expressions)) {
        results[name] = await execute(expr, context);
    }
    return results;
}
```

## 🐛 Troubleshooting

### Common Issues

#### Error: Cannot find module 'helix-hlx' or command not found
```bash
# Install globally
npm install -g helix-hlx

# Or install locally in your project
npm install helix-hlx

# For development builds
cd helix/sdk/js
npm install
npm run build
npm install -g .
```

#### Error: Module did not self-register
```bash
# The native addon wasn't built correctly
npm run build

# Or rebuild for your specific platform
npm run build:debug
```

#### TypeScript errors
```bash
# Make sure TypeScript definitions are correct
npm run typecheck

# Regenerate types if needed
npm run build
```

### Debug Mode
```javascript
const { HelixConfig } = require('helix-hlx');

// Enable debug logging
process.env.DEBUG = 'helix:*';

const config = new HelixConfig();
config.set('debug', true);
```

### Performance Profiling
```javascript
const { execute } = require('helix-hlx');

console.time('helix-execution');
const result = await execute('@database.port + 1000');
console.timeEnd('helix-execution');

console.time('config-access');
const value = config.get('database.host');
console.timeEnd('config-access');
```

## 🖥️ Terminal User Interface (TUI)

The Helix TUI provides an interactive terminal-based interface for managing Helix configurations and vaults.

### Launching the TUI
```bash
hlx tui
```

### TUI Features

The TUI includes several panels:

- **Files Panel (Ctrl+1)**: Browse and select vault files
- **Tabs Panel (Ctrl+2)**: Manage multiple open documents
- **Editor Panel (Ctrl+3)**: Edit Helix configuration files
- **Operators Panel (Ctrl+4)**: Browse and insert Helix operators
- **Commands Panel (Ctrl+5)**: Quick command shortcuts
- **Terminal Log (Ctrl+6)**: View activity logs
- **Status Bar (Ctrl+7)**: Current focus and document state

### Keyboard Shortcuts

**Navigation:**
- `Ctrl+1-7`: Switch between panels
- `↑/↓`: Navigate lists
- `Enter`: Select/open item
- `Ctrl+N`: Create new tab
- `Ctrl+T`: Next tab
- `Ctrl+X`: Close tab

**Operators:**
- `Ctrl+A/B`: Cycle operator categories
- `Ctrl+C`: Reset to first category
- `Ctrl+Y`: Insert selected operator

**Actions:**
- `Ctrl+S`: Save current tab
- `Ctrl+Q`: Quit TUI

### TUI Usage Example

```bash
# Start the TUI
hlx tui

# Use Ctrl+1 to focus on Files panel
# Navigate with arrow keys, press Enter to open a file
# Edit in the Editor panel (Ctrl+3)
# Insert operators from the Operators panel (Ctrl+4)
# Save with Ctrl+S
# Exit with Ctrl+Q
```

## 📚 Examples

### Complete Application Example
```javascript
const { HelixConfig, parse, execute } = require('helix-hlx');

class AppConfig {
    constructor() {
        // Load configuration
        const env = process.env.NODE_ENV || 'development';
        this.config = parseFile(`config.${env}.hlx`);

        // Override with environment variables
        this.config.set('database.host', process.env.DB_HOST || this.config.get('database.host'));
        this.config.set('database.port', parseInt(process.env.DB_PORT) || this.config.get('database.port'));
    }

    getDbConnectionString() {
        const host = this.config.get('database.host');
        const port = this.config.get('database.port');
        const database = this.config.get('database.name');
        return `postgresql://${host}:${port}/${database}`;
    }

    isFeatureEnabled(feature) {
        const features = this.config.get('features') || [];
        return features.includes(feature);
    }

    getSetting(key, defaultValue = null) {
        return this.config.get(key) ?? defaultValue;
    }

    async validateUser(userId) {
        const context = { user: { id: userId } };
        return await execute('@user.id > 0 && @user.id < 1000000', context);
    }
}

// Usage
const appConfig = new AppConfig();
console.log(appConfig.getDbConnectionString());
console.log(appConfig.isFeatureEnabled('caching'));
console.log(appConfig.getSetting('app.version', '1.0.0'));

// Async validation
appConfig.validateUser(12345).then(valid => {
    console.log(`User is ${valid ? 'valid' : 'invalid'}`);
});
```

### Express.js Middleware
```javascript
const { parse } = require('helix-hlx');

function helixConfigMiddleware(configPath) {
    return (req, res, next) => {
        try {
            req.helixConfig = parseFile(configPath);
            next();
        } catch (error) {
            next(error);
        }
    };
}

// Usage in Express app
app.use('/api', helixConfigMiddleware('api-config.hlx'));
```

## 🔗 Links

- [Helix Language Documentation](https://github.com/cyber-boost/helix)
- [napi-rs Documentation](https://napi.rs/)
- [Node.js Native Addons](https://nodejs.org/api/addons.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please see the main Helix repository for contribution guidelines.

---

**Made with ❤️ by the Helix Team**
