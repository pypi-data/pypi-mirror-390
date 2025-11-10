# Helix Ruby SDK

A Ruby gem providing native bindings to the Helix configuration language compiler.

## Installation

```bash
gem install helix
```

## Usage

```ruby
require 'helix'

# Parse and validate HLX configuration
result = Helix.do_thing('agent my_agent { name = "Test Agent" }')
puts result # => "Successfully processed HLX configuration"

# Parse HLX source code
Helix.parse('workflow my_workflow { steps = [] }')

# Load an HLX file
Helix.load_file('/path/to/config.hlx')

# Pretty print HLX code
pretty = Helix.pretty_print('agent a{name="test"}')
puts pretty
```

## Requirements

- Ruby 3.0+
- Rust toolchain (only needed for gem installation/compilation)

## Development

To build the gem locally:

```bash
git clone https://github.com/cyber-boost/helix.git
cd helix/sdk/ruby/helix-gem
bundle install
rake compile
gem build helix.gemspec
```

## License

MIT