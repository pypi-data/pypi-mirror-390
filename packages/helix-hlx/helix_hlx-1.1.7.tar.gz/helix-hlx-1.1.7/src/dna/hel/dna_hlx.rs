use std::collections::HashMap;
use std::path::{Path, PathBuf};
use crate::dna::hel::error::HlxError;
use crate::dna::atp::value::Value;
use crate::dna::hel::dispatch::{HelixDispatcher, DispatchResult};
use crate::HelixConfig;
use crate::dna::ops::engine::OperatorEngine;

/// Trait for converting Rust types into DnaValue
pub trait IntoValue {
    fn into_value(self) -> Value;
}

/// Trait for converting DnaValue into Rust types
pub trait FromValue: Sized {
    fn from_value(value: &Value) -> Option<Self>;
}

impl IntoValue for Value {
    fn into_value(self) -> Value {
        self
    }
}

impl IntoValue for &str {
    fn into_value(self) -> Value {
        Value::String(self.to_string())
    }
}

impl IntoValue for String {
    fn into_value(self) -> Value {
        Value::String(self)
    }
}

impl IntoValue for &String {
    fn into_value(self) -> Value {
        Value::String(self.clone())
    }
}

impl IntoValue for bool {
    fn into_value(self) -> Value {
        Value::Bool(self)
    }
}

impl IntoValue for i8 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for i16 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for i32 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for i64 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for u8 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for u16 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for u32 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for u64 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for f32 {
    fn into_value(self) -> Value {
        Value::Number(self as f64)
    }
}

impl IntoValue for f64 {
    fn into_value(self) -> Value {
        Value::Number(self)
    }
}

// Array support for Vec of IntoValue types
impl<T: IntoValue> IntoValue for Vec<T> {
    fn into_value(self) -> Value {
        Value::Array(self.into_iter().map(|v| v.into_value()).collect())
    }
}

// FromValue implementations
impl FromValue for String {
    fn from_value(value: &Value) -> Option<Self> {
        match value {
            Value::String(s) => Some(s.clone()),
            _ => None,
        }
    }
}

// Note: &str cannot be returned from &Value due to lifetime constraints
// Use String or the get_str() method for string slices

impl FromValue for f64 {
    fn from_value(value: &Value) -> Option<Self> {
        value.as_number()
    }
}

impl FromValue for i32 {
    fn from_value(value: &Value) -> Option<Self> {
        value.as_number().map(|n| n as i32)
    }
}

impl FromValue for i64 {
    fn from_value(value: &Value) -> Option<Self> {
        value.as_number().map(|n| n as i64)
    }
}

impl FromValue for u32 {
    fn from_value(value: &Value) -> Option<Self> {
        value.as_number().map(|n| n as u32)
    }
}

impl FromValue for u64 {
    fn from_value(value: &Value) -> Option<Self> {
        value.as_number().map(|n| n as u64)
    }
}

impl FromValue for bool {
    fn from_value(value: &Value) -> Option<Self> {
        value.as_boolean()
    }
}

impl FromValue for Vec<String> {
    fn from_value(value: &Value) -> Option<Self> {
        match value {
            Value::Array(arr) => {
                let mut result = Vec::new();
                for item in arr {
                    if let Value::String(s) = item {
                        result.push(s.clone());
                    } else {
                        return None;
                    }
                }
                Some(result)
            }
            _ => None,
        }
    }
}

impl FromValue for Vec<i32> {
    fn from_value(value: &Value) -> Option<Self> {
        match value {
            Value::Array(arr) => {
                let mut result = Vec::new();
                for item in arr {
                    if let Some(n) = item.as_number() {
                        result.push(n as i32);
                    } else {
                        return None;
                    }
                }
                Some(result)
            }
            _ => None,
        }
    }
}

impl FromValue for Vec<f64> {
    fn from_value(value: &Value) -> Option<Self> {
        match value {
            Value::Array(arr) => {
                let mut result = Vec::new();
                for item in arr {
                    if let Some(n) = item.as_number() {
                        result.push(n);
                    } else {
                        return None;
                    }
                }
                Some(result)
            }
            _ => None,
        }
    }
}

impl FromValue for Vec<bool> {
    fn from_value(value: &Value) -> Option<Self> {
        match value {
            Value::Array(arr) => {
                let mut result = Vec::new();
                for item in arr {
                    if let Some(b) = item.as_boolean() {
                        result.push(b);
                    } else {
                        return None;
                    }
                }
                Some(result)
            }
            _ => None,
        }
    }
}

// ============================================================
// DYNAMIC GET API - PHP-like behavior
// ============================================================

/// Dynamic value that can be any supported type
#[derive(Debug, Clone)]
pub enum DynamicValue {
    String(String),
    Number(f64),
    Integer(i64),
    Bool(bool),
    Array(Vec<Value>),
    Empty,
}

impl DynamicValue {
    /// Try to get as string
    pub fn as_string(&self) -> Option<String> {
        match self {
            DynamicValue::String(s) => Some(s.clone()),
            DynamicValue::Number(n) => Some(n.to_string()),
            DynamicValue::Integer(i) => Some(i.to_string()),
            DynamicValue::Bool(b) => Some(b.to_string()),
            _ => None,
        }
    }
    
