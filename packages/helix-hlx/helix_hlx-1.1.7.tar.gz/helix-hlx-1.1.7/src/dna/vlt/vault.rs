//! Vault (vlt) - Version control for HLX files
//! 
//! Provides automatic versioning and backup functionality for HLX configuration files.
//! Files are stored in `~/.dna/vlt/` with hash-based organization.

use std::collections::HashMap;
use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::time::SystemTime;
use chrono::{DateTime, Local, Utc};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};

/// Version control system for HLX files
pub struct Vault {
    /// Root directory for vault storage
    pub root: PathBuf,
    /// Configuration settings
    pub config: VaultConfig,
}

/// Vault configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultConfig {
    /// Enable compression for stored files
    #[serde(default)]
    pub compress: bool,
    /// Auto-save interval in minutes (0 = disabled)
    #[serde(default)]
    pub auto_save_interval: u32,
    /// Maximum versions to keep (0 = unlimited)
    #[serde(default)]
    pub max_versions: u32,
    /// Days to keep old versions before GC
    #[serde(default = "default_retention_days")]
    pub retention_days: u32,
    /// Default editor command
    #[serde(default = "default_editor")]
    pub editor: String,
}

fn default_retention_days() -> u32 { 30 }
fn default_editor() -> String { "vim".to_string() }

impl Default for VaultConfig {
    fn default() -> Self {
        Self {
            compress: false,
            auto_save_interval: 0,
            max_versions: 0,
            retention_days: default_retention_days(),
            editor: default_editor(),
        }
    }
}

/// Manifest for tracking file versions
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Manifest {
    /// Original file path
    pub original_path: Option<String>,
    /// File hash (SHA-256)
    pub file_hash: String,
    /// List of versions
    pub versions: Vec<Version>,
    /// Metadata
    pub metadata: HashMap<String, String>,
}

/// Individual version entry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Version {
    /// Version ID (timestamp-based)
    pub id: String,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// File size in bytes
    pub size: u64,
    /// Optional description
    pub description: Option<String>,
    /// Checksum of this version
    pub checksum: String,
    /// Is this version compressed?
    #[serde(default)]
    pub compressed: bool,
}

/// Result type for vault operations
pub type VaultResult<T> = Result<T, VaultError>;

/// Vault-specific errors
#[derive(Debug, thiserror::Error)]
pub enum VaultError {
    #[error("IO error: {0}")]
    Io(#[from] io::Error),
    
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    
    #[error("File not found in vault: {0}")]
    FileNotFound(String),
    
    #[error("Version not found: {0}")]
    VersionNotFound(String),
    
    #[error("Invalid file hash: {0}")]
    InvalidHash(String),
    
    #[error("Configuration error: {0}")]
    Config(String),
}

impl Vault {
    /// Create a new vault instance
    pub fn new() -> VaultResult<Self> {
        let root = Self::get_vault_dir()?;
        let config = Self::load_config(&root)?;
        
        Ok(Self { root, config })
    }
    
    /// Get the vault directory, creating if necessary
    fn get_vault_dir() -> VaultResult<PathBuf> {
        let home = std::env::var("HOME")
            .or_else(|_| std::env::var("USERPROFILE"))
            .map_err(|_| VaultError::Config("Cannot determine home directory".to_string()))?;
        
        let vault_dir = PathBuf::from(home).join(".dna").join("vlt");
        
        // Create directory structure
        fs::create_dir_all(&vault_dir)?;
        fs::create_dir_all(vault_dir.join("vlt"))?;
        fs::create_dir_all(vault_dir.join("tmp"))?;
        fs::create_dir_all(vault_dir.join("log"))?;
        fs::create_dir_all(vault_dir.join("bny"))?;
        
        Ok(vault_dir)
    }
    
