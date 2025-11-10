//! Vault (vlt) CLI commands

use clap::{Args, Subcommand};
use std::path::PathBuf;
use colored::*;
use crate::dna::vlt::{Vault, VaultError};
use std::process::Command;
use std::env;

#[derive(Args)]
pub struct VltArgs {
    #[command(subcommand)]
    command: VltCommands,
}

#[derive(Subcommand)]
enum VltCommands {
    /// Create new HLX file in editor
    New {
        /// Optional filename (defaults to timestamped name)
        name: Option<String>,
    },
    
    /// Open file with automatic backup
    Open {
        /// File path to open
        path: Option<PathBuf>,
        
        /// Editor to use (overrides HLX_EDITOR and $EDITOR)
        #[arg(short, long)]
        editor: Option<String>,
    },
    
    /// List all files in vault
    List {
        /// Show detailed information
        #[arg(short, long)]
        long: bool,
    },
    
    /// Save file to vault
    Save {
        /// File path to save
        path: PathBuf,
        
        /// Optional description for this version
        #[arg(short, long)]
        description: Option<String>,
    },
    
    /// Show version history
    History {
        /// File path
        path: PathBuf,
        
        /// Number of versions to show
        #[arg(short = 'n', long, default_value = "10")]
        limit: usize,
        
        /// Show full details
        #[arg(short = 'l', long)]
        long: bool,
    },
    
    /// Revert to specific version
    Revert {
        /// File path
        path: PathBuf,
        
        /// Version ID to revert to
        version: String,
        
        /// Force revert without confirmation
        #[arg(short, long)]
        force: bool,
    },
    
    /// Show differences between versions
    Diff {
        /// File path
        path: PathBuf,
        
        /// First version (defaults to current)
        #[arg(short = 'a', long)]
        from: Option<String>,
        
        /// Second version (defaults to latest)
        #[arg(short = 'b', long)]
        to: Option<String>,
    },
    
    /// Manage vault configuration
    Config {
        /// Show current configuration
        #[arg(short, long)]
        show: bool,
        
        /// Set compression on/off
        #[arg(long)]
        compress: Option<bool>,
        
        /// Set retention days
        #[arg(long)]
        retention_days: Option<u32>,
        
        /// Set max versions
        #[arg(long)]
        max_versions: Option<u32>,
        
        /// Set default editor
        #[arg(long)]
        editor: Option<String>,
    },
    
    /// Clean up old versions
    Gc {
        /// Dry run - show what would be deleted
        #[arg(short, long)]
        dry_run: bool,
        
        /// Force cleanup without confirmation
        #[arg(short, long)]
        force: bool,
    },

    /// Launch the interactive TUI for managing the vault
    Tui,
}

pub fn run(args: VltArgs) -> Result<(), VaultError> {
    match args.command {
        VltCommands::New { name } => create_new_file(name),
        VltCommands::Open { path, editor } => open_file(path, editor),
        VltCommands::List { long } => list_files(long),
        VltCommands::Save { path, description } => save_file(path, description),
        VltCommands::History { path, limit, long } => show_history(path, limit, long),
        VltCommands::Revert { path, version, force } => revert_file(path, version, force),
        VltCommands::Diff { path, from, to } => show_diff(path, from, to),
        VltCommands::Config { show, compress, retention_days, max_versions, editor } => {
            manage_config(show, compress, retention_days, max_versions, editor)
        },
        VltCommands::Gc { dry_run, force } => garbage_collect(dry_run, force),
        VltCommands::Tui => {
            crate::dna::vlt::tui::launch()
                .map_err(|e| VaultError::Config(format!("TUI launch failed: {}", e)))
        },
    }
}

fn get_editor() -> String {
    // Try to get editor from environment, with fallbacks
    env::var("EDITOR")
        .or_else(|_| env::var("VISUAL"))
        .unwrap_or_else(|_| {
            // Platform-specific defaults
            if cfg!(windows) {
                "notepad".to_string()
            } else {
                "vim".to_string()
            }
        })
}

fn open_editor_with_fallback(file_path: &str) -> std::io::Result<std::process::ExitStatus> {
    let editors = vec![
        env::var("EDITOR").ok(),
        env::var("VISUAL").ok(),
        Some("vim".to_string()),
        Some("nano".to_string()),
        Some("emacs".to_string()),
    ];
    
    for editor_opt in editors {
        if let Some(editor) = editor_opt {
            match Command::new(&editor).arg(file_path).status() {
                Ok(status) => return Ok(status),
                Err(_) => continue, // Try next editor
            }
        }
    }
    
    // Fallback to system default
    #[cfg(windows)]
    return Command::new("notepad").arg(file_path).status();
    
    #[cfg(unix)]
    return Command::new("vim").arg(file_path).status();
}