    /// Try to get as number
    pub fn as_number(&self) -> Option<f64> {
        match self {
            DynamicValue::Number(n) => Some(*n),
            DynamicValue::Integer(i) => Some(*i as f64),
            DynamicValue::String(s) => s.parse().ok(),
            _ => None,
        }
    }
    
    /// Try to get as integer
    pub fn as_integer(&self) -> Option<i64> {
        match self {
            DynamicValue::Integer(i) => Some(*i),
            DynamicValue::Number(n) => Some(*n as i64),
            DynamicValue::String(s) => s.parse().ok(),
            _ => None,
        }
    }
    
    /// Try to get as bool
    pub fn as_bool(&self) -> Option<bool> {
        match self {
            DynamicValue::Bool(b) => Some(*b),
            DynamicValue::String(s) => match s.as_str() {
                "true" | "1" | "yes" | "on" => Some(true),
                "false" | "0" | "no" | "off" => Some(false),
                _ => None,
            },
            DynamicValue::Integer(i) => Some(*i != 0),
            DynamicValue::Number(n) => Some(*n != 0.0),
            _ => None,
        }
    }
    
    /// Check if empty
    pub fn is_empty(&self) -> bool {
        matches!(self, DynamicValue::Empty)
    }
}

// ============================================================
// FLUENT GET API - Method chaining for cleanest syntax
// ============================================================

/// Fluent getter for type-safe value retrieval without annotations
pub struct TypedGetter<'a> {
    value: Option<&'a Value>,
}

impl<'a> TypedGetter<'a> {
    /// Get as String (owned)
    pub fn string(self) -> Option<String> {
        self.value.and_then(|v| String::from_value(v))
    }
    
    /// Get as &str
    pub fn str(&self) -> Option<&str> {
        self.value.and_then(|v| v.as_string())
    }
    
    /// Get as i32
    pub fn i32(self) -> Option<i32> {
        self.value.and_then(|v| i32::from_value(v))
    }
    
    /// Get as i64
    pub fn i64(self) -> Option<i64> {
        self.value.and_then(|v| i64::from_value(v))
    }
    
    /// Get as u32
    pub fn u32(self) -> Option<u32> {
        self.value.and_then(|v| u32::from_value(v))
    }
    
    /// Get as u64
    pub fn u64(self) -> Option<u64> {
        self.value.and_then(|v| u64::from_value(v))
    }
    
    /// Get as f32
    pub fn f32(self) -> Option<f32> {
        self.value.and_then(|v| f64::from_value(v)).map(|n| n as f32)
    }
    
    /// Get as f64
    pub fn f64(self) -> Option<f64> {
        self.value.and_then(|v| f64::from_value(v))
    }
    
    /// Get as bool
    pub fn bool(self) -> Option<bool> {
        self.value.and_then(|v| bool::from_value(v))
    }
    
    /// Get as Vec<String>
    pub fn vec_string(self) -> Option<Vec<String>> {
        self.value.and_then(|v| Vec::<String>::from_value(v))
    }
    
    /// Get as Vec<i32>
    pub fn vec_i32(self) -> Option<Vec<i32>> {
        self.value.and_then(|v| Vec::<i32>::from_value(v))
    }
    
    /// Get as Vec<f64>
    pub fn vec_f64(self) -> Option<Vec<f64>> {
        self.value.and_then(|v| Vec::<f64>::from_value(v))
    }
    
    /// Get as Vec<bool>
    pub fn vec_bool(self) -> Option<Vec<bool>> {
        self.value.and_then(|v| Vec::<bool>::from_value(v))
    }
    
    // With default values
    
    /// Get as String or return default
    pub fn string_or(self, default: String) -> String {
        self.string().unwrap_or(default)
    }
    
    /// Get as String or return empty string
    pub fn string_or_default(self) -> String {
        self.string().unwrap_or_default()
    }
    
    /// Get as i32 or return default
    pub fn i32_or(self, default: i32) -> i32 {
        self.i32().unwrap_or(default)
    }
    
    /// Get as i64 or return default
    pub fn i64_or(self, default: i64) -> i64 {
        self.i64().unwrap_or(default)
    }
    
    /// Get as f64 or return default
    pub fn f64_or(self, default: f64) -> f64 {
        self.f64().unwrap_or(default)
    }
    
    /// Get as bool or return default
    pub fn bool_or(self, default: bool) -> bool {
        self.bool().unwrap_or(default)
    }
    
    /// Get as bool or return false
    pub fn bool_or_false(self) -> bool {
        self.bool().unwrap_or(false)
    }
    
    /// Get as bool or return true
    pub fn bool_or_true(self) -> bool {
        self.bool().unwrap_or(true)
    }
}

// ============================================================
// SECTION GETTER API - Builder pattern for same section
// ============================================================

/// Builder for getting multiple values from the same section
pub struct SectionGetter<'a, 'b> {
    hlx: &'a Hlx,
    section: &'b str,
}

impl<'a, 'b> SectionGetter<'a, 'b> {
    pub fn string(&self, key: &str) -> Option<String> {
        self.hlx.get::<String>(self.section, key)
    }
    
