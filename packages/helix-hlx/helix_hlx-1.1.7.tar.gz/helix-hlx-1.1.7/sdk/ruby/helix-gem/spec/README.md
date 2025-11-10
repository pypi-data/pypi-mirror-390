# Helix Ruby SDK Test Suite

This directory contains comprehensive tests for the Helix Ruby SDK native extension.

## Test Structure

### Core Test Files

- **`spec_helper.rb`** - Shared test configuration, utilities, and test data
- **`helix_spec.rb`** - Main functionality tests for all Helix module methods
- **`error_handling_spec.rb`** - Comprehensive error handling and edge case tests
- **`integration_spec.rb`** - End-to-end integration tests and performance benchmarks
- **`native_extension_spec.rb`** - Tests specific to the Rust native extension functionality

### Test Categories

#### Unit Tests (`helix_spec.rb`)
- Parsing valid HLX configurations
- File loading functionality
- Pretty printing
- Execution via HelixInterpreter
- Validation without execution
- AST generation
- Return type validation

#### Error Handling Tests (`error_handling_spec.rb`)
- Syntax error handling
- File operation errors
- Runtime execution errors
- Argument validation
- Edge cases (empty strings, large configs, etc.)

#### Integration Tests (`integration_spec.rb`)
- End-to-end workflows
- Data consistency across operations
- Performance characteristics
- Memory management
- Concurrent usage patterns
- Real-world usage scenarios

#### Native Extension Tests (`native_extension_spec.rb`)
- Extension loading verification
- Method signature validation
- Return type checking
- Memory management
- JSON serialization
- Rust runtime integration
- HLX to Rust data conversion

## Running Tests

### Prerequisites

Ensure you have:
- Ruby 3.0+
- Rust toolchain (cargo)
- Bundler

### Setup

```bash
cd sdk/ruby/helix-gem
bundle install
rake compile  # Compile the native extension
```

### Run All Tests

```bash
# Run tests with compilation
rake test

# Run tests only (assumes extension is compiled)
rake spec

# Run tests with coverage
rake spec_with_coverage
```

### Run Specific Test Files

```bash
# Run specific test file
bundle exec rspec spec/helix_spec.rb

# Run specific test
bundle exec rspec spec/helix_spec.rb:10

# Run tests matching a pattern
bundle exec rspec --pattern "**/*error*"
```

### Code Quality

```bash
# Run RuboCop
rake rubocop

# Run all quality checks
rake quality
```

## Test Data

The `TestData` module in `spec_helper.rb` provides sample HLX configurations:

- `sample_agent_config` - Basic agent configuration
- `sample_workflow_config` - Simple workflow definition
- `sample_project_config` - Project metadata
- `complex_config` - Multi-component configuration
- `invalid_syntax_config` - Syntax error examples
- `invalid_semantic_config` - Semantic validation error examples

## Coverage

Tests aim for comprehensive coverage of:

- ✅ All public API methods
- ✅ Valid input handling
- ✅ Invalid input error handling
- ✅ File operations
- ✅ Memory management
- ✅ Concurrent usage
- ✅ Performance characteristics
- ✅ Native extension integration
- ✅ JSON serialization/deserialization
- ✅ Data type conversions

## Continuous Integration

The test suite is designed to run in CI environments with:

- Automatic dependency installation
- Native extension compilation
- Parallel test execution
- Coverage reporting
- Code quality checks

## Debugging Tests

For debugging failing tests:

1. Run with verbose output:
   ```bash
   bundle exec rspec --format documentation --backtrace
   ```

2. Run a specific failing test:
   ```bash
   bundle exec rspec spec/helix_spec.rb:25
   ```

3. Check native extension compilation:
   ```bash
   rake compile
   ```

4. Verify Rust code changes if tests fail unexpectedly

## Adding New Tests

When adding new tests:

1. Follow RSpec best practices
2. Add test data to `TestData` module if reusable
3. Include both positive and negative test cases
4. Test error conditions and edge cases
5. Ensure tests are isolated and don't depend on external state
6. Update this README if adding new test categories

## Performance Benchmarks

Integration tests include performance benchmarks for:

- Parsing large configurations
- Concurrent operations
- Memory usage patterns
- Scaling characteristics

These help ensure the native extension maintains good performance characteristics.