    /// Load vault configuration using HLX format
    fn load_config(root: &Path) -> VaultResult<VaultConfig> {
        let config_path = root.join("config.hlx");
        
        if config_path.exists() {
            // For now, parse the HLX file manually to avoid async issues
            let content = std::fs::read_to_string(&config_path)
                .map_err(|e| VaultError::Config(format!("Failed to read config: {}", e)))?;
            
            // Simple parsing - look for vault section
            let mut config = VaultConfig::default();
            
            // This is a simplified parser - in production you'd use the full HLX parser
            for line in content.lines() {
                let line = line.trim();
                if line.contains("compress") && line.contains("true") {
                    config.compress = true;
                }
                if let Some(pos) = line.find("retention_days") {
                    if let Some(eq_pos) = line[pos..].find('=') {
                        let value_str = line[pos + eq_pos + 1..].trim();
                        if let Ok(days) = value_str.parse::<u32>() {
                            config.retention_days = days;
                        }
                    }
                }
                // Similar parsing for other fields...
            }
            
            Ok(config)
        } else {
            // Create default config
            let config = VaultConfig::default();
            
            // Write config in HLX format
            let mut content = String::new();
            content.push_str("vault :\n");
            content.push_str(&format!("    compress = {}\n", config.compress));
            content.push_str(&format!("    auto_save_interval = {}\n", config.auto_save_interval));
            content.push_str(&format!("    max_versions = {}\n", config.max_versions));
            content.push_str(&format!("    retention_days = {}\n", config.retention_days));
            content.push_str(&format!("    editor = \"{}\"\n", config.editor));
            content.push_str(";\n");
            
            std::fs::write(&config_path, content)?;
            
            Ok(config)
        }
    }
    
    /// Calculate file hash
    fn hash_file(path: &Path) -> VaultResult<String> {
        let content = fs::read(path)?;
        let mut hasher = Sha256::new();
        hasher.update(&content);
        Ok(format!("{:x}", hasher.finalize()))
    }
    
    /// Get version directory for a file
    fn get_version_dir(&self, file_hash: &str) -> PathBuf {
        self.root.join("vlt").join(file_hash)
    }
    
    /// Save a file to the vault
    pub fn save(&self, path: &Path, description: Option<String>) -> VaultResult<String> {
        // Calculate file hash
        let file_hash = Self::hash_file(path)?;
        let version_dir = self.get_version_dir(&file_hash);
        
        // Create version directory if needed
        fs::create_dir_all(&version_dir)?;
        
        // Generate version ID with microseconds to avoid duplicates
        let now = Local::now();
        let version_id = now.format("%Y%m%dT%H%M%S%3f").to_string();
        let version_file = version_dir.join(format!("{}.hlx", version_id));
        
        // Make sure the file doesn't exist (wait if necessary)
        let mut counter = 0;
        while version_file.exists() && counter < 10 {
            std::thread::sleep(std::time::Duration::from_millis(10));
            counter += 1;
        }
        
        // Read file content
        let content = fs::read(path)?;
        let size = content.len() as u64;
        
        // Optionally compress
        let (final_content, compressed) = if self.config.compress {
            use flate2::write::GzEncoder;
            use flate2::Compression;
            
            let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
            encoder.write_all(&content)?;
            (encoder.finish()?, true)
        } else {
            (content, false)
        };
        
        // Write version file
        fs::write(&version_file, &final_content)?;
        
        // Calculate checksum of stored content
        let mut hasher = Sha256::new();
        hasher.update(&final_content);
        let checksum = format!("{:x}", hasher.finalize());
        
        // Update manifest
        let manifest_path = version_dir.join("manifest.json");
        let mut manifest = if manifest_path.exists() {
            let content = fs::read_to_string(&manifest_path)?;
            serde_json::from_str(&content)?
        } else {
            Manifest {
                original_path: Some(path.to_string_lossy().to_string()),
                file_hash: file_hash.clone(),
                versions: Vec::new(),
                metadata: HashMap::new(),
            }
        };
        
        // Add new version
        manifest.versions.push(Version {
            id: version_id.clone(),
            created_at: now.with_timezone(&Utc),
            size,
            description,
            checksum,
            compressed,
        });
        
        // Enforce max versions if configured
        if self.config.max_versions > 0 && manifest.versions.len() > self.config.max_versions as usize {
            let to_remove = manifest.versions.len() - self.config.max_versions as usize;
            for version in manifest.versions.drain(..to_remove) {
                let old_file = version_dir.join(format!("{}.hlx", version.id));
                let _ = fs::remove_file(old_file);
            }
        }
        
        // Save manifest
        let manifest_content = serde_json::to_string_pretty(&manifest)?;
        fs::write(&manifest_path, manifest_content)?;
        
        Ok(version_id)
    }
    