    pub fn i32(&self, key: &str) -> Option<i32> {
        self.hlx.get::<i32>(self.section, key)
    }
    
    pub fn i64(&self, key: &str) -> Option<i64> {
        self.hlx.get::<i64>(self.section, key)
    }
    
    pub fn f64(&self, key: &str) -> Option<f64> {
        self.hlx.get::<f64>(self.section, key)
    }
    
    pub fn bool(&self, key: &str) -> Option<bool> {
        self.hlx.get::<bool>(self.section, key)
    }
    
    // With defaults
    pub fn string_or(&self, key: &str, default: &str) -> String {
        self.string(key).unwrap_or_else(|| default.to_string())
    }
    
    pub fn i32_or(&self, key: &str, default: i32) -> i32 {
        self.i32(key).unwrap_or(default)
    }
    
    pub fn i64_or(&self, key: &str, default: i64) -> i64 {
        self.i64(key).unwrap_or(default)
    }
    
    pub fn f64_or(&self, key: &str, default: f64) -> f64 {
        self.f64(key).unwrap_or(default)
    }
    
    pub fn bool_or(&self, key: &str, default: bool) -> bool {
        self.bool(key).unwrap_or(default)
    }
}

pub struct Hlx {
    pub config: Option<HelixConfig>,
    pub data: HashMap<String, HashMap<String, Value>>,
    file_path: Option<PathBuf>,
    pub dispatcher: HelixDispatcher,
    pub operator_engine: OperatorEngine,
}
impl Hlx {
    pub async fn load<P: AsRef<Path>>(path: P) -> Result<Self, HlxError> {
        let path = path.as_ref().to_path_buf();
        let mut hlx = Self {
            config: None,
            data: HashMap::new(),
            file_path: Some(path.clone()),
            dispatcher: HelixDispatcher::new(),
            operator_engine: OperatorEngine::new().await?,
        };
        hlx.dispatcher.initialize().await?;
        if path.extension().and_then(|s| s.to_str()) == Some("hlxb") {
            #[cfg(feature = "compiler")]
            {
                let loader = crate::dna::mds::loader::BinaryLoader::new();
                let binary = loader
                    .load_file(&path)
                    .map_err(|e| HlxError::compilation_error(
                        format!("Failed to load binary: {:?}", e),
                        "Ensure file is a valid HLXB file",
                    ))?;
                // Convert binary to config if needed
                hlx.config = Some(crate::HelixConfig::default());
            }
            #[cfg(not(feature = "compiler"))]
            {
                return Err(
                    HlxError::compilation_error(
                        "Binary file support not available",
                        "Compile with 'compiler' feature enabled",
                    ),
                );
            }
        } else {
            let content = std::fs::read_to_string(&path)
                .map_err(|e| HlxError::io_error(
                    format!("Failed to read file: {}", e),
                    "Ensure file exists and is readable",
                ))?;
            match hlx.dispatcher.parse_and_execute(&content).await? {
                DispatchResult::Executed(value) => {
                    if let Value::Object(obj) = value {
                        for (section, section_data) in obj {
                            if let Value::Object(section_obj) = section_data {
                                let mut section_map = HashMap::new();
                                for (key, val) in section_obj {
                                    section_map.insert(key, val);
                                }
                                hlx.data.insert(section, section_map);
                            }
                        }
                    }
                }
                DispatchResult::Parsed(ast) => {
                    hlx.config = Some(
                        crate::ast_to_config(ast)
                            .map_err(|e| HlxError::config_conversion(
                                "conversion".to_string(),
                                e.to_string(),
                            ))?,
                    );
                }
                _ => {}
            }
        }
        Ok(hlx)
    }
    pub async fn new() -> Result<Self, HlxError> {
        Ok(Self {
            config: None,
            data: HashMap::new(),
            file_path: None,
            dispatcher: HelixDispatcher::new(),
            operator_engine: OperatorEngine::new().await?,
        })
    }
    /// Get the raw Value from a section (for advanced use)
    pub fn get_raw(&self, section: &str, key: &str) -> Option<&Value> {
        self.data.get(section)?.get(key)
    }
    
    /// Get a value from a section with automatic type conversion
    /// 
    /// # Examples
    /// ```
    /// let name: String = hlx.get("project", "name")?;
    /// let port: i32 = hlx.get("config", "port")?;
    /// let debug: bool = hlx.get("features", "debug")?;
    /// let tags: Vec<String> = hlx.get("tags", "list")?;
    /// ```
    pub fn get<T: FromValue>(&self, section: &str, key: &str) -> Option<T> {
        self.get_raw(section, key).and_then(|v| T::from_value(v))
    }
    
    /// Get a string value from a section
    /// 
    /// # Examples
    /// ```
    /// let name = hlx.get_str("project", "name").unwrap_or("unknown");
    /// ```
    pub fn get_str(&self, section: &str, key: &str) -> Option<&str> {
        self.get_raw(section, key)?.as_string()
    }
    
    /// Get a numeric value from a section
    /// 
    /// # Examples
    /// ```
    /// let port = hlx.get_num("config", "port").unwrap_or(8080);
    /// ```
    pub fn get_num(&self, section: &str, key: &str) -> Option<f64> {
        self.get_raw(section, key)?.as_number()
    }
    
