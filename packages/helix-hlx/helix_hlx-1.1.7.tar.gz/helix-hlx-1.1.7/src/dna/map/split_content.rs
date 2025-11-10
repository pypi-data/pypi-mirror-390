/// Splits content into tags and sentences based on a specific format
///
/// This function expects content in the format "tag1, tag2, tag3., sentence text"
/// where tags are separated by commas and followed by "., " then the sentence text.
///
/// # Arguments
/// * `content` - The content string to split
///
/// # Returns
/// A tuple containing:
/// - `Vec<String>`: The parsed tags
/// - `String`: The sentence text (everything after "., ")
///
/// # Examples
/// ```
/// use helix::dna::map::split_content;
///
/// let (tags, sentence) = split_content("cat, dog, bird., This is a sentence about animals");
/// assert_eq!(tags, vec!["cat", "dog", "bird"]);
/// assert_eq!(sentence, "This is a sentence about animals");
/// ```
pub fn split_content(content: &str) -> (Vec<String>, String) {
    // Split on the delimiter "., " which separates tags from sentences
    let split: Vec<&str> = content.split("., ").collect();

    // Parse tags from the first part (before "., ")
    let tags: Vec<String> = split[0]
        .split(',')
        .map(str::trim)
        .map(String::from)
        .collect();

    // Get the sentence from the second part (after "., ")
    let sentence = split
        .get(1)
        .unwrap_or(&"")
        .trim()
        .to_string();

    (tags, sentence)
}
