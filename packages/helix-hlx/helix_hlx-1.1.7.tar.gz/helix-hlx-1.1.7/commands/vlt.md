# HLX Vault (vlt) Command Documentation

## Overview

The `hlx vlt` commands provide automatic version control for HLX configuration files. Every time you save or edit an HLX file, a versioned backup is automatically created in `~/.dna/vlt/`.

## Core Concepts

- **Vault Storage**: All versions are stored in `~/.dna/vlt/` organized by file hash
- **Automatic Backups**: Every save operation creates a timestamped backup
- **HLX Native**: Configuration uses `.hlx` format (not TOML/YAML)
- **Editor Integration**: Seamless integration with your preferred text editor

## Commands

### `hlx vlt new [NAME]`

Create a new HLX file and open it in your editor.

```bash
# Create with auto-generated name
hlx vlt new

# Create with specific name
hlx vlt new myconfig
```

The file is automatically saved to the vault after editing.

### `hlx vlt open [PATH]`

Open an existing file with automatic backup before editing.

```bash
# Open file with default editor
hlx vlt open config.hlx

# Open with specific editor
hlx vlt open config.hlx --editor nano
```

### `hlx vlt list`

List all files tracked in the vault.

```bash
# Simple list
hlx vlt list

# Detailed view with version info
hlx vlt list --long
```

### `hlx vlt save PATH`

Manually save a file to the vault with optional description.

```bash
# Quick save
hlx vlt save config.hlx

# Save with description
hlx vlt save config.hlx -d "Added database settings"
```

### `hlx vlt history PATH`

View version history for a file.

```bash
# Show last 10 versions
hlx vlt history config.hlx

# Show all versions with details
hlx vlt history config.hlx -n 50 --long
```

### `hlx vlt revert PATH VERSION`

Revert a file to a previous version.

```bash
# Revert to specific version
hlx vlt revert config.hlx 20241026T150145123

# Force revert without confirmation
hlx vlt revert config.hlx 20241026T150145123 --force
```

### `hlx vlt diff PATH`

Compare versions of a file.

```bash
# Compare current with latest vault version
hlx vlt diff config.hlx

# Compare two specific versions
hlx vlt diff config.hlx --from 20241026T150145123 --to 20241026T160230456
```

### `hlx vlt config`

Manage vault configuration (stored in `~/.dna/vlt/config.hlx`).

```bash
# Show current configuration
hlx vlt config

# Enable compression
hlx vlt config --compress true

# Set retention period
hlx vlt config --retention-days 60

# Set default editor
hlx vlt config --editor "code"
```

### `hlx vlt gc`

Clean up old versions based on retention policy.

```bash
# Dry run - see what would be deleted
hlx vlt gc --dry-run

# Run garbage collection
hlx vlt gc

# Force without confirmation
hlx vlt gc --force
```

## Configuration

Vault configuration is stored in `~/.dna/vlt/config.hlx`:

```hlx
[vault]
compress = false          # Enable gzip compression
auto_save_interval = 0    # Auto-save interval in minutes (0 = disabled)
max_versions = 0          # Maximum versions per file (0 = unlimited)
retention_days = 30       # Days to keep old versions
editor = "vim"           # Default editor
```

## Environment Variables

- `EDITOR` or `VISUAL`: Override default editor
- `HLX_EDITOR`: HLX-specific editor override

## Integration with HLX

The vault system is deeply integrated with HLX:

1. **Automatic Backups**: Any `hlx` save operation triggers a vault backup
2. **Native Format**: All configs use `.hlx` format
3. **Seamless Workflow**: Work normally, backups happen automatically

## Examples

### Creating and Editing Configuration

```bash
# Create new config
hlx vlt new myapp

# Edit the file (opens in editor)
# Add your configuration using HLX commands:
# hlx.set("database", "host", "localhost")
# hlx.set("database", "port", 5432)
# hlx.save()

# File is automatically backed up after save
```

### Working with Existing Files

```bash
# Open for editing (auto-backup before edit)
hlx vlt open production.hlx

# View history
hlx vlt history production.hlx

# Revert if needed
hlx vlt revert production.hlx 20241026T150145123
```

### Managing Vault

```bash
# See all tracked files
hlx vlt list --long

# Configure vault
hlx vlt config --compress true --retention-days 90

# Clean up old versions
hlx vlt gc --dry-run
hlx vlt gc
```

## Best Practices

1. **Regular Cleanup**: Run `hlx vlt gc` periodically to manage disk space
2. **Descriptive Saves**: Use `-d` flag to add descriptions for important changes
3. **Version Before Major Changes**: Manually save before significant edits
4. **Configure Retention**: Adjust `retention_days` based on your needs

## Troubleshooting

### Editor Not Opening
- Check `EDITOR` or `VISUAL` environment variables
- Use `hlx vlt config --editor <editor>` to set default
- The system tries multiple editors: $EDITOR → $VISUAL → vim → nano → emacs

### Vault Growing Too Large
- Run `hlx vlt gc` to clean old versions
- Set `max_versions` to limit versions per file
- Enable compression: `hlx vlt config --compress true`

### Cannot Find Version
- Use `hlx vlt history <file>` to list all versions
- Version IDs are timestamps: YYYYMMDDTHHMMSS[milliseconds]