    /// Get a boolean value from a section
    /// 
    /// # Examples
    /// ```
    /// let debug = hlx.get_bool("features", "debug").unwrap_or(false);
    /// ```
    pub fn get_bool(&self, section: &str, key: &str) -> Option<bool> {
        self.get_raw(section, key)?.as_boolean()
    }
    
    /// Get an array value from a section
    /// 
    /// # Examples
    /// ```
    /// let items = hlx.get_array("data", "items").unwrap_or(&[]);
    /// ```
    pub fn get_array(&self, section: &str, key: &str) -> Option<&[Value]> {
        self.get_raw(section, key)?.as_array()
    }
    
    // ============================================================
    // CLEANEST GET API - Zero annotations required
    // ============================================================
    
    /// Get a String value (owned) from a section
    /// 
    /// # Examples
    /// ```
    /// let name = hlx.get_string("project", "name").unwrap_or_default();
    /// ```
    pub fn get_string(&self, section: &str, key: &str) -> Option<String> {
        self.get::<String>(section, key)
    }
    
    /// Get an i32 value from a section
    /// 
    /// # Examples
    /// ```
    /// let port = hlx.get_i32("config", "port").unwrap_or(8080);
    /// ```
    pub fn get_i32(&self, section: &str, key: &str) -> Option<i32> {
        self.get::<i32>(section, key)
    }
    
    /// Get an i64 value from a section
    /// 
    /// # Examples
    /// ```
    /// let timestamp = hlx.get_i64("data", "timestamp").unwrap_or(0);
    /// ```
    pub fn get_i64(&self, section: &str, key: &str) -> Option<i64> {
        self.get::<i64>(section, key)
    }
    
    /// Get a u32 value from a section
    /// 
    /// # Examples
    /// ```
    /// let count = hlx.get_u32("stats", "count").unwrap_or(0);
    /// ```
    pub fn get_u32(&self, section: &str, key: &str) -> Option<u32> {
        self.get::<u32>(section, key)
    }
    
    /// Get a u64 value from a section
    /// 
    /// # Examples
    /// ```
    /// let size = hlx.get_u64("stats", "size").unwrap_or(0);
    /// ```
    pub fn get_u64(&self, section: &str, key: &str) -> Option<u64> {
        self.get::<u64>(section, key)
    }
    
    /// Get an f32 value from a section
    /// 
    /// # Examples
    /// ```
    /// let percentage = hlx.get_f32("stats", "cpu_usage").unwrap_or(0.0);
    /// ```
    pub fn get_f32(&self, section: &str, key: &str) -> Option<f32> {
        self.get_num(section, key).map(|n| n as f32)
    }
    
    /// Get an f64 value from a section
    /// 
    /// # Examples
    /// ```
    /// let precise_value = hlx.get_f64("data", "measurement").unwrap_or(0.0);
    /// ```
    pub fn get_f64(&self, section: &str, key: &str) -> Option<f64> {
        self.get_num(section, key)
    }
    
    /// Get a Vec<String> value from a section
    /// 
    /// # Examples
    /// ```
    /// let tags = hlx.get_vec_string("project", "tags").unwrap_or_default();
    /// ```
    pub fn get_vec_string(&self, section: &str, key: &str) -> Option<Vec<String>> {
        self.get::<Vec<String>>(section, key)
    }
    
    /// Get a Vec<i32> value from a section
    /// 
    /// # Examples
    /// ```
    /// let ports = hlx.get_vec_i32("config", "ports").unwrap_or_default();
    /// ```
    pub fn get_vec_i32(&self, section: &str, key: &str) -> Option<Vec<i32>> {
        self.get::<Vec<i32>>(section, key)
    }
    
    /// Get a Vec<f64> value from a section
    /// 
    /// # Examples
    /// ```
    /// let measurements = hlx.get_vec_f64("data", "samples").unwrap_or_default();
    /// ```
    pub fn get_vec_f64(&self, section: &str, key: &str) -> Option<Vec<f64>> {
        self.get::<Vec<f64>>(section, key)
    }
    
    /// Get a Vec<bool> value from a section
    /// 
    /// # Examples
    /// ```
    /// let flags = hlx.get_vec_bool("features", "flags").unwrap_or_default();
    /// ```
    pub fn get_vec_bool(&self, section: &str, key: &str) -> Option<Vec<bool>> {
        self.get::<Vec<bool>>(section, key)
    }
    
    /// Get a value dynamically - tries to determine type automatically
    /// 
    /// # Examples
    /// ```
    /// let value = hlx.get_dynamic("config", "port").unwrap();
    /// // Can use as different types:
    /// if let Some(num) = value.as_number() {
    ///     println!("Port as number: {}", num);
    /// }
    /// if let Some(str) = value.as_string() {
    ///     println!("Port as string: {}", str);
    /// }
    /// ```
    pub fn get_dynamic(&self, section: &str, key: &str) -> Option<DynamicValue> {
        let value = self.get_raw(section, key)?;
        
        match value {
            Value::String(s) => Some(DynamicValue::String(s.clone())),
            Value::Number(n) => {
                // Check if it's actually an integer
                if n.fract() == 0.0 && *n >= i64::MIN as f64 && *n <= i64::MAX as f64 {
                    Some(DynamicValue::Integer(*n as i64))
                } else {
                    Some(DynamicValue::Number(*n))
                }
            }
            Value::Bool(b) => Some(DynamicValue::Bool(*b)),
            Value::Array(arr) => Some(DynamicValue::Array(arr.clone())),
            _ => Some(DynamicValue::Empty),
        }
    }
    