    /// Load the latest version of a file
    pub fn load_latest(&self, path: &Path) -> VaultResult<Vec<u8>> {
        let file_hash = Self::hash_file(path)?;
        let version_dir = self.get_version_dir(&file_hash);
        let manifest_path = version_dir.join("manifest.json");
        
        if !manifest_path.exists() {
            return Err(VaultError::FileNotFound(path.to_string_lossy().to_string()));
        }
        
        let manifest: Manifest = serde_json::from_str(&fs::read_to_string(&manifest_path)?)?;
        
        let latest = manifest.versions.last()
            .ok_or_else(|| VaultError::FileNotFound("No versions found".to_string()))?;
        
        self.load_version(&file_hash, &latest.id)
    }
    
    /// Load a specific version
    pub fn load_version(&self, file_hash: &str, version_id: &str) -> VaultResult<Vec<u8>> {
        let version_dir = self.get_version_dir(file_hash);
        let manifest_path = version_dir.join("manifest.json");
        
        if !manifest_path.exists() {
            return Err(VaultError::FileNotFound(file_hash.to_string()));
        }
        
        let manifest: Manifest = serde_json::from_str(&fs::read_to_string(&manifest_path)?)?;
        
        let version = manifest.versions.iter()
            .find(|v| v.id == version_id)
            .ok_or_else(|| VaultError::VersionNotFound(version_id.to_string()))?;
        
        let version_file = version_dir.join(format!("{}.hlx", version_id));
        let content = fs::read(&version_file)?;
        
        // Decompress if needed
        if version.compressed {
            use flate2::read::GzDecoder;
            use std::io::Read;
            
            let mut decoder = GzDecoder::new(&content[..]);
            let mut decompressed = Vec::new();
            decoder.read_to_end(&mut decompressed)?;
            Ok(decompressed)
        } else {
            Ok(content)
        }
    }
    
    /// List all versions of a file
    pub fn list_versions(&self, path: &Path) -> VaultResult<Vec<Version>> {
        // Search by path in all manifests
        let vlt_dir = self.root.join("vlt");
        if !vlt_dir.exists() {
            return Ok(Vec::new());
        }
        
        // Collect all versions for this file across all hashes
        let mut all_versions = Vec::new();
        let path_string = path.to_string_lossy().to_string();
        
        for entry in fs::read_dir(&vlt_dir)? {
            let entry = entry?;
            if entry.path().is_dir() {
                let manifest_path = entry.path().join("manifest.json");
                if manifest_path.exists() {
                    let content = fs::read_to_string(&manifest_path)?;
                    let manifest: Manifest = serde_json::from_str(&content)?;
                    
                    // Check if this manifest is for our file
                    if let Some(orig_path) = &manifest.original_path {
                        if orig_path == &path_string {
                            all_versions.extend(manifest.versions);
                        }
                    }
                }
            }
        }
        
        // Sort by creation time
        all_versions.sort_by(|a, b| a.created_at.cmp(&b.created_at));
        
        Ok(all_versions)
    }
    
    /// Revert a file to a specific version
    pub fn revert(&self, path: &Path, version_id: &str) -> VaultResult<()> {
        // Find the version across all manifests
        let vlt_dir = self.root.join("vlt");
        if !vlt_dir.exists() {
            return Err(VaultError::FileNotFound(path.to_string_lossy().to_string()));
        }
        
        let path_string = path.to_string_lossy().to_string();
        
        for entry in fs::read_dir(&vlt_dir)? {
            let entry = entry?;
            if entry.path().is_dir() {
                let manifest_path = entry.path().join("manifest.json");
                if manifest_path.exists() {
                    let content = fs::read_to_string(&manifest_path)?;
                    let manifest: Manifest = serde_json::from_str(&content)?;
                    
                    // Check if this manifest is for our file
                    if let Some(orig_path) = &manifest.original_path {
                        if orig_path == &path_string {
                            // Check if this manifest contains the version we want
                            if manifest.versions.iter().any(|v| v.id == version_id) {
                                // Found the right manifest and version
                                let content = self.load_version(&manifest.file_hash, version_id)?;
                                
                                // Create backup of current version before reverting
                                if path.exists() {
                                    let _ = self.save(path, Some(format!("Before revert to {}", version_id)));
                                }
                                
                                // Write reverted content
                                fs::write(path, content)?;
                                return Ok(());
                            }
                        }
                    }
                }
            }
        }
        
        Err(VaultError::VersionNotFound(version_id.to_string()))
    }
    
