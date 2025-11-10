use std::path::Path;
use anyhow::{Context, Result};
use serde_json::Value;
use tokio::fs;
use log::info;

/// Processes a SafeTensors file by extracting its metadata and saving it as JSON
///
/// This function reads the metadata from a SafeTensors file using memory mapping
/// for efficient access, converts it to JSON format, and writes it to a .json file
/// with the same base name as the input file.
///
/// # Arguments
/// * `file` - Path to the SafeTensors file to process
///
/// # Returns
/// Returns `Ok(())` on success, or an error if file operations fail
///
/// # Example
/// ```rust,no_run
/// use std::path::Path;
/// use helix::dna::map::process_safetensors_file;
///
/// # async fn example() -> Result<(), Box<dyn std::error::Error>> {
/// let path = Path::new("model.safetensors");
/// process_safetensors_file(path).await?;
/// # Ok(())
/// # }
/// ```
pub async fn process_safetensors_file(file: &Path) -> Result<()> {
    // Extract metadata from the SafeTensors file
    let json = get_json_metadata(file)?;

    // Convert to pretty-printed JSON
    let pretty_json = serde_json::to_string_pretty(&json)
        .context("Failed to serialize metadata to JSON")?;

    // Log the metadata for debugging
    info!("Extracted metadata: {}", pretty_json);

    // Write to a .json file with the same base name
    let output_path = file.with_extension("json");
    fs::write(&output_path, pretty_json).await
        .with_context(|| format!("Failed to write metadata to {}", output_path.display()))?;

    info!("Successfully processed SafeTensors file: {} -> {}",
          file.display(), output_path.display());

    Ok(())
}

/// Internal function to extract JSON metadata from a SafeTensors file
fn get_json_metadata(path: &Path) -> Result<Value> {
    use safetensors::SafeTensors;
    use memmap2::MmapOptions;
    use std::fs::File;

    // Open the file
    let file = File::open(path)
        .with_context(|| format!("Failed to open SafeTensors file: {}", path.display()))?;

    // Memory map the file for efficient reading
    let mmap = unsafe {
        MmapOptions::new().map(&file)
            .with_context(|| format!("Failed to memory map file: {}", path.display()))?
    };

    // Read SafeTensors metadata
    let (_header_size, metadata) = SafeTensors::read_metadata(&mmap)
        .with_context(|| format!("Failed to read SafeTensors metadata from: {}", path.display()))?;

    // Convert metadata to JSON value
    let metadata_json: Value = serde_json::to_value(&metadata)
        .context("Failed to convert metadata to JSON value")?;

    // Extract training-specific metadata if available
    let training_metadata = crate::metadata::extract_training_metadata(&metadata_json);

    Ok(training_metadata)
}