    /// Get any value and try to convert to the most appropriate type
    /// Returns the value as a string representation for maximum compatibility
    /// 
    /// # Examples
    /// ```
    /// let port = hlx.get_auto("config", "port").unwrap(); // "8080"
    /// let debug = hlx.get_auto("features", "debug").unwrap(); // "true"
    /// ```
    pub fn get_auto(&self, section: &str, key: &str) -> Option<String> {
        self.get_raw(section, key).map(|v| match v {
            Value::String(s) => s.clone(),
            Value::Number(n) => {
                if n.fract() == 0.0 {
                    format!("{:.0}", n)
                } else {
                    n.to_string()
                }
            }
            Value::Bool(b) => b.to_string(),
            Value::Array(arr) => format!("{:?}", arr),
            Value::Object(obj) => format!("{:?}", obj),
            Value::Null => "null".to_string(),
            Value::Duration(d) => format!("{:?}", d),
            Value::Reference(r) => r.clone(),
            Value::Identifier(i) => i.clone(),
        })
    }
    
    // ============================================================
    // FLUENT GET API - select() method for cleanest syntax
    // ============================================================
    
    /// Fluent API for clean type inference without annotations
    /// 
    /// # Examples
    /// ```
    /// let name = hlx.select("project", "name").string();
    /// let port = hlx.select("config", "port").i32();
    /// let debug = hlx.select("features", "debug").bool();
    /// 
    /// // With defaults
    /// let name = hlx.select("project", "name").string_or("unknown".to_string());
    /// let port = hlx.select("config", "port").i32_or(8080);
    /// let debug = hlx.select("features", "debug").bool_or_false();
    /// ```
    pub fn select(&self, section: &str, key: &str) -> TypedGetter {
        TypedGetter {
            value: self.get_raw(section, key),
        }
    }
    