fn create_new_file(name: Option<String>) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    
    // Generate filename
    let filename = name.unwrap_or_else(|| {
        format!("new_{}.hlx", chrono::Local::now().format("%Y%m%d_%H%M%S"))
    });
    
    let tmp_dir = vault.root.join("tmp");
    std::fs::create_dir_all(&tmp_dir)?;
    let file_path = tmp_dir.join(&filename);
    
    // Create empty HLX file with basic structure
    let mut content = String::new();
    content.push_str("info :\n");
    content.push_str(&format!("    created = \"{}\"\n", chrono::Local::now().to_rfc3339()));
    content.push_str(";\n\n");
    
    // Write initial content
    std::fs::write(&file_path, content)?;
    
    println!("{} Creating new HLX file: {}", "→".blue(), filename);
    
    // Open in editor
    let status = open_editor_with_fallback(&file_path.to_string_lossy())
        .map_err(|e| VaultError::Config(format!("Failed to launch editor: {}", e)))?;
    
    if !status.success() {
        return Err(VaultError::Config("Editor exited with error".to_string()));
    }
    
    // After editing, save to vault
    if file_path.exists() {
        let version_id = vault.save(&file_path, Some("Created new HLX file".to_string()))?;
        println!("{} Saved to vault: {} (version: {})", "✓".green(), filename, version_id);
        
        // Move from tmp to current directory if user wants to keep it
        let target_path = PathBuf::from(&filename);
        if !target_path.exists() {
            std::fs::rename(&file_path, &target_path)?;
            println!("{} File saved as: {}", "✓".green(), filename);
        }
    }
    
    Ok(())
}

fn list_files(long: bool) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    let vlt_dir = vault.root.join("vlt");
    
    if !vlt_dir.exists() {
        println!("{} No files in vault yet", "→".yellow());
        return Ok(());
    }
    
    let mut files: std::collections::HashMap<String, Vec<(String, chrono::DateTime<chrono::Utc>, u64)>> = std::collections::HashMap::new();
    
    // Scan all manifests
    for entry in std::fs::read_dir(&vlt_dir)? {
        let entry = entry?;
        if entry.path().is_dir() {
            let manifest_path = entry.path().join("manifest.json");
            if manifest_path.exists() {
                let content = std::fs::read_to_string(&manifest_path)?;
                let manifest: crate::dna::vlt::Manifest = serde_json::from_str(&content)?;
                
                if let Some(path) = &manifest.original_path {
                    let filename = PathBuf::from(path)
                        .file_name()
                        .unwrap_or_default()
                        .to_string_lossy()
                        .to_string();
                    
                    for version in &manifest.versions {
                        files.entry(filename.clone())
                            .or_insert_with(Vec::new)
                            .push((version.id.clone(), version.created_at, version.size));
                    }
                }
            }
        }
    }
    
    if files.is_empty() {
        println!("{} No files in vault", "→".yellow());
        return Ok(());
    }
    
    println!("{} Files in vault:", "→".blue());
    println!();
    
    let mut sorted_files: Vec<_> = files.into_iter().collect();
    sorted_files.sort_by(|a, b| a.0.cmp(&b.0));
    
    for (filename, mut versions) in sorted_files {
        versions.sort_by(|a, b| b.1.cmp(&a.1)); // Sort by date, newest first
        
        if long {
            println!("{} {} ({} versions)", "●".green(), filename.bright_white(), versions.len());
            for (i, (id, date, size)) in versions.iter().take(3).enumerate() {
                println!("  {} {} - {} bytes", 
                    if i == 0 { "└─".dimmed() } else { "├─".dimmed() },
                    date.format("%Y-%m-%d %H:%M:%S"),
                    size
                );
            }
            if versions.len() > 3 {
                println!("  {} ... {} more versions", "└─".dimmed(), versions.len() - 3);
            }
            println!();
        } else {
            let latest = &versions[0];
            println!("{} {} - {} versions, latest: {}",
                "●".green(),
                filename,
                versions.len(),
                latest.1.format("%Y-%m-%d %H:%M:%S")
            );
        }
    }
    
    Ok(())
}

