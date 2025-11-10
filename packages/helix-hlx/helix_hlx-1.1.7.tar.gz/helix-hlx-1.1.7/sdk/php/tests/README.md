# Helix PHP SDK Tests

This directory contains comprehensive tests for the Helix PHP SDK, focusing on FFI functionality validation.

## Test Structure

### FFITest.php
Direct FFI interface tests that validate:
- FFI library loading and initialization
- Basic connectivity and function calls
- Memory management and pointer handling
- Error conditions and edge cases
- Performance characteristics
- Data type conversions
- UTF-8 string handling

### FFIMemoryTest.php
Memory management and performance tests that ensure:
- No memory leaks during FFI operations
- Proper cleanup of allocated strings
- Reasonable memory usage patterns
- Garbage collection compatibility
- Stress testing with large datasets
- Concurrent operation safety

### HelixIntegrationTest.php
Integration tests that validate the complete SDK functionality:
- Real Helix code execution through PHP SDK
- Configuration management
- File loading and template processing
- Error handling and validation
- Context management (session, request)
- Complex data operations

### Existing Tests
- `HelixTest.php` - Main SDK class functionality
- `InterpreterTest.php` - Interpreter operations
- `ConfigTest.php` - Configuration management

## Running Tests

### Prerequisites
- PHP 7.4+ with FFI extension enabled
- PHPUnit 9.0+
- Compiled Helix FFI library (`helix_ffi.so`)

### Installation
```bash
cd sdk/php
composer install
```

### Run All Tests
```bash
vendor/bin/phpunit
```

### Run Specific Test Suites
```bash
# FFI tests only
vendor/bin/phpunit --testsuite "FFI Tests"

# Integration tests only
vendor/bin/phpunit --testsuite "Integration Tests"

# Memory tests only
vendor/bin/phpunit --testsuite "Memory Tests"

# Unit tests only
vendor/bin/phpunit --testsuite "Unit Tests"
```

### Run With Coverage
```bash
vendor/bin/phpunit --coverage-html coverage/
```

## Test Requirements

### FFI Library
The tests require the Helix FFI library to be built and available at `../helix_ffi.so`. If the library is not available, FFI-related tests will be skipped.

To build the FFI library:
```bash
cd ../../
cargo build --release --features php
cp target/release/libhelix.so sdk/php/helix_ffi.so
```

### Test Categories

#### FFI Tests
- **Purpose**: Validate direct FFI functionality
- **Requirements**: FFI library must be available
- **Coverage**: Memory management, data conversion, error handling

#### Integration Tests
- **Purpose**: Validate complete SDK functionality
- **Requirements**: PHP SDK classes
- **Coverage**: Real Helix execution, configuration, file operations

#### Memory Tests
- **Purpose**: Ensure no memory leaks or excessive usage
- **Requirements**: FFI library must be available
- **Coverage**: Memory allocation/deallocation patterns

#### Unit Tests
- **Purpose**: Test individual components
- **Requirements**: PHP SDK classes
- **Coverage**: Class methods, error conditions, edge cases

## Test Results

Tests will be marked as skipped if prerequisites are not met:
- `FFI extension not available` - PHP FFI extension not loaded
- `Helix FFI library not found` - helix_ffi.so file missing
- `Failed to load FFI library` - Library exists but cannot be loaded

## Performance Expectations

- **Memory Usage**: Tests ensure memory growth stays within reasonable limits
- **Execution Time**: Individual tests should complete within 30 seconds
- **Concurrent Operations**: Multiple FFI calls should not interfere with each other

## Debugging

If tests fail unexpectedly:
1. Check PHP error logs
2. Verify FFI extension is loaded: `php -m | grep ffi`
3. Ensure library is built: `ls -la ../helix_ffi.so`
4. Check library permissions: `ldd ../helix_ffi.so`

## Continuous Integration

These tests are designed to run in CI environments and will:
- Skip gracefully when FFI is not available
- Provide detailed failure information
- Generate coverage reports
- Respect time limits and resource constraints