    /// Get editor command from config or environment
    pub fn get_editor(&self) -> String {
        std::env::var("HLX_EDITOR")
            .or_else(|_| std::env::var("EDITOR"))
            .unwrap_or_else(|_| self.config.editor.clone())
    }
    
    /// Clean up old versions based on retention policy
    pub fn garbage_collect(&self) -> VaultResult<usize> {
        let mut removed_count = 0;
        let vlt_dir = self.root.join("vlt");
        
        if !vlt_dir.exists() {
            return Ok(0);
        }
        
        let cutoff = SystemTime::now()
            .checked_sub(std::time::Duration::from_secs(
                self.config.retention_days as u64 * 24 * 60 * 60
            ))
            .ok_or_else(|| VaultError::Config("Invalid retention days".to_string()))?;
        
        for entry in fs::read_dir(&vlt_dir)? {
            let entry = entry?;
            if !entry.path().is_dir() {
                continue;
            }
            
            let manifest_path = entry.path().join("manifest.json");
            if !manifest_path.exists() {
                continue;
            }
            
            let content = fs::read_to_string(&manifest_path)?;
            let mut manifest: Manifest = serde_json::from_str(&content)?;
            let original_count = manifest.versions.len();
            
            // Remove old versions
            manifest.versions.retain(|v| {
                let keep = v.created_at.timestamp() as u64 > cutoff.duration_since(SystemTime::UNIX_EPOCH).unwrap().as_secs();
                if !keep {
                    let version_file = entry.path().join(format!("{}.hlx", v.id));
                    let _ = fs::remove_file(version_file);
                    removed_count += 1;
                }
                keep
            });
            
            // Update manifest if versions were removed
            if manifest.versions.len() < original_count {
                if manifest.versions.is_empty() {
                    // Remove empty directories
                    let _ = fs::remove_file(&manifest_path);
                    let _ = fs::remove_dir(entry.path());
                } else {
                    let manifest_content = serde_json::to_string_pretty(&manifest)?;
                    fs::write(&manifest_path, manifest_content)?;
                }
            }
        }
        
        Ok(removed_count)
    }
    
    /// Add agent (Ruby binding stub)
    pub async fn add_agent<T, U>(_agent: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add context (Ruby binding stub)
    pub async fn add_context<T, U>(_context: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add crew (Ruby binding stub)
    pub async fn add_crew<T, U>(_crew: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add database (Ruby binding stub)
    pub async fn add_database<T, U>(_database: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add load (Ruby binding stub)
    pub async fn add_load<T, U>(_load: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add memory (Ruby binding stub)
    pub async fn add_memory<T, U>(_memory: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add pipeline (Ruby binding stub)
    pub async fn add_pipeline<T, U>(_pipeline: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add plugin (Ruby binding stub)
    pub async fn add_plugin<T, U>(_plugin: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add section (Ruby binding stub)
    pub async fn add_section<T, U>(_section: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add workflow (Ruby binding stub)
    pub async fn add_workflow<T, U>(_workflow: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
    
    /// Add row (Ruby binding stub)
    pub async fn add_row<T, U>(_row: T, _ruby: U) -> VaultResult<()> {
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    
    #[test]
    fn test_vault_creation() {
        let temp_dir = TempDir::new().unwrap();
        std::env::set_var("HOME", temp_dir.path());
        
        let vault = Vault::new().unwrap();
        assert!(vault.root.exists());
        assert!(vault.root.join("vlt").exists());
        assert!(vault.root.join("tmp").exists());
        assert!(vault.root.join("log").exists());
        assert!(vault.root.join("bny").exists());
    }
}
