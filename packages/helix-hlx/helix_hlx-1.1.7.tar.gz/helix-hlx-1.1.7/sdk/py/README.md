# Helix Python SDK

![Helix Language](https://img.shields.io/badge/Helix-Language-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![PyPI](https://img.shields.io/badge/PyPI-Ready-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

A Python SDK for the **Helix Configuration Language** - a powerful, AI-optimized configuration language designed for modern applications.

## 🚀 Features

- **High-Performance**: Compiled Rust backend with PyO3 bindings
- **Type-Safe**: Full type hints and static analysis support
- **Cross-Platform**: Universal wheels for Windows, macOS, and Linux
- **Zero Dependencies**: No Rust toolchain required for end users
- **Production Ready**: Enterprise-grade error handling and validation

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install helix-lang
```

### From Source (Development)
```bash
# Clone the repository
git clone https://github.com/cyber-boost/helix.git
cd helix

# Build and install
python sdk/py/build.py all
```

## 🔧 Quick Start

### Basic Configuration
```python
import helix

# Create a configuration object
config = helix.HelixConfig()

# Set values
config.set("database.host", "localhost")
config.set("database.port", 5432)
config.set("features", ["auth", "caching", "logging"])

# Get values
host = config.get("database.host")
port = config.get("database.port", 3306)  # with default
features = config.get("features", [])

print(f"Database: {host}:{port}")
print(f"Features: {features}")
```

### Parsing Helix Source Code
```python
import helix

# Parse Helix configuration from string
source = '''
database {
    host = "production-db.example.com"
    port = 5432
    credentials {
        username = "admin"
        password = "secret"
    }
}

features = ["auth", "caching", "metrics"]
debug = false
'''

config = helix.parse(source)

# Access parsed values
db_host = config.get("database.host")
db_port = config.get("database.port")
username = config.get("database.credentials.username")
```

### Loading from Files
```python
import helix

# Load configuration from a .hlx file
config = helix.load_file("config.hlx")

# Access configuration values
app_name = config.get("app.name")
version = config.get("app.version")
```

### Direct Expression Execution
```python
import helix

# Execute Helix expressions with context
context = {
    "user_id": 12345,
    "permissions": ["read", "write"],
    "settings": {"theme": "dark"}
}

result = helix.execute("@env.user_id + 1000", context)
print(f"Result: {result}")

# Check permissions
has_permission = helix.execute("user_id in permissions", {
    "user_id": 12345,
    "permissions": ["read", "write", "admin"]
})
print(f"Has permission: {has_permission}")
```

## 🏗️ API Reference

### HelixConfig Class

The main interface for working with Helix configurations.

#### Constructor
```python
HelixConfig(source: Optional[str] = None, file_path: Optional[str] = None)
```

#### Methods
- `get(key: str, default: Any = None) -> Any`: Get a configuration value
- `set(key: str, value: Any) -> None`: Set a configuration value
- `keys() -> List[str]`: Get all configuration keys
- `items() -> Dict[str, Any]`: Get all configuration items
- `execute(expression: str) -> Any`: Execute a Helix expression
- `to_dict() -> Dict[str, Any]`: Convert to Python dictionary

### HelixParser Class

Static utility for parsing Helix configurations.

#### Static Methods
- `parse(source: str) -> HelixConfig`: Parse Helix source code
- `load_file(file_path: str) -> HelixConfig`: Load from file

### HelixInterpreter Class

Direct access to the Helix interpreter (async).

#### Constructor
```python
HelixInterpreter()
```

#### Methods
- `async execute(expression: str) -> Any`: Execute expression
- `set_variable(name: str, value: Any) -> None`: Set variable
- `get_variable(name: str) -> Any`: Get variable

### Utility Functions

#### `parse(source: str) -> HelixConfig`
Parse Helix source code into a configuration object.

#### `execute(expression: str, context: Optional[Dict[str, Any]] = None) -> Any`
Execute a Helix expression with optional context.

#### `load_file(file_path: str) -> HelixConfig`
Load a Helix configuration from a file.

## 🎯 Advanced Usage

### Working with Complex Data Types

```python
import helix

config = helix.HelixConfig()

# Set complex nested structures
config.set("servers", [
    {"host": "server1.example.com", "port": 8080},
    {"host": "server2.example.com", "port": 8081}
])

# Access nested values
servers = config.get("servers")
server1_host = servers[0]["host"] if servers else None
```

### Custom Context for Execution

```python
import helix

# Create context with custom variables
context = {
    "user": {"id": 12345, "name": "John Doe"},
    "permissions": ["read", "write"],
    "settings": {"max_connections": 100}
}

# Execute expressions with context
result = helix.execute("@user.id == 12345", context)
max_conn = helix.execute("@settings.max_connections", context)
```

### Error Handling

```python
import helix

try:
    config = helix.parse("invalid helix syntax {")
except Exception as e:
    print(f"Parse error: {e}")

try:
    result = config.get("nonexistent.key")
except KeyError:
    print("Key not found")

# Safe access with defaults
value = config.get("maybe.key", "default_value")
```

## 🧪 Testing

### Unit Tests
```bash
# Run Python tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_config.py

# Run with coverage
python -m pytest --cov=helix tests/
```

### Integration Tests
```python
import helix

def test_basic_config():
    config = helix.HelixConfig()
    config.set("test", "value")
    assert config.get("test") == "value"

def test_parsing():
    source = 'key = "value"'
    config = helix.parse(source)
    assert config.get("key") == "value"
```

## 🔧 Development

### Building from Source

#### Prerequisites
- Python 3.8+
- Rust toolchain (for development builds)
- Maturin (Python package)

#### Development Build
```bash
# Install maturin
pip install maturin

# Build wheel
maturin build --release

# Install in development mode
pip install target/wheels/helix_lang-*.whl --force-reinstall
```

#### Development with Hot Reload (requires Rust)
```bash
# For development builds with Rust
maturin develop

# Run tests
python -m pytest tests/
```

### Project Structure
```
sdk/py/
├── helix/              # Python package
│   ├── __init__.py    # Main module
│   ├── _core.pyi      # Type stubs
│   └── _core.so/.pyd  # Compiled extension (generated)
├── build.py           # Build script
├── pyproject.toml     # Python packaging config
└── README.md          # This file
```

## 📋 Configuration Examples

### Application Configuration
```python
import helix

config = helix.parse('''
app {
    name = "MyApp"
    version = "1.0.0"
    environment = "production"
}

database {
    host = "db.example.com"
    port = 5432
    name = "myapp_db"
}

redis {
    host = "redis.example.com"
    port = 6379
}

features = ["auth", "caching", "metrics"]
debug = false
''')

# Access configuration
app_name = config.get("app.name")
db_host = config.get("database.host")
features = config.get("features")
```

### Environment-Based Configuration
```python
import helix

# Load configuration based on environment
env = os.getenv("ENVIRONMENT", "development")
config = helix.load_file(f"config.{env}.hlx")

# Override with environment variables
config.set("database.host", os.getenv("DB_HOST", config.get("database.host")))
config.set("database.password", os.getenv("DB_PASSWORD"))
```

## 🚀 Performance Tips

### Caching Configuration Objects
```python
import helix

# Cache configuration objects for better performance
config_cache = {}

def get_config(env: str):
    if env not in config_cache:
        config_cache[env] = helix.load_file(f"config.{env}.hlx")
    return config_cache[env]
```

### Batch Operations
```python
# Better: batch multiple operations
config = helix.HelixConfig()
config.set("key1", "value1")
config.set("key2", "value2")
config.set("key3", "value3")

# Avoid: individual operations (creates intermediate objects)
```

### Expression Optimization
```python
# Pre-compile frequently used expressions
frequently_used = [
    "@user.permissions.contains('admin')",
    "@config.debug == true",
    "@server.status == 'active'"
]

# Use cached expressions in loops
for expr in frequently_used:
    result = helix.execute(expr, context)
```

## 🐛 Troubleshooting

### Common Issues

#### ImportError: No module named 'helix'
```bash
# Make sure the package is installed
pip install helix-lang

# Or install from local build
pip install target/wheels/helix_lang-*.whl --force-reinstall
```

#### AttributeError: module 'helix' has no attribute '_core'
```bash
# The extension module wasn't built correctly
python sdk/py/build.py build
python sdk/py/build.py install
```

#### PyO3 Runtime Error
```bash
# Try rebuilding with different Python version
PYTHON_VERSION=3.9 maturin build --release
```

### Debug Mode
```python
import helix

# Enable debug mode for more detailed error messages
import logging
logging.basicConfig(level=logging.DEBUG)

config = helix.HelixConfig()
```

## 📚 Examples

### Complete Application Example
```python
import helix
import os

class AppConfig:
    def __init__(self):
        # Load configuration
        env = os.getenv("ENV", "development")
        self.config = helix.load_file(f"config.{env}.hlx")

        # Override with environment variables
        self.config.set("database.host", os.getenv("DB_HOST"))
        self.config.set("database.port", int(os.getenv("DB_PORT", 5432)))

    def get_db_connection_string(self):
        host = self.config.get("database.host")
        port = self.config.get("database.port")
        db_name = self.config.get("database.name")
        return f"postgresql://{host}:{port}/{db_name}"

    def is_feature_enabled(self, feature: str):
        features = self.config.get("features", [])
        return feature in features

    def get_setting(self, key: str, default=None):
        return self.config.get(key, default)

# Usage
app_config = AppConfig()
print(app_config.get_db_connection_string())
print(app_config.is_feature_enabled("caching"))
print(app_config.get_setting("app.version", "1.0.0"))
```

## 🔗 Links

- [Helix Language Documentation](https://github.com/cyber-boost/helix)
- [PyO3 Documentation](https://pyo3.rs/)
- [Maturin Documentation](https://maturin.rs/)
- [Python Packaging Guide](https://packaging.python.org/)

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please see the main Helix repository for contribution guidelines.

---

**Made with ❤️ by the Helix Team**