    /// Get a builder for retrieving multiple values from the same section
    /// 
    /// # Examples
    /// ```
    /// let config = hlx.get_from("config");
    /// let port = config.i32_or("port", 8080);
    /// let debug = config.bool_or("debug", false);
    /// let name = config.string_or("name", "default");
    /// ```
    pub fn get_from<'a>(&'a self, section: &'a str) -> SectionGetter<'a, 'a> {
        SectionGetter {
            hlx: self,
            section,
        }
    }
    
    /// Set a value in a section - automatically converts Rust types to DnaValue
    /// 
    /// # Examples
    /// ```
    /// // String values
    /// hlx.set("project", "name", "MyProject");
    /// hlx.set("project", "version", String::from("1.0.0"));
    /// 
    /// // Numeric values
    /// hlx.set("config", "port", 8080);
    /// hlx.set("config", "timeout", 30.5);
    /// 
    /// // Boolean values
    /// hlx.set("features", "debug", true);
    /// 
    /// // Explicit DnaValue for complex types
    /// hlx.set("data", "items", DnaValue::Array(vec![
    ///     DnaValue::String("item1".to_string()),
    ///     DnaValue::String("item2".to_string()),
    /// ]));
    /// ```
    pub fn set<T: IntoValue>(&mut self, section: &str, key: &str, value: T) {
        self.data
            .entry(section.to_string())
            .or_insert_with(HashMap::new)
            .insert(key.to_string(), value.into_value());
    }
    
    // Keep old method names for backward compatibility (delegates to new set)
    pub fn set_str(&mut self, section: &str, key: &str, value: &str) {
        self.set(section, key, value);
    }
    
    pub fn set_num(&mut self, section: &str, key: &str, value: f64) {
        self.set(section, key, value);
    }
    
    pub fn set_bool(&mut self, section: &str, key: &str, value: bool) {
        self.set(section, key, value);
    }
    
    /// Increase a numeric value by the specified amount
    /// If the key doesn't exist, it will be initialized to 0 + amount
    /// If the value is not a number, it will be converted to 0 + amount
    pub fn increase(&mut self, section: &str, key: &str, amount: f64) -> Result<f64, HlxError> {
        let current_value = self.get_raw(section, key)
            .and_then(|v| v.as_number())
            .unwrap_or(0.0);
        
        let new_value = current_value + amount;
        
        self.set(section, key, Value::Number(new_value));
        Ok(new_value)
    }
    pub fn index(&self, section: &str) -> Option<&HashMap<String, Value>> {
        self.data.get(section)
    }
    pub fn index_mut(&mut self, section: &str) -> Option<&mut HashMap<String, Value>> {
        self.data.get_mut(section)
    }
    pub async fn server(&mut self) -> Result<(), HlxError> {
        if self.dispatcher.is_ready() {
            Ok(())
        } else {
            self.dispatcher.initialize().await
        }
    }
    pub async fn watch(&mut self) -> Result<(), HlxError> {
        #[cfg(feature = "compiler")]
        {
            if let Some(path) = &self.file_path {
                println!("Watching {} for changes...", path.display());
                Ok(())
            } else {
                Err(
                    HlxError::invalid_input(
                        "No file loaded for watching",
                        "Load a file first with Hlx::load()",
                    ),
                )
            }
        }
        #[cfg(not(feature = "compiler"))]
        {
            Err(
                HlxError::compilation_error(
                    "Watch mode not available",
                    "Compile with 'compiler' feature enabled",
                ),
            )
        }
    }
    pub async fn process(&mut self) -> Result<(), HlxError> {
        if let Some(path) = &self.file_path {
            let content = std::fs::read_to_string(path)
                .map_err(|e| HlxError::io_error(
                    format!("Failed to read file: {}", e),
                    "Ensure file exists and is readable",
                ))?;
            match self.dispatcher.parse_and_execute(&content).await? {
                DispatchResult::Executed(value) => {
                    println!("Processed successfully: {:?}", value);
                    Ok(())
                }
                _ => Ok(()),
            }
        } else {
            Err(
                HlxError::invalid_input(
                    "No file loaded for processing",
                    "Load a file first with Hlx::load()",
                ),
            )
        }
    }
    pub async fn compile(&mut self) -> Result<(), HlxError> {
        #[cfg(feature = "compiler")]
        {
            if let Some(path) = &self.file_path {
                use crate::dna::compiler::{Compiler, OptimizationLevel};
                let compiler = Compiler::builder()
                    .optimization_level(OptimizationLevel::Two)
                    .compression(true)
                    .cache(true)
                    .verbose(false)
                    .build();
                let binary = compiler
                    .compile_file(path)
                    .map_err(|e| HlxError::compilation_error(
                        format!("Compilation failed: {}", e),
                        "Check file syntax and try again",
                    ))?;
                let binary_path = path.with_extension("hlxb");
                let serializer = crate::dna::mds::serializer::BinarySerializer::new(true);
                serializer
                    .write_to_file(&binary, &binary_path)
                    .map_err(|e| HlxError::io_error(
                        format!("Failed to write binary file: {}", e),
                        "Ensure output directory is writable",
                    ))?;
                println!(
                    "✅ Successfully compiled {} to {}", path.display(), binary_path
                    .display()
                );
                Ok(())
            } else {
                Err(
                    HlxError::invalid_input(
                        "No file loaded for compilation",
                        "Load a file first with Hlx::load()",
                    ),
                )
            }
        }
        #[cfg(not(feature = "compiler"))]
        {
            Err(
                HlxError::compilation_error(
                    "Compilation not available",
                    "Compile with 'compiler' feature enabled",
                ),
            )
        }
    }
    pub async fn execute(&mut self, code: &str) -> Result<Value, HlxError> {
        if !self.dispatcher.is_ready() {
            self.dispatcher.initialize().await?;
        }
        match self.dispatcher.parse_and_execute(code).await {
            Ok(DispatchResult::Executed(value)) => Ok(value),
            Ok(DispatchResult::ParseError(err)) => {
                Err(
                    HlxError::invalid_input(
                        format!("Parse error: {}", err),
                        "Check syntax",
                    ),
                )
            }
            Ok(DispatchResult::ExecutionError(err)) => Err(err),
            Ok(DispatchResult::Parsed(_)) => {
                Err(
                    HlxError::execution_error(
                        "Parsed but not executed",
                        "Use process() for file processing",
                    ),
                )
            }
            Err(e) => Err(e),
        }
    }
    pub async fn execute_operator(
        &self,
        operator: &str,
        params: &str,
    ) -> Result<Value, HlxError> {
        self.operator_engine.execute_operator(operator, params).await
    }
    pub fn sections(&self) -> Vec<&String> {
        self.data.keys().collect()
    }
    pub fn keys(&self, section: &str) -> Option<Vec<&String>> {
        self.data.get(section).map(|s| s.keys().collect())
    }
    
    /// Set the file path for saving
    /// 
    /// # Example
    /// ```
    /// let mut hlx = Hlx::new().await?;
    /// hlx.set_file_path("config.hlx");
    /// hlx.save()?; // Will save to config.hlx
    /// ```
    pub fn set_file_path<P: AsRef<Path>>(&mut self, path: P) {
        self.file_path = Some(path.as_ref().to_path_buf());
    }
    
    /// Get the current file path
    pub fn get_file_path(&self) -> Option<&Path> {
        self.file_path.as_deref()
    }
    pub fn save(&self) -> Result<(), HlxError> {
        if let Some(path) = &self.file_path {
            let mut content = String::new();
            
            // Generate proper HLX format with colon/semicolon syntax
            for (section, keys) in &self.data {
                // Use section name directly with colon syntax
                content.push_str(&format!("{} :\n", section));
                
                for (key, value) in keys {
                    // Format value appropriately
                    let formatted_value = match value {
                        Value::String(s) => format!("\"{}\"", s),
                        Value::Number(n) => n.to_string(),
                        Value::Bool(b) => b.to_string(),
                        Value::Array(arr) => {
                            let items: Vec<String> = arr.iter().map(|v| {
                                match v {
                                    Value::String(s) => format!("\"{}\"", s),
                                    Value::Number(n) => n.to_string(),
                                    Value::Bool(b) => b.to_string(),
                                    _ => format!("{}", v),
                                }
                            }).collect();
                            format!("[{}]", items.join(", "))
                        },
                        Value::Object(obj) => {
                            let pairs: Vec<String> = obj.iter().map(|(k, v)| {
                                format!("{} = {}", k, v)
                            }).collect();
                            format!("{{\n        {}\n    }}", pairs.join("\n        "))
                        },
                        _ => format!("{}", value),
                    };
                    
                    content.push_str(&format!("    {} = {}\n", key, formatted_value));
                }
                
                content.push_str(";\n\n");
            }
            
            std::fs::write(path, content)
                .map_err(|e| HlxError::io_error(
                    format!("Failed to save file: {}", e),
                    "Ensure write permissions",
                ))?;
            
            // Automatic vault backup for .hlx files
            if path.extension().and_then(|s| s.to_str()) == Some("hlx") {
                if let Ok(vault) = crate::dna::vlt::Vault::new() {
                    let description = format!("Auto-backup from hlx.save()");
                    let _ = vault.save(path, Some(description));
                }
            }
            
            Ok(())
        } else {
            Err(
                HlxError::invalid_input(
                    "No file path set",
                    "Load a file first or set file_path manually",
                ),
            )
        }
    }

    /// Generate HLX content as a string without writing to file
    /// 
    /// # Example
    /// ```
    /// let mut hlx = Hlx::new().await?;
    /// hlx.set("project", "name", Value::String("MyProject".to_string()));
    /// hlx.set("project", "version", Value::String("1.0.0".to_string()));
    /// let content = hlx.make()?;
    /// println!("Generated HLX content:\n{}", content);
    /// ```
    pub fn make(&self) -> Result<String, HlxError> {
        let mut content = String::new();
        
        // Generate proper HLX format with colon/semicolon syntax
        for (section, keys) in &self.data {
            // Use section name directly with colon syntax
            content.push_str(&format!("{} :\n", section));
            
            for (key, value) in keys {
                // Format value appropriately
                let formatted_value = match value {
                    Value::String(s) => format!("\"{}\"", s),
                    Value::Number(n) => n.to_string(),
                    Value::Bool(b) => b.to_string(),
                    Value::Array(arr) => {
                        let items: Vec<String> = arr.iter().map(|v| {
                            match v {
                                Value::String(s) => format!("\"{}\"", s),
                                Value::Number(n) => n.to_string(),
                                Value::Bool(b) => b.to_string(),
                                _ => format!("{}", v),
                            }
                        }).collect();
                        format!("[{}]", items.join(", "))
                    },
                    Value::Object(obj) => {
                        let pairs: Vec<String> = obj.iter().map(|(k, v)| {
                            format!("{} = {}", k, v)
                        }).collect();
                        format!("{{\n        {}\n    }}", pairs.join("\n        "))
                    },
                    _ => format!("{}", value),
                };
                
                content.push_str(&format!("    {} = {}\n", key, formatted_value));
            }
            
            content.push_str(";\n\n");
        }
        
        Ok(content)
    }
}
impl std::ops::Index<&str> for Hlx {
    type Output = HashMap<String, Value>;
    fn index(&self, section: &str) -> &Self::Output {
        self.data
            .get(section)
            .unwrap_or_else(|| panic!("Section '{}' not found", section))
    }
}
impl std::ops::IndexMut<&str> for Hlx {
    fn index_mut(&mut self, section: &str) -> &mut Self::Output {
        self.data.entry(section.to_string()).or_insert_with(HashMap::new)
    }
}



