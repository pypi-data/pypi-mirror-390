# Helix Java SDK

High-performance Java bindings for the Helix configuration language using JNI (Java Native Interface).

## Features

- **Fastest Performance**: Direct JNI bindings for maximum speed
- **Type Safety**: Full Java type safety with proper error handling
- **Async Support**: Asynchronous operations for non-blocking execution
- **Easy Integration**: Simple API that integrates seamlessly with Java applications
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Quick Start

### 1. Add Dependency

```xml
<dependency>
    <groupId>com.helix</groupId>
    <artifactId>helix-sdk</artifactId>
    <version>1.1.8</version>
</dependency>
```

### 2. Basic Usage

```java
import com.helix.HelixSDK;
import com.helix.HelixConfig;
import com.helix.HelixException;

public class Example {
    public static void main(String[] args) {
        try {
            // Parse Helix configuration
            String config = """
                agent "my_agent" {
                    name = "My Agent"
                    description = "A simple agent"
                }
                """;
            
            String astJson = HelixSDK.parse(config);
            System.out.println("Parsed: " + astJson);
            
            // Validate configuration
            boolean isValid = HelixSDK.validate(config);
            System.out.println("Valid: " + isValid);
            
            // Execute Helix code
            String result = HelixSDK.execute(config);
            System.out.println("Result: " + result);
            
            // Work with configuration object
            HelixConfig helixConfig = new HelixConfig(astJson);
            System.out.println("Agents: " + helixConfig.getAgentCount());
            
        } catch (HelixException e) {
            System.err.println("Error: " + e.getDetailedMessage());
        } finally {
            HelixSDK.shutdown();
        }
    }
}
```

## API Reference

### HelixSDK

Main SDK class providing static methods for Helix operations.

#### Methods

- `parse(String source)` - Parse Helix source code into AST JSON
- `execute(String source)` - Execute Helix code and return result
- `loadFile(String filePath)` - Load and execute a Helix file
- `validate(String source)` - Validate Helix configuration
- `getVersion()` - Get Helix library version
- `test()` - Test native library connection

#### Async Methods

- `parseAsync(String source)` - Asynchronously parse Helix code
- `executeAsync(String source)` - Asynchronously execute Helix code
- `loadFileAsync(String filePath)` - Asynchronously load and execute file

#### Utility Methods

- `parseAndValidate(String source)` - Parse and validate in one call
- `executeWithContext(String source, Map<String, String> context)` - Execute with context
- `shutdown()` - Cleanup resources

### HelixConfig

Represents a parsed Helix configuration with easy access to components.

#### Methods

- `getAgents()` - Get all agents as Map<String, JsonNode>
- `getWorkflows()` - Get all workflows as Map<String, JsonNode>
- `getContexts()` - Get all contexts as Map<String, JsonNode>
- `getCrews()` - Get all crews as Map<String, JsonNode>
- `getPipelines()` - Get all pipelines as Map<String, JsonNode>
- `getMemory()` - Get memory configuration
- `hasAgent(String name)` - Check if agent exists
- `getAgentCount()` - Get number of agents
- `getSummary()` - Get configuration summary

### HelixException

Exception thrown by Helix operations with detailed error information.

#### Methods

- `getErrorCode()` - Get specific error code
- `getContext()` - Get additional context
- `getDetailedMessage()` - Get detailed error message

## Advanced Usage

### Async Operations

```java
// Parse asynchronously
CompletableFuture<String> parseFuture = HelixSDK.parseAsync(config);
String astJson = parseFuture.get();

// Execute asynchronously
CompletableFuture<String> executeFuture = HelixSDK.executeAsync(config);
String result = executeFuture.get();
```

### Complex Configuration Analysis

```java
HelixConfig config = new HelixConfig(astJson);

// Analyze agents
config.getAgents().forEach((name, agent) -> {
    System.out.println("Agent: " + name);
    if (agent.has("capabilities")) {
        System.out.println("  Capabilities: " + agent.get("capabilities"));
    }
});

// Get configuration summary
Map<String, Object> summary = config.getSummary();
summary.forEach((key, value) -> {
    System.out.println(key + ": " + value);
});
```

### Error Handling

```java
try {
    String result = HelixSDK.parse(invalidConfig);
} catch (HelixException e) {
    System.err.println("Error Code: " + e.getErrorCode());
    System.err.println("Context: " + e.getContext());
    System.err.println("Message: " + e.getDetailedMessage());
}
```

## Building from Source

### Prerequisites

- Java 11 or higher
- Maven 3.6 or higher
- Rust toolchain (for native library)
- GCC or Clang (for JNI compilation)

### Build Steps

1. **Build the native library:**
   ```bash
   cd sdk/java
   ./build_native.sh
   ```

2. **Compile Java code:**
   ```bash
   mvn compile
   ```

3. **Run tests:**
   ```bash
   mvn test
   ```

4. **Package:**
   ```bash
   mvn package
   ```

## Native Library

The SDK includes native libraries for multiple platforms:

- `linux/x86_64/libhelix_java.so`
- `linux/aarch64/libhelix_java.so`
- `darwin/x86_64/libhelix_java.dylib`
- `darwin/aarch64/libhelix_java.dylib`
- `windows/x86_64/helix_java.dll`

The appropriate library is automatically loaded based on your system.

## Performance

The JNI bindings provide the fastest possible integration with Java:

- **Direct Memory Access**: No serialization overhead
- **Native Speed**: Direct calls to Rust implementation
- **Minimal Overhead**: JNI overhead is negligible
- **Async Support**: Non-blocking operations for high throughput

## Examples

See the `examples/` directory for complete examples:

- `BasicExample.java` - Simple usage examples
- `AdvancedExample.java` - Complex configuration analysis
- `AsyncExample.java` - Asynchronous operations

## Troubleshooting

### Library Loading Issues

If you get `UnsatisfiedLinkError`:

1. Ensure the native library is in your `java.library.path`
2. Check that the library architecture matches your system
3. Verify all dependencies are available

### Build Issues

If native compilation fails:

1. Ensure Rust toolchain is installed
2. Check that Java development headers are available
3. Verify GCC/Clang is installed

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [Report issues](https://github.com/cyber-boost/helix/issues)
- Documentation: [Full documentation](https://helix.cyber-boost.com/docs)
- Community: [Join our community](https://discord.gg/helix)
