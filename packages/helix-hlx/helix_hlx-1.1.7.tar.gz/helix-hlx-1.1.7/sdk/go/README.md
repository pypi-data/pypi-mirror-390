# Helix Configuration Language - Go SDK

A powerful configuration language designed specifically for AI systems, now available for Go applications.

## Features

- **AI-Optimized Syntax**: Designed specifically for AI system configuration
- **Type Safety**: Strong typing with compile-time validation
- **High Performance**: Native Rust implementation with Go bindings via cgo
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Rich Data Types**: Support for complex data structures and AI-specific types
- **Automatic FFI Generation**: Uses cbindgen for seamless Rust-Go integration

## Installation

```bash
go get github.com/cyber-boost/helix
```

## Quick Start

```go
package main

import (
    "fmt"
    "log"
    "github.com/cyber-boost/helix"
)

func main() {
    // Parse a Helix configuration
    config, err := helix.Parse(`
agent my_agent {
    name = "AI Assistant"
    model = "gpt-4"
    temperature = 0.7
    max_tokens = 2048
}

workflow main_workflow {
    steps = [
        { action = "analyze", agent = my_agent }
        { action = "generate", agent = my_agent }
    ]
}
`)
    if err != nil {
        log.Fatal(err)
    }
    defer config.Close()

    // Access configuration values
    agent, err := config.GetAgent("my_agent")
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Agent: %s\n", agent.Name)
    fmt.Printf("Model: %s\n", agent.Model)
}
```

## API Reference

### Core Types

- `HelixConfig`: Root configuration object
- `Agent`: AI agent configuration
- `Workflow`: Workflow definition
- `Memory`: Memory configuration
- `Context`: Context configuration
- `Crew`: Crew configuration
- `Pipeline`: Pipeline configuration

### Error Handling

```go
config, err := helix.Parse(configText)
if err != nil {
    if helixErr, ok := err.(*helix.HelixError); ok {
        fmt.Printf("Parse error: %s\n", helixErr.Message)
        fmt.Printf("Error code: %d\n", helixErr.Code)
        fmt.Printf("Location: %d:%d\n", helixErr.Line, helixErr.Column)
    } else {
        fmt.Printf("Unexpected error: %v\n", err)
    }
}
```

## Advanced Usage

### File-based Configuration

```go
// Parse from file
config, err := helix.ParseFile("config.hlx")
if err != nil {
    log.Fatal(err)
}
defer config.Close()
```

### Complex Configuration Types

```go
// Access agents with custom properties
agents, err := config.GetAgents()
if err != nil {
    log.Fatal(err)
}

for _, agent := range agents {
    fmt.Printf("Agent: %s\n", agent.Name)
    fmt.Printf("Model: %s\n", agent.Model)
    
    // Access custom properties
    if tools, ok := agent.Properties["tools"].([]interface{}); ok {
        fmt.Printf("Tools: %v\n", tools)
    }
    
    if memoryEnabled, ok := agent.Properties["memory_enabled"].(bool); ok {
        fmt.Printf("Memory Enabled: %t\n", memoryEnabled)
    }
}

// Access workflows with steps
workflows, err := config.GetWorkflows()
if err != nil {
    log.Fatal(err)
}

for _, workflow := range workflows {
    fmt.Printf("Workflow: %s\n", workflow.Name)
    fmt.Printf("Steps: %d\n", len(workflow.Steps))
    
    for _, step := range workflow.Steps {
        fmt.Printf("  Step: %s\n", step.Action)
        if step.Agent != "" {
            fmt.Printf("    Agent: %s\n", step.Agent)
        }
        
        // Access step properties
        if parameters, ok := step.Properties["parameters"].(map[string]interface{}); ok {
            fmt.Printf("    Parameters: %v\n", parameters)
        }
    }
}
```

### Memory Management

```go
// Always close the configuration to free C resources
config, err := helix.Parse(configText)
if err != nil {
    log.Fatal(err)
}
defer config.Close() // Important: free C resources
```

## Building from Source

### Prerequisites

- Go 1.21 or later
- Rust 1.70 or later
- Cargo
- cbindgen

### Build Steps

1. Clone the repository:
```bash
git clone https://github.com/cyber-boost/helix.git
cd helix/sdk/go
```

2. Install cbindgen:
```bash
cargo install cbindgen
```

3. Build the Rust library:
```bash
cargo build --release --features csharp
```

4. Generate C header and build Go SDK:
```bash
./build.sh
```

5. Run examples:
```bash
go run examples/basic/main.go
go run examples/advanced/main.go
go run examples/file/main.go
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `basic/main.go`: Simple configuration parsing
- `advanced/main.go`: Complex multi-component configurations
- `file/main.go`: File-based configuration parsing

## Architecture

The Go SDK uses the following architecture:

1. **Rust Core**: The core Helix parser and semantic analyzer written in Rust
2. **C FFI Layer**: C-style foreign function interface for Rust-Go interop
3. **Go Bindings**: Go structs that wrap the native functionality
4. **cgo Integration**: Automatic FFI generation with cbindgen

## Performance

- **Native Performance**: Core parsing logic runs in native Rust code
- **Minimal Overhead**: cgo calls are optimized for minimal marshalling
- **Memory Efficient**: Automatic memory management with proper cleanup
- **Cross-Platform**: Single codebase works on Windows, macOS, and Linux

## Cross-Platform Support

The SDK supports the following platforms:

- **Linux**: x86_64-unknown-linux-gnu
- **macOS**: aarch64-apple-darwin, x86_64-apple-darwin
- **Windows**: x86_64-pc-windows-msvc

## Troubleshooting

### Common Issues

1. **Native Library Not Found**: Ensure the Rust library is built with `csharp` feature
2. **Platform-Specific Issues**: Check that the correct native library is present
3. **Memory Issues**: Always call `Close()` on `HelixConfig`

### Debug Mode

For debugging, build with debug symbols:
```bash
cargo build --features csharp
go build -tags debug
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