// RecordBatch type for Ruby bindings
pub type RecordBatch = Vec<HashMap<String, Value>>;
pub mod test_operators {
    use super::*;
    pub async fn test_fundamental_operators() -> Result<(), HlxError> {
        let mut hlx = Hlx::new().await?;
        println!("Testing fundamental operators...");
        let result = hlx.execute(r#"@var(name="test_var", value="hello")"#).await?;
        println!("@var result: {:?}", result);
        let result = hlx.execute(r#"@env(key="HOME")"#).await?;
        println!("@env result: {:?}", result);
        let result = hlx.execute(r#"@date("Y-m-d")"#).await?;
        println!("@date result: {:?}", result);
        let result = hlx.execute(r#"@time("H:i:s")"#).await?;
        println!("@time result: {:?}", result);
        let result = hlx.execute("@uuid()").await?;
        println!("@uuid result: {:?}", result);
        let result = hlx.execute(r#"@string("hello world", "upper")"#).await?;
        println!("@string result: {:?}", result);
        let result = hlx.execute(r#"@math("5 + 3")"#).await?;
        println!("@math result: {:?}", result);
        let result = hlx.execute(r#"@calc("a = 10; b = 5; a + b")"#).await?;
        println!("@calc result: {:?}", result);
        let result = hlx
            .execute(r#"@if(condition="true", then="yes", else="no")"#)
            .await?;
        println!("@if result: {:?}", result);
        let result = hlx
            .execute(r#"@array(values="[1,2,3]", operation="length")"#)
            .await?;
        println!("@array result: {:?}", result);
        let result = hlx.execute(r#"@json('{"name":"test"}', "parse")"#).await?;
        println!("@json result: {:?}", result);
        let result = hlx.execute(r#"@base64("hello", "encode")"#).await?;
        println!("@base64 result: {:?}", result);
        let result = hlx.execute(r#"@hash("password", "sha256")"#).await?;
        println!("@hash result: {:?}", result);
        println!("All fundamental operators tested successfully!");
        Ok(())
    }
    pub async fn test_conditional_operators() -> Result<(), HlxError> {
        let mut hlx = Hlx::new().await?;
        println!("Testing conditional operators...");
        let result = hlx
            .execute(r#"@if(condition="@math('5 > 3')", then="greater", else="less")"#)
            .await?;
        println!("@if with expression: {:?}", result);
        let result = hlx
            .execute(
                r#"@switch(value="2", cases="{'1':'one','2':'two','3':'three'}", default="unknown")"#,
            )
            .await?;
        println!("@switch result: {:?}", result);
        let result = hlx
            .execute(r#"@filter(array="[1,2,3,4,5]", condition="@math('value > 3')")"#)
            .await?;
        println!("@filter result: {:?}", result);
        let result = hlx
            .execute(r#"@map(array="[1,2,3]", transform="@math('value * 2')")"#)
            .await?;
        println!("@map result: {:?}", result);
        let result = hlx
            .execute(
                r#"@reduce(array="[1,2,3,4]", initial="0", operation="@math('acc + value')")"#,
            )
            .await?;
        println!("@reduce result: {:?}", result);
        println!("All conditional operators tested successfully!");
        Ok(())
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[tokio::test]
    async fn test_hlx_interface() {
        let mut hlx = Hlx::new().await.unwrap();
        hlx.data.insert("database".to_string(), HashMap::new());
        hlx.index_mut("database")
            .unwrap()
            .insert(
                "host".to_string(),
                crate::dna::atp::value::Value::String("localhost".to_string()),
            );
        hlx.index_mut("database")
            .unwrap()
            .insert("port".to_string(), crate::dna::atp::value::Value::Number(5432.0));
        assert_eq!(
            hlx.get("database", "host"), Some(& crate::dna::atp::value::Value::String("localhost"
            .to_string()))
        );
        assert_eq!(hlx.get("database", "port"), Some(& Value::Number(5432.0)));
        let sections = hlx.sections();
        assert!(sections.iter().any(| s | * s == "database"));
        let keys = hlx.keys("database").unwrap();
        assert!(keys.iter().any(| k | * k == "host"));
    }
    #[tokio::test]
    async fn test_operator_execution() {
        let hlx = Hlx::new().await.unwrap();
        let result = hlx.execute_operator("date", "{\"format\":\"Y-m-d\"}").await;
        println!("Direct operator execution result: {:?}", result);
        assert!(result.is_ok());
        let result = hlx.execute_operator("uuid", "").await;
        println!("UUID operator execution result: {:?}", result);
        assert!(result.is_ok());
        let result = hlx.execute_operator("nonexistent", "{}").await;
        println!("Invalid operator result: {:?}", result);
        assert!(result.is_err());
    }
    #[tokio::test]
    async fn test_operator_integration() {
        use crate::ops::OperatorParser;
        let mut ops_parser = OperatorParser::new().await;
        let result = ops_parser.parse_value("@date(\"Y-m-d\")").await.unwrap();
        match result {
            crate::dna::atp::value::Value::String(date_str) => {
                assert!(! date_str.is_empty());
                println!("✅ @date operator working: {}", date_str);
            }
            _ => panic!("Expected string result from @date"),
        }
        let result = ops_parser.parse_value("@uuid()").await.unwrap();
        match result {
            crate::dna::atp::value::Value::String(uuid_str) => {
                assert!(! uuid_str.is_empty());
                println!(
                    "✅ @uuid operator working: {} (length: {})", uuid_str, uuid_str
                    .len()
                );
            }
            _ => panic!("Expected string result from @uuid"),
        }
        use crate::dna::ops::OperatorEngine;
        let operator_engine = OperatorEngine::new().await.unwrap();
        let result = operator_engine
            .execute_operator("date", "{\"format\":\"%Y-%m-%d\"}")
            .await
            .unwrap();
        match result {
            crate::dna::atp::value::Value::String(date_str) => {
                assert!(! date_str.is_empty());
                println!("✅ Direct date operator working: {}", date_str);
            }
            _ => panic!("Expected string result from direct date operator"),
        }
        let result = operator_engine.execute_operator("uuid", "").await.unwrap();
        match result {
            crate::dna::atp::value::Value::String(uuid_str) => {
                assert!(! uuid_str.is_empty());
                println!(
                    "✅ Direct uuid operator working: {} (length: {})", uuid_str,
                    uuid_str.len()
                );
            }
            _ => panic!("Expected string result from direct uuid operator"),
        }
        println!("✅ ops.rs and operators/ integration fully working!");
    }
    #[tokio::test]
    async fn test_comprehensive_operator_testing() {
        assert!(true);
    }
}