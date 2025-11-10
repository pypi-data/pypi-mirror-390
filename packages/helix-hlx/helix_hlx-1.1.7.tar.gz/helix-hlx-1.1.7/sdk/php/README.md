# Helix Language PHP SDK

[![PHP Version](https://img.shields.io/badge/php-%3E%3D7.4-blue.svg)](https://php.net)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.7-blue.svg)](https://github.com/helix-lang/php)

The **Helix Language PHP SDK** provides native PHP bindings for the Helix Configuration Language, powered by a high-performance Rust implementation using **FFI (Foreign Function Interface)** with the [FFI extension](https://php.net/ffi).

## 🚀 Features

- **Native Performance**: Built on Rust with high-performance FFI bindings
- **Full Language Support**: Complete Helix language interpreter and runtime
- **PHP-Native API**: Fluent, intuitive PHP interfaces with object-oriented design
- **Type Safety**: Strong typing with PHP 8+ support
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **No Extension Compilation**: Uses PHP's built-in FFI extension (PHP 7.4+)
- **Memory Efficient**: Zero-copy operations where possible
- **Production Ready**: Comprehensive error handling and validation

## 📦 Installation

### Prerequisites

- **PHP 7.4+** with FFI extension enabled
- **Composer** for dependency management

### Option 1: Composer (Recommended)

```bash
composer require helix/lang
```

### Option 2: Manual Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/helix-lang/php.git
   cd php
   ```

2. **Install dependencies**
   ```bash
   composer install
   ```

3. **Build the SDK**
   ```bash
   php build.php --install
   ```

4. **Verify installation**
   ```bash
   php test_ffi.php
   ```

### Enable FFI Extension

Make sure the FFI extension is enabled in your `php.ini`:

```ini
extension=ffi
```

Or install the FFI extension if not available:

```bash
# Ubuntu/Debian
sudo apt install php-ffi

# macOS with Homebrew
brew install php-ffi

# Windows: Enable in php.ini
```

## 🔧 Configuration

### Basic Setup

```php
<?php

require_once 'vendor/autoload.php';

// Create a Helix instance
$helix = new Helix\\Helix();

// Or use the global functions
$result = helix_execute('@env("HOME")');
echo $result;
```

### Configuration

```php
<?php

use Helix\\Helix;
use Helix\\Config;
use Helix\\Interpreter;

// Create a new Helix instance
$helix = Helix::create();

// Configure the execution context
$helix->context()
    ->setRequest('GET', '/api/data')
    ->setSession(['user_id' => 123])
    ->setParam('limit', '10');

// Set configuration values
$helix->config()
    ->set('database.host', 'localhost')
    ->set('database.port', 5432)
    ->set('api.key', 'your-api-key');

// Save configuration to file
$helix->config()->save('/path/to/config.json');
```

## 📚 Usage Examples

### Basic Execution

```php
<?php

use Helix\\Helix;

$helix = Helix::create();

// Execute simple expressions
$result = $helix->execute('@math("2 + 3 * 4")');
echo $result; // Output: 14

// Execute with variables
$result = $helix->execute('@var("x", 42) @var("y", 8) @math("$x + $y")');
echo $result; // Output: 50

// Load and execute a file
$result = $helix->loadFile('/path/to/template.hlx');
```

### Configuration Management

```php
<?php

use Helix\\Config;

$config = Config::create();

// Set values
$config->set('app.name', 'My Application');
$config->set('database.host', 'localhost');
$config->set('database.port', 5432);

// Type-safe getters
$name = $config->getString('app.name');
$port = $config->getInt('database.port', 3306);
$debug = $config->getBool('app.debug', false);

// Array access
$items = $config->toArray();

// Load from file
$config->load('/path/to/config.json');
```

### Advanced Execution

```php
<?php

use Helix\\Helix;
use Helix\\ExecutionContext;

$helix = Helix::create();

// Create custom execution context
$context = ExecutionContext::create()
    ->setRequest('POST', '/api/users', ['Content-Type' => 'application/json'], '{"name":"John"}')
    ->setSession(['user_id' => 123, 'role' => 'admin'])
    ->setParam('id', '456')
    ->setCookie('session_token', 'abc123');

// Execute with context
$result = $helix->interpreter()->executeWithContext('@json()', $context);
```

### Template Processing

```php
<?php

use Helix\\Helix;

$helix = Helix::create();

// Load a template with variables
$template = $helix->loadTemplate('/path/to/template.hlx', [
    'title' => 'Welcome',
    'user' => 'John Doe',
    'items' => ['apple', 'banana', 'orange']
]);

echo $template;
```

## 🔍 API Reference

### Helix Class

The main entry point for the Helix SDK.

#### Methods

- `Helix::create()`: Create a new Helix instance
- `execute(string $code)`: Execute Helix code
- `parse(string $code)`: Parse Helix code to AST
- `loadFile(string $filePath)`: Load and execute a file
- `config()`: Get the configuration instance
- `interpreter()`: Get the interpreter instance
- `context()`: Get the execution context instance

### Config Class

Manages configuration values with type-safe access.

#### Methods

- `set(string $key, $value)`: Set a configuration value
- `get(string $key, $default = null)`: Get a configuration value
- `has(string $key)`: Check if a key exists
- `delete(string $key)`: Remove a key
- `clear()`: Clear all values
- `keys()`: Get all keys
- `values()`: Get all values
- `items()`: Get all key-value pairs
- `load(string $filePath)`: Load from file
- `save(string $filePath)`: Save to file
- `toArray()`: Convert to array

#### Type-safe getters

- `getString(string $key, string $default = '')`: Get as string
- `getInt(string $key, int $default = 0)`: Get as integer
- `getFloat(string $key, float $default = 0.0)`: Get as float
- `getBool(string $key, bool $default = false)`: Get as boolean
- `getArray(string $key, array $default = [])`: Get as array

### Interpreter Class

Provides access to the Helix interpreter.

#### Methods

- `parse(string $code)`: Parse code to AST representation
- `execute(string $code)`: Execute code
- `loadFile(string $filePath)`: Load and execute a file
- `executeWithContext(string $code, ExecutionContext $context)`: Execute with context
- `evaluate(string $expression)`: Evaluate a simple expression
- `validate(string $code)`: Validate syntax

### ExecutionContext Class

Configures the execution environment.

#### Methods

- `setRequest(string $method, string $url, array $headers = [], string $body = '')`: Set request data
- `setSession(array $data)`: Set session data
- `setSessionVar(string $key, $value)`: Set a session variable
- `setCookies(array $cookies)`: Set cookies
- `setParams(array $params)`: Set URL parameters
- `setQuery(array $query)`: Set query parameters

### Global Functions

- `helix_parse(string $code)`: Parse Helix code
- `helix_execute(string $code)`: Execute Helix code
- `helix_load_file(string $filePath)`: Load and execute a file

## 🧪 Testing

Run the test suite:

```bash
# Using Composer
composer test

# Using PHPUnit directly
./vendor/bin/phpunit

# Using the provided test script
php tests/run-tests.php
```

### Writing Tests

```php
<?php

use PHPUnit\\Framework\\TestCase;
use Helix\\Helix;

class HelixTest extends TestCase
{
    public function testBasicExecution()
    {
        $helix = Helix::create();
        $result = $helix->execute('@math("1 + 1")');

        $this->assertEquals(2, $result);
    }

    public function testConfiguration()
    {
        $config = new Helix\\Config();
        $config->set('test.key', 'value');

        $this->assertEquals('value', $config->get('test.key'));
    }
}
```

## 🛠️ Development

### Building from Source

1. **Install dependencies**
   ```bash
   composer install
   ```

2. **Build the extension**
   ```bash
   phpize
   ./configure
   make
   make install
   ```

3. **Run tests**
   ```bash
   make test
   ```

### Project Structure

```
sdk/php/
├── src/                    # PHP source files
│   ├── lib.rs             # Rust extension code
│   ├── Config.php         # Configuration class
│   ├── Interpreter.php    # Interpreter wrapper
│   ├── ExecutionContext.php # Context wrapper
│   ├── Helix.php          # Main SDK class
│   └── autoload.php       # Autoloader
├── composer.json          # Composer configuration
├── ext.php                # Extension configuration
├── README.md              # This file
└── tests/                 # Test files
```

## 📋 Requirements

- **PHP**: 7.4 or higher
- **Rust**: 1.70 or higher (for building from source)
- **Composer**: 2.0 or higher (for dependency management)

## 🐛 Troubleshooting

### Common Issues

1. **Extension not loading**
   - Check `php.ini` has `extension=helix.so`
   - Verify PHP version compatibility
   - Check extension path: `php -i | grep extension_dir`

2. **Build errors**
   - Ensure Rust is installed: `rustc --version`
   - Check PHP development headers: `phpize --help`
   - Try `make clean && make`

3. **Runtime errors**
   - Check PHP error logs
   - Verify all dependencies are installed
   - Test with simple code first

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](https://helix-lang.org/docs/php)
- [GitHub Repository](https://github.com/helix-lang/php)
- [Issue Tracker](https://github.com/helix-lang/php/issues)
- [Packagist](https://packagist.org/packages/helix/lang)

---

**Built with ❤️ using Rust and ext-php-rs**