fn open_file(path: Option<PathBuf>, editor: Option<String>) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    
    // Determine file path
    let file_path = if let Some(p) = path {
        // Save backup if file exists
        if p.exists() {
            let version_id = vault.save(&p, Some("Auto-backup before editing".to_string()))?;
            println!("{} Created backup: {}", "✓".green(), version_id);
        }
        p
    } else {
        // Create temporary file in vault
        let tmp_dir = vault.root.join("tmp");
        std::fs::create_dir_all(&tmp_dir)?;
        let tmp_file = tmp_dir.join(format!("tmp_{}.hlx", chrono::Local::now().format("%Y%m%d_%H%M%S")));
        std::fs::write(&tmp_file, "")?;
        tmp_file
    };
    
    // Get editor command
    let use_fallback = editor.is_none();
    let editor_cmd = editor.unwrap_or_else(get_editor);
    
    // Launch editor
    println!("{} Opening {} with {}", "→".blue(), file_path.display(), editor_cmd);
    let status = if !use_fallback {
        // Use specified editor
        Command::new(&editor_cmd)
            .arg(&file_path)
            .status()
            .map_err(|e| VaultError::Config(format!("Failed to launch editor '{}': {}", editor_cmd, e)))?
    } else {
        // Use fallback system
        open_editor_with_fallback(&file_path.to_string_lossy())
            .map_err(|e| VaultError::Config(format!("Failed to launch editor: {}", e)))?
    };
    
    if !status.success() {
        return Err(VaultError::Config(format!("Editor '{}' exited with error", editor_cmd)));
    }
    
    // After editor closes, save if file was modified
    if file_path.exists() {
        let metadata = std::fs::metadata(&file_path)?;
        if metadata.modified()?.elapsed().unwrap().as_secs() < 5 {
            let version_id = vault.save(&file_path, Some("Saved after editing".to_string()))?;
            println!("{} Saved version: {}", "✓".green(), version_id);
        } else {
            println!("{} No changes detected", "→".yellow());
        }
    }
    
    Ok(())
}

fn save_file(path: PathBuf, description: Option<String>) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    
    if !path.exists() {
        return Err(VaultError::FileNotFound(path.to_string_lossy().to_string()));
    }
    
    let version_id = vault.save(&path, description)?;
    println!("{} Saved {} as version {}", "✓".green(), path.display(), version_id);
    
    Ok(())
}

fn show_history(path: PathBuf, limit: usize, long: bool) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    
    let versions = vault.list_versions(&path)?;
    if versions.is_empty() {
        println!("{} No versions found for {}", "→".yellow(), path.display());
        return Ok(());
    }
    
    println!("{} Version history for {}", "→".blue(), path.display());
    println!();
    
    let start = versions.len().saturating_sub(limit);
    for (i, version) in versions[start..].iter().enumerate() {
        if long {
            println!("{} {} {}", 
                if i == versions[start..].len() - 1 { "●".green() } else { "○".white() },
                version.id.bright_white(),
                version.created_at.format("%Y-%m-%d %H:%M:%S").to_string().dimmed()
            );
            println!("  {} Size: {} bytes", "│".dimmed(), version.size);
            if let Some(desc) = &version.description {
                println!("  {} {}", "│".dimmed(), desc.italic());
            }
            if version.compressed {
                println!("  {} {}", "│".dimmed(), "Compressed".yellow());
            }
            println!();
        } else {
            println!("{} {} {} {}",
                if i == versions[start..].len() - 1 { "●".green() } else { "○".white() },
                version.id,
                version.created_at.format("%Y-%m-%d %H:%M:%S").to_string().dimmed(),
                version.description.as_deref().unwrap_or("").italic()
            );
        }
    }
    
    if versions.len() > limit {
        println!("... {} more versions (use -n to show more)", versions.len() - limit);
    }
    
    Ok(())
}

fn revert_file(path: PathBuf, version: String, force: bool) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    
    if !force {
        print!("{} Revert {} to version {}? [y/N] ", "?".yellow(), path.display(), version);
        std::io::Write::flush(&mut std::io::stdout())?;
        
        let mut input = String::new();
        std::io::stdin().read_line(&mut input)?;
        
        if !input.trim().eq_ignore_ascii_case("y") {
            println!("{} Cancelled", "×".red());
            return Ok(());
        }
    }
    
    vault.revert(&path, &version)?;
    println!("{} Reverted {} to version {}", "✓".green(), path.display(), version);
    
    Ok(())
}

