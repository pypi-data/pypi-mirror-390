# Helix Configuration Language - C# SDK

A powerful configuration language designed specifically for AI systems, now available for .NET applications.

## Features

- **AI-Optimized Syntax**: Designed specifically for AI system configuration
- **Type Safety**: Strong typing with compile-time validation
- **High Performance**: Native Rust implementation with C# bindings
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Rich Data Types**: Support for complex data structures and AI-specific types
- **Automatic FFI Generation**: Uses dotnet-rust for seamless Rust-C# integration

## Installation

```bash
dotnet add package Helix.Configuration
```

## Quick Start

```csharp
using Helix;

// Parse a Helix configuration
var config = HelixParser.Parse(@"
agent my_agent {
    name = ""AI Assistant""
    model = ""gpt-4""
    temperature = 0.7
    max_tokens = 2048
}

workflow main_workflow {
    steps = [
        { action = ""analyze"", agent = my_agent }
        { action = ""generate"", agent = my_agent }
    ]
}
");

// Access configuration values
var agent = config.GetAgent("my_agent");
Console.WriteLine($"Agent: {agent.Name}");
Console.WriteLine($"Model: {agent.Model}");
```

## API Reference

### Core Classes

- `HelixParser`: Main parser for Helix configuration files
- `HelixConfig`: Root configuration object
- `AgentConfig`: AI agent configuration
- `WorkflowConfig`: Workflow definition
- `MemoryConfig`: Memory configuration
- `ContextConfig`: Context configuration
- `CrewConfig`: Crew configuration
- `PipelineConfig`: Pipeline configuration
- `Value`: Dynamic value type for Helix values

### Error Handling

```csharp
try 
{
    var config = HelixParser.Parse(configText);
}
catch (HelixParseException ex)
{
    Console.WriteLine($"Parse error: {ex.Message}");
    Console.WriteLine($"Location: {ex.Line}:{ex.Column}");
}
```

## Advanced Usage

### File-based Configuration

```csharp
// Parse from file
var config = HelixParser.ParseFile("config.hlx");
```

### Complex Configuration Types

```csharp
// Access agents with custom properties
foreach (var agent in config.Agents)
{
    var tools = agent.GetProperty<List<string>>("tools");
    var memoryEnabled = agent.GetProperty<bool>("memory_enabled");
    var safetyLevel = agent.GetProperty<string>("safety_level");
}

// Access workflows with steps
foreach (var workflow in config.Workflows)
{
    foreach (var step in workflow.Steps)
    {
        var parameters = step.GetProperty<Dictionary<string, object>>("parameters");
        var input = step.GetProperty<string>("input");
    }
}
```

### Memory Management

```csharp
// The HelixConfig implements IDisposable for proper cleanup
using var config = HelixParser.Parse(configText);
// Configuration will be automatically disposed
```

## Building from Source

### Prerequisites

- .NET 6.0 or later
- Rust 1.70 or later
- Cargo

### Build Steps

1. Clone the repository:
```bash
git clone https://github.com/cyber-boost/helix.git
cd helix/sdk/csharp
```

2. Build the Rust library with C# bindings:
```bash
cargo build --release --features csharp
```

3. Build the C# SDK:
```bash
dotnet build --configuration Release
```

4. Run examples:
```bash
dotnet run --project examples/BasicExample.cs
```

### Creating NuGet Package

```bash
# Build and pack
./build.sh Release net6.0 true

# Or using PowerShell
./build.ps1 -Configuration Release -TargetFramework net6.0 -Pack
```

### Publishing to NuGet

```bash
# Push to NuGet (requires API key)
./build.sh Release net6.0 true true YOUR_API_KEY

# Or using PowerShell
./build.ps1 -Configuration Release -TargetFramework net6.0 -Pack -Push -ApiKey YOUR_API_KEY
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `BasicExample.cs`: Simple configuration parsing
- `AdvancedExample.cs`: Complex multi-component configurations
- `FileExample.cs`: File-based configuration parsing

## Architecture

The C# SDK uses the following architecture:

1. **Rust Core**: The core Helix parser and semantic analyzer written in Rust
2. **FFI Layer**: C-style foreign function interface for Rust-C# interop
3. **C# Bindings**: Managed C# classes that wrap the native functionality
4. **dotnet-rust Integration**: Automatic FFI generation and binding

## Performance

- **Native Performance**: Core parsing logic runs in native Rust code
- **Minimal Overhead**: FFI calls are optimized for minimal marshalling
- **Memory Efficient**: Automatic memory management with proper disposal
- **Cross-Platform**: Single codebase works on Windows, macOS, and Linux

## Troubleshooting

### Common Issues

1. **Native Library Not Found**: Ensure the Rust library is built with `csharp` feature
2. **Platform-Specific Issues**: Check that the correct native library is present
3. **Memory Issues**: Always use `using` statements or call `Dispose()` on `HelixConfig`

### Debug Mode

For debugging, build with debug symbols:
```bash
cargo build --features csharp
dotnet build --configuration Debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: [https://github.com/cyber-boost/helix/issues](https://github.com/cyber-boost/helix/issues)
- Documentation: [https://github.com/cyber-boost/helix/tree/main/docs](https://github.com/cyber-boost/helix/tree/main/docs)