fn show_diff(path: PathBuf, from: Option<String>, to: Option<String>) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    
    // Get file hash for loading versions
    let file_hash = if path.exists() {
        let content = std::fs::read(&path)?;
        let mut hasher = sha2::Sha256::new();
        use sha2::Digest;
        hasher.update(&content);
        format!("{:x}", hasher.finalize())
    } else {
        return Err(VaultError::FileNotFound(path.to_string_lossy().to_string()));
    };
    
    let versions = vault.list_versions(&path)?;
    if versions.is_empty() {
        println!("{} No versions found for {}", "→".yellow(), path.display());
        return Ok(());
    }
    
    // Determine versions to compare
    let from_version = from.as_deref().unwrap_or("current");
    let to_version = to.as_deref().unwrap_or(&versions.last().unwrap().id);
    
    // Load content
    let from_content = if from_version == "current" {
        std::fs::read_to_string(&path)?
    } else {
        String::from_utf8(vault.load_version(&file_hash, from_version)?).map_err(|e| VaultError::Config(format!("Invalid UTF-8: {}", e)))?
    };
    
    let to_content = String::from_utf8(vault.load_version(&file_hash, to_version)?).map_err(|e| VaultError::Config(format!("Invalid UTF-8: {}", e)))?;
    
    // Simple diff display
    println!("{} Diff {} → {}", "→".blue(), from_version, to_version);
    println!();
    
    let from_lines: Vec<&str> = from_content.lines().collect();
    let to_lines: Vec<&str> = to_content.lines().collect();
    
    let max_lines = from_lines.len().max(to_lines.len());
    for i in 0..max_lines {
        match (from_lines.get(i), to_lines.get(i)) {
            (Some(f), Some(t)) if f != t => {
                println!("{} {}", "-".red(), f.red());
                println!("{} {}", "+".green(), t.green());
            }
            (Some(f), None) => println!("{} {}", "-".red(), f.red()),
            (None, Some(t)) => println!("{} {}", "+".green(), t.green()),
            _ => {}
        }
    }
    
    Ok(())
}

fn manage_config(
    show: bool,
    compress: Option<bool>,
    retention_days: Option<u32>,
    max_versions: Option<u32>,
    editor: Option<String>,
) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    let config_path = vault.root.join("config.hlx");
    
    if show || (compress.is_none() && retention_days.is_none() && max_versions.is_none() && editor.is_none()) {
        // Show current config
        println!("{} Current vault configuration:", "→".blue());
        println!();
        println!("  Compression: {}", vault.config.compress);
        println!("  Auto-save interval: {} minutes", vault.config.auto_save_interval);
        println!("  Max versions: {}", if vault.config.max_versions == 0 { "unlimited".to_string() } else { vault.config.max_versions.to_string() });
        println!("  Retention days: {}", vault.config.retention_days);
        println!("  Editor: {}", vault.config.editor);
        return Ok(());
    }
    
    // Build updated config if any changes requested
    if compress.is_some() || retention_days.is_some() || max_versions.is_some() || editor.is_some() {
        // Create new config with updated values
        let current_config = vault.config.clone();
        let new_compress = compress.unwrap_or(current_config.compress);
        let new_retention = retention_days.unwrap_or(current_config.retention_days);
        let new_max_versions = max_versions.unwrap_or(current_config.max_versions);
        let new_editor = editor.unwrap_or_else(|| current_config.editor.clone());
        let new_auto_save = current_config.auto_save_interval;
        
        // Write updated config in HLX format
        let mut content = String::new();
        content.push_str("vault :\n");
        content.push_str(&format!("    compress = {}\n", new_compress));
        content.push_str(&format!("    auto_save_interval = {}\n", new_auto_save));
        content.push_str(&format!("    max_versions = {}\n", new_max_versions));
        content.push_str(&format!("    retention_days = {}\n", new_retention));
        content.push_str(&format!("    editor = \"{}\"\n", new_editor));
        content.push_str(";\n");
        
        std::fs::write(&config_path, content)?;
        println!("{} Configuration updated", "✓".green());
    }
    
    Ok(())
}

fn garbage_collect(dry_run: bool, force: bool) -> Result<(), VaultError> {
    let vault = Vault::new()?;
    
    if !force && !dry_run {
        print!("{} Run garbage collection? This will delete old versions. [y/N] ", "?".yellow());
        std::io::Write::flush(&mut std::io::stdout())?;
        
        let mut input = String::new();
        std::io::stdin().read_line(&mut input)?;
        
        if !input.trim().eq_ignore_ascii_case("y") {
            println!("{} Cancelled", "×".red());
            return Ok(());
        }
    }
    
    if dry_run {
        println!("{} Running garbage collection (dry run)...", "→".blue());
        // TODO: Implement dry run logic
        println!("{} Would remove X versions older than {} days", "→".yellow(), vault.config.retention_days);
    } else {
        println!("{} Running garbage collection...", "→".blue());
        let removed = vault.garbage_collect()?;
        println!("{} Removed {} old versions", "✓".green(), removed);
    }
    
    Ok(())
}
