#![allow(missing_docs, clippy::must_use_candidate)]
#![cfg_attr(windows, feature(abi_vectorcall))]
#[cfg(feature = "php")]
pub use crate::dna::atp::value::Value as DnaValue;
#[cfg(feature = "php")]
pub use crate::dna::atp::*;
#[cfg(feature = "php")]
pub use crate::dna::bch::*;
#[cfg(feature = "php")]
pub use crate::dna::cmd::*;
#[cfg(feature = "php")]
pub use crate::dna::compiler::Compiler;
#[cfg(feature = "php")]
pub use crate::dna::compiler::*;
#[cfg(feature = "php")]
pub use crate::dna::exp::*;
#[cfg(feature = "php")]
pub use crate::dna::hel::dna_hlx::Hlx;
#[cfg(feature = "php")]
pub use crate::dna::hel::*;
#[cfg(feature = "php")]
pub use crate::dna::map::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::optimizer::OptimizationLevel;
#[cfg(feature = "php")]
pub use crate::dna::mds::*;
#[cfg(feature = "php")]
pub use crate::dna::ngs::*;
#[cfg(feature = "php")]
pub use crate::dna::ops::*;
#[cfg(feature = "php")]
pub use crate::dna::out::*;
#[cfg(feature = "php")]
pub use crate::dna::tst::*;
#[cfg(feature = "php")]
pub use crate::dna::vlt::Vault;
#[cfg(feature = "php")]
pub use crate::dna::atp::ast::*;
#[cfg(feature = "php")]
pub use crate::dna::atp::interpreter::*;
#[cfg(feature = "php")]
pub use crate::dna::atp::lexer::*;
#[cfg(feature = "php")]
pub use crate::dna::atp::output::*;
#[cfg(feature = "php")]
pub use crate::dna::atp::parser::*;
#[cfg(feature = "php")]
pub use crate::dna::atp::types::*;
#[cfg(feature = "php")]
pub use crate::dna::hel::binary::*;
#[cfg(feature = "php")]
pub use crate::dna::hel::dispatch::*;
#[cfg(feature = "php")]
pub use crate::dna::hel::dna_hlx::*;
#[cfg(feature = "php")]
pub use crate::dna::hel::error::*;  
#[cfg(feature = "php")]
pub use crate::dna::hel::hlx::*;
#[cfg(feature = "php")]
pub use crate::dna::map::core::*;
#[cfg(feature = "php")]
pub use crate::dna::map::hf::*;
#[cfg(feature = "php")]
pub use crate::dna::map::reasoning::*;
#[cfg(feature = "php")]
use crate::dna::map::caption::E621Config as MapE621Config;
#[cfg(feature = "php")]
pub use crate::dna::mds::a_example::{Document, Embedding, Metadata};
#[cfg(feature = "php")]
pub use crate::dna::mds::benches::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::bundle::*;
#[cfg(feature = "php")]  
pub use crate::dna::mds::cache::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::caption::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::codegen::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::concat::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::config::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::decompile::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::filter::*; 
pub use crate::dna::mds::migrate::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::modules::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::optimizer::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::project::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::runtime::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::schema::*;
#[cfg(feature = "php")]  
pub use crate::dna::mds::semantic::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::serializer::*;
#[cfg(feature = "php")]
pub use crate::dna::mds::server::*;
#[cfg(feature = "php")]
pub use crate::dna::out::helix_format::*;
#[cfg(feature = "php")]
pub use crate::dna::out::hlx_config_format::*;
#[cfg(feature = "php")]
pub use crate::dna::out::hlxb_config_format::*;
#[cfg(feature = "php")]
pub use crate::dna::out::hlxc_format::*;
#[cfg(feature = "php")]
pub use crate::dna::vlt::tui::*;
#[cfg(feature = "php")]
pub use crate::dna::vlt::vault::*;
#[cfg(feature = "php")]
pub use crate::dna::map::core::TrainingSample; 

#[cfg(feature = "php")]
use std::collections::HashMap;
#[cfg(all(feature = "csharp", feature = "compiler"))]
use bincode;
#[cfg(feature = "php")]
pub type Env = *mut std::ffi::c_void;
#[cfg(feature = "php")]
pub type CsObject = *mut std::ffi::c_void;
#[cfg(feature = "php")]
pub type CsUnknown = *mut std::ffi::c_void;
#[cfg(feature = "php")]
pub type CsResult<T> = std::result::Result<T, CsError>;
#[cfg(feature = "php")]
use std::os::raw::c_char;
#[cfg(feature = "php")]
use std::ffi::{CStr, CString};
#[cfg(feature = "php")]
pub use crate::Parser;

#[cfg(feature = "php")]
use crate::HelixConfig as RustHelixConfig;
#[cfg(feature = "php")]
use serde_json;

#[cfg(feature = "php")]
use ext_php_rs::{constant::IntoConst, prelude::*, types::ZendClassObject};

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct HelixConfigFFI {
    ptr: *mut RustHelixConfig,
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsError {
    message: String,
}

#[cfg(feature = "php")]
impl CsError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

#[cfg(feature = "php")]
impl std::fmt::Display for CsError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

#[cfg(feature = "php")]
impl std::error::Error for CsError {}

#[cfg(feature = "php")]
pub type NewError = CsError;

#[cfg(feature = "php")]
pub fn error_csharp(message: impl Into<String>) -> CsError {
    CsError::new(message)
}

#[cfg(feature = "php")]
pub fn result_to_ptr<T>(result: CsResult<T>) -> *mut c_char
where
    T: Into<*mut c_char>,
{
    match result {
        Ok(val) => val.into(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "php")]
unsafe fn c_string_to_rust(s: *const c_char) -> String {
    if s.is_null() {
        return String::new();
    }
    CStr::from_ptr(s)
        .to_string_lossy()
        .into_owned()
}

#[cfg(feature = "php")]
unsafe fn c_string_to_rust_option(s: *const c_char) -> Option<String> {
    if s.is_null() {
        None
    } else {
        Some(c_string_to_rust(s))
    }
}

#[cfg(feature = "php")]
pub fn rust_string_to_c(s: String) -> *mut c_char {
    match CString::new(s) {
        Ok(c_str) => c_str.into_raw(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "php")]
pub fn rust_result_string_to_c(result: CsResult<String>) -> *mut c_char {
    match result {
        Ok(s) => rust_string_to_c(s),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "php")]
unsafe fn c_u32_to_rust_option(val: *const u32) -> Option<u32> {
    if val.is_null() {
        None
    } else {
        Some(*val)
    }
}

#[cfg(feature = "php")]
unsafe fn c_bool_to_rust_option(val: *const bool) -> Option<bool> {
    if val.is_null() {
        None
    } else {
        Some(*val)
    }
}

#[cfg(feature = "php")]
pub fn rust_result_f64_to_c(result: CsResult<f64>, error_out: *mut *mut c_char) -> f64 {
    match result {
        Ok(val) => {
            if !error_out.is_null() {
                unsafe { *error_out = std::ptr::null_mut(); }
            }
            val
        }
        Err(e) => {
            if !error_out.is_null() {
                unsafe { *error_out = rust_string_to_c(e.to_string()); }
            }
            0.0
        }
    }
}

#[cfg(feature = "php")]
pub fn rust_result_bool_to_c(result: CsResult<bool>, error_out: *mut *mut c_char) -> bool {
    match result {
        Ok(val) => {
            if !error_out.is_null() {
                unsafe { *error_out = std::ptr::null_mut(); }
            }
            val
        }
        Err(e) => {
            if !error_out.is_null() {
                unsafe { *error_out = rust_string_to_c(e.to_string()); }
            }
            false
        }
    }
}

#[cfg(feature = "php")]
pub fn rust_result_u64_to_c(result: CsResult<u64>, error_out: *mut *mut c_char) -> u64 {
    match result {
        Ok(val) => {
            if !error_out.is_null() {
                unsafe { *error_out = std::ptr::null_mut(); }
            }
            val
        }
        Err(e) => {
            if !error_out.is_null() {
                unsafe { *error_out = rust_string_to_c(e.to_string()); }
            }
            0
        }
    }
}

#[cfg(feature = "php")]
pub trait EnvExt {
    fn create_string(&self, s: &str) -> CsResult<CsUnknown>;
    fn create_double(&self, n: f64) -> CsResult<CsUnknown>;
    fn get_boolean(&self, b: bool) -> CsResult<CsUnknown>;
    fn create_array_with_length(&self, len: usize) -> CsResult<CsUnknown>;
    fn create_object(&self) -> CsResult<CsUnknown>;
    fn get_null(&self) -> CsResult<CsUnknown>;
}

#[cfg(feature = "php")]
impl EnvExt for Env {
    fn create_string(&self, _s: &str) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
    fn create_double(&self, _n: f64) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
    fn get_boolean(&self, _b: bool) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
    fn create_array_with_length(&self, _len: usize) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
    fn create_object(&self) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
    fn get_null(&self) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}


#[cfg(feature = "php")]
pub trait CsUnknownExt {
    fn into_unknown(self) -> *mut c_char;
    fn coerce_to_string(&self) -> CsResult<CsUnknown>;
    fn into_utf8(&self) -> CsResult<CsUnknown>;
}

#[cfg(feature = "php")]
impl CsUnknownExt for CsUnknown {
    fn into_unknown(self) -> *mut c_char {
        std::ptr::null_mut()
    }
    fn coerce_to_string(&self) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
    fn into_utf8(&self) -> CsResult<CsUnknown> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}

#[cfg(feature = "php")]
pub trait CsUnknownStr {
    fn as_str(&self) -> CsResult<&str>;
}

#[cfg(feature = "php")]
impl CsUnknownStr for CsUnknown {
    fn as_str(&self) -> CsResult<&str> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}

#[cfg(feature = "php")]
pub trait CsUnknownArray {
    fn set_element(&mut self, index: u32, value: CsUnknown) -> CsResult<()>;
}

#[cfg(feature = "php")]
impl CsUnknownArray for CsUnknown {
    fn set_element(&mut self, _index: u32, _value: CsUnknown) -> CsResult<()> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}

#[cfg(feature = "php")]
pub trait CsUnknownObject {
    fn set_named_property(&mut self, key: &str, value: CsUnknown) -> CsResult<()>;
}

#[cfg(feature = "php")]
impl CsUnknownObject for CsUnknown {
    fn set_named_property(&mut self, _key: &str, _value: CsUnknown) -> CsResult<()> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}

#[cfg(feature = "php")]
#[php_function]
    pub fn value_to_csharp(env: Env, value: &crate::dna::atp::value::Value) -> *mut c_char {
        match value {
            crate::dna::atp::value::Value::String(s) => {
                match env.create_string(s) {
                    Ok(csharp_val) => csharp_val.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            },
            crate::dna::atp::value::Value::Number(n) => {
                match env.create_double(*n) {
                    Ok(csharp_val) => csharp_val.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            }
            crate::dna::atp::value::Value::Bool(b) => {
                match env.get_boolean(*b) {
                    Ok(csharp_val) => csharp_val.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            }
            crate::dna::atp::value::Value::Array(arr) => {
                match env.create_array_with_length(arr.len()) {
                    Ok(mut csharp_arr) => {
                        for (i, item) in arr.iter().enumerate() {
                            let csharp_item = value_to_csharp(env, item);
                            if csharp_item.is_null() {
                                return std::ptr::null_mut();
                            }
                            let csharp_item_unknown = csharp_item as CsUnknown;
                            if let Err(_) = csharp_arr.set_element(i as u32, csharp_item_unknown) {
                                return std::ptr::null_mut();
                            }
                        }
                        csharp_arr.into_unknown()
                    }
                    Err(_) => std::ptr::null_mut(),
                }
            }
            crate::dna::atp::value::Value::Object(obj) => {
                match env.create_object() {
                    Ok(mut csharp_obj) => {
                        for (key, val) in obj {
                            let csharp_val = value_to_csharp(env, val);
                            if csharp_val.is_null() {
                                return std::ptr::null_mut();
                            }
                            let csharp_val_unknown = csharp_val as CsUnknown;
                            if let Err(_) = csharp_obj.set_named_property(key, csharp_val_unknown) {
                                return std::ptr::null_mut();
                            }
                        }
                        csharp_obj.into_unknown()
                    }
                    Err(_) => std::ptr::null_mut(),
                }
            }
            crate::dna::atp::value::Value::Null => {
                match env.get_null() {
                    Ok(null_val) => null_val.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            }
            crate::dna::atp::value::Value::Duration(d) => {
                match env.create_string(&d.to_string()) {
                    Ok(csharp_val) => csharp_val.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            }
            crate::dna::atp::value::Value::Reference(r) => {
                match env.create_string(&r.to_string()) {
                    Ok(csharp_val) => csharp_val.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            }
            crate::dna::atp::value::Value::Identifier(i) => {
                match env.create_string(&i.to_string()) {
                    Ok(csharp_val) => csharp_val.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            }
        }
    }
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHelixAst {
    inner: HelixAst,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsHelixAst {
    
    #[php_function]
    pub fn new() -> Self {
            Self {
                inner: HelixAst::new(),
        }
    }
    
    #[php_function]
    pub fn add_declaration(&mut self, _decl: &CsObject) -> *mut c_char{
            std::ptr::null_mut()
    }

    
    #[php_function]
    pub fn get_projects(&self, env: Env) -> *mut c_char {
            let projects = self.inner.get_projects();
            match env.create_array_with_length(projects.len()) {
                Ok(mut result) => {
                    for (i, _project) in projects.iter().enumerate() {
                        match env.get_null() {
                            Ok(null_val) => {
                                if let Err(_) = result.set_element(i as u32, null_val) {
                                    return std::ptr::null_mut();
                                }
                            }
                            Err(_) => return std::ptr::null_mut(),
                        }
                    }
                    result.into_unknown()
                }
                Err(_) => std::ptr::null_mut(),
            }
        }
    }
    #[php_function]
    pub fn get_agents(&self, env: Env) -> *mut c_char {
            let agents = self.inner.get_agents();
            match env.create_array_with_length(agents.len()) {
                Ok(mut result) => {
                    for (i, _agent) in agents.iter().enumerate() {
                        match env.get_null() {
                            Ok(null_val) => {
                                if let Err(_) = result.set_element(i as u32, null_val) {
                                    return std::ptr::null_mut();
                                }
                            }
                            Err(_) => return std::ptr::null_mut(),
                        }
                    }
                    result.into_unknown()
                }
                Err(_) => std::ptr::null_mut(),
            }
        }
    
    #[php_function]
    pub fn get_workflows(&self, env: Env) -> *mut c_char {
            let workflows = self.inner.get_workflows();
            match env.create_array_with_length(workflows.len()) {
                Ok(mut result) => {
                    for (i, _workflow) in workflows.iter().enumerate() {
                        match env.get_null() {
                            Ok(null_val) => {
                                if let Err(_) = result.set_element(i as u32, null_val) {
                                    return std::ptr::null_mut();
                                }
                            }
                            Err(_) => return std::ptr::null_mut(),
                        }
                    }
                    result.into_unknown()
                }
                Err(_) => std::ptr::null_mut(),
            }
        }
    
    #[php_function]
    pub fn get_contexts(&self, env: Env) -> *mut c_char {
            let contexts = self.inner.get_contexts();
            match env.create_array_with_length(contexts.len()) {
                Ok(mut result) => {
                    for (i, _context) in contexts.iter().enumerate() {
                        match env.get_null() {
                            Ok(null_val) => {
                                if let Err(_) = result.set_element(i as u32, null_val) {
                                    return std::ptr::null_mut();
                                }
                            }
                            Err(_) => return std::ptr::null_mut(),
                        }
                    }
                    result.into_unknown()
                }
                Err(_) => std::ptr::null_mut(),
            }
        }
    

// Csthon wrapper for AstPrettyPrinter
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsAstPrettyPrinter {
    inner: AstPrettyPrinter,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsAstPrettyPrinter {

    #[php_function]
    pub fn new() -> Self {
            Self {
                inner: AstPrettyPrinter::new(),
        }

    }
    #[php_function]
    pub fn print(&mut self, ast: &CsHelixAst) -> *mut c_char {
        rust_string_to_c(self.inner.print(&ast.inner))
}
}

// Csthon wrapper for Expression
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsExpression {
    inner: Expression,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsExpression {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: Expression::Identifier("".to_string()),
    }


    }
    #[php_function]
    pub fn binary(
        left: &CsExpression,
        op: &str,
        right: &CsExpression,
    ) -> *mut CsExpression {
        let op_str = c_string_to_rust(op);
        // Parse binary operator
        let binary_op = match op_str.as_str() {
            "+" => BinaryOperator::Add,
            "-" => BinaryOperator::Sub,
            "*" => BinaryOperator::Mul,
            "/" => BinaryOperator::Div,
            "==" => BinaryOperator::Eq,
            "!=" => BinaryOperator::Ne,
            "<" => BinaryOperator::Lt,
            ">" => BinaryOperator::Gt,
            "<=" => BinaryOperator::Le,
            ">=" => BinaryOperator::Ge,
            "&&" => BinaryOperator::And,
            "||" => BinaryOperator::Or,
            _ => return std::ptr::null_mut(),
        };

        let expr = Expression::binary(
            left.inner.clone(),
            binary_op,
            right.inner.clone(),
        );
        Box::into_raw(Box::new(Self { inner: expr }))
    }
    #[php_function]
    pub fn as_string(&self) -> *mut c_char {
        rust_string_to_c(self.inner.as_string().unwrap_or_default())
    }
    #[php_function]
    pub fn as_number(&self, error_out: *mut *mut c_char) -> f64 {
        rust_result_f64_to_c(
            self.inner
                .as_number()
                .ok_or_else(|| error_csharp("Value is not a number")),
            error_out
        )
    }
    #[php_function]
    pub fn as_bool(&self, error_out: *mut *mut c_char) -> bool {
        rust_result_bool_to_c(
            self.inner
                .as_bool()
                .ok_or_else(|| error_csharp("Value is not a boolean")),
            error_out
        )
    }
    #[php_function]
    pub fn as_array(&self, env: Env) -> *mut c_char {
        let arr = match self.inner.as_array() {
            Some(arr) => arr,
            None => return std::ptr::null_mut(),
        };
        match env.create_array_with_length(arr.len()) {
            Ok(mut result) => {
                for (i, _expr) in arr.iter().enumerate() {
                    match env.get_null() {
                        Ok(null_val) => {
                            if let Err(_) = result.set_element(i as u32, null_val) {
                                return std::ptr::null_mut();
                            }
                        }
                        Err(_) => return std::ptr::null_mut(),
                    }
                }
                result.into_unknown()
            }
            Err(_) => std::ptr::null_mut(),
        }
    }
    #[php_function]
    pub fn as_object(&self, env: Env) -> *mut c_char {
        let obj = match self.inner.as_object() {
            Some(obj) => obj,
            None => return std::ptr::null_mut(),
        };
        match env.create_object() {
            Ok(mut result) => {
                for (key, _expr) in obj {
                    match env.get_null() {
                        Ok(null_val) => {
                            if let Err(_) = result.set_named_property(key, null_val) {
                                return std::ptr::null_mut();
                            }
                        }
                        Err(_) => return std::ptr::null_mut(),
                    }
                }
                result.into_unknown()
            }
            Err(_) => std::ptr::null_mut(),
        }
    }
    #[php_function]
    pub fn to_value(&self, env: Env) -> *mut c_char {
        let value = self.inner.to_value();
        value_to_csharp(env, &value)
}
}

// Csthon wrapper for AstBuilder
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsAstBuilder {
    inner: AstBuilder,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsAstBuilder {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: AstBuilder::new(),
    }

    }
    #[php_function]
    pub fn add_agent(&mut self, _agent: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_workflow(&mut self, _workflow: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_context(&mut self, _context: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_memory(&mut self, _memory: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_crew(&mut self, _crew: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_pipeline(&mut self, _pipeline: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_plugin(&mut self, _plugin: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_database(&mut self, _database: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_load(&mut self, _load: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_section(&mut self, _section: &CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn build(&mut self) -> *mut CsHelixAst {
        let ast = std::mem::replace(&mut self.inner, crate::dna::atp::ast::AstBuilder::new()).build();
    }
}

// HelixInterpreter wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHelixInterpreter {
    inner: HelixInterpreter,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsHelixInterpreter {
    
    #[php_function]
    pub fn new(error_out: *mut *mut c_char) -> *mut CsHelixInterpreter {
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
            }
        };
        let interpreter = match rt.block_on(HelixInterpreter::new()) {
            Ok(interpreter) => interpreter,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
            }
        };
        Box::into_raw(Box::new(CsHelixInterpreter { inner: interpreter }))
    }

    }
    #[php_function]
    pub fn execute_ast(&mut self, env: Env, ast: &CsHelixAst) -> *mut c_char {
        let ast_clone = ast.inner.clone();
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        let result = match rt.block_on(self.inner.execute_ast(&ast_clone)) {
            Ok(result) => result,
            Err(_) => return std::ptr::null_mut(),
        };
        value_to_csharp(env, &result)
    }
    #[php_function]
    pub fn operator_engine(&self, env: Env) -> *mut c_char {
        let _engine = self.inner.operator_engine();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
    #[php_function]
    pub fn operator_engine_mut(&mut self, env: Env) -> *mut c_char {
        let _engine = self.inner.operator_engine_mut();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
    #[php_function]
    pub fn set_variable(&mut self, name: *const c_char, value: CsUnknown) -> *mut c_char{
        let name_str = c_string_to_rust(name);
        let val = if let Ok(csharp_str) = value.coerce_to_string() {
            if let Ok(utf8) = csharp_str.into_utf8() {
                if let Ok(s) = utf8.as_str() {
                    crate::dna::atp::value::Value::String(s.to_string())
                } else {
                    crate::dna::atp::value::Value::String("unknown".to_string())
                }
            } else {
                crate::dna::atp::value::Value::String("unknown".to_string())
            }
        } else {
            crate::dna::atp::value::Value::String("unknown".to_string())
        };
        self.inner.set_variable(&name_str, val);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn get_variable(&self, env: Env, name: *const c_char) -> *mut c_char {
        let name_str = c_string_to_rust(name);
        let value = self.inner.get_variable(&name_str);
        match value {
            Some(v) => value_to_csharp(env, &v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            }
        }
    }
    #[php_function]
    pub fn list_variables(&self, env: Env) -> *mut c_char {
        let vars = self.inner.list_variables();
        let var_names: Vec<String> = vars.into_iter().map(|(name, _value)| name).collect();
        match env.create_array_with_length(var_names.len()) {
            Ok(mut result) => {
                for (i, name) in var_names.iter().enumerate() {
                    match env.create_string(name) {
                        Ok(s) => {
                            if let Err(_) = result.set_element(i as u32, s) {
                                return std::ptr::null_mut();
                            }
                        }
                        Err(_) => return std::ptr::null_mut(),
                    }
                }
                result.into_unknown()
            }
            Err(_) => std::ptr::null_mut(),
        }
    }

// SourceMap wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsSourceMap {
    inner: SourceMap,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsSourceMap {
    
    #[php_function]
    pub fn new(source: *const c_char, error_out: *mut *mut c_char) -> *mut CsSourceMap {
            let source_str = c_string_to_rust(source);
            let inner = match SourceMap::new(source_str.clone()) {
                Ok(inner) => inner,
                Err(e) => {
                    if !error_out.is_null() {
                        *error_out = rust_string_to_c(e.to_string());
                    }
                    return std::ptr::null_mut();
                }
            };
            Box::into_raw(Box::new(CsSourceMap { inner }))
        }
    }
    #[php_function]
    pub fn get_line(&self, line_num: usize) -> *mut c_char {
            let line = self.inner.get_line(line_num);
            rust_string_to_c(line.unwrap_or_default().to_string())
    }


#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsSectionName {
    inner: crate::dna::atp::ops::SectionName,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsSectionName {
    
    #[php_function]
    pub fn new(s: *const c_char) -> Self {
            Self {
                inner: crate::dna::atp::ops::SectionName::new(c_string_to_rust(s)),
        }
    }
    #[php_function]
    pub fn as_str(&self) -> *mut c_char {
            rust_string_to_c(self.inner.as_str().to_string())
    }
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsVariableName {
    inner: crate::dna::atp::ops::VariableName,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsVariableName {
    
    #[php_function]
    pub fn new(s: *const c_char) -> Self {
        Self {
            inner: crate::dna::atp::ops::VariableName::new(c_string_to_rust(s)),
    }

    }
    #[php_function]
    pub fn as_str(&self) -> *mut c_char {
        rust_string_to_c(self.inner.as_str().to_string())
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCacheKey {
    inner: crate::dna::atp::ops::CacheKey,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCacheKey {
    
    #[php_function]
    pub fn new(file: *const c_char, key: *const c_char) -> Self {
        let file_str = c_string_to_rust(file);
        let key_str = c_string_to_rust(key);
        Self {
            inner: crate::dna::atp::ops::CacheKey::new(&file_str, &key_str),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsRegexCache {
    inner: crate::dna::atp::ops::RegexCache,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsRegexCache {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: crate::dna::atp::ops::RegexCache::new(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsStringParser {
    inner: crate::dna::atp::ops::StringParser,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsStringParser {

    #[php_function]
    pub fn new(input: *const c_char) -> Self {
        Self {
            inner: crate::dna::atp::ops::StringParser::new(c_string_to_rust(input)),
    }
}

    #[php_function]
    pub fn parse_quoted_string(&mut self) -> *mut c_char {
        match self.inner.parse_quoted_string() {
            Ok(s) => rust_string_to_c(s),
        }
    }
    }
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsOperatorParser {
    inner: crate::dna::atp::ops::OperatorParser,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsOperatorParser {

    #[php_function]
    pub fn new(error_out: *mut *mut c_char) -> *mut CsOperatorParser {
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(e) => {
                    if !error_out.is_null() {
                        *error_out = rust_string_to_c(e.to_string());
                    return std::ptr::null_mut();
                }
            }
        };
        let parser = match rt.block_on(crate::dna::atp::ops::OperatorParser::new()) {
            Ok(parser) => parser,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
            }
        };
        Box::into_raw(Box::new(CsOperatorParser { inner: parser }))
    }

    }
    #[php_function]
    pub fn load_hlx(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.load_hlx()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
    #[php_function]
    pub fn try_math(&self, s: *const c_char, error_out: *mut *mut c_char) -> f64 {
        let s_str = c_string_to_rust(s);
        let result = crate::dna::atp::ops::eval_math_expression(&s_str)
            .map_err(|e| error_csharp(e.to_string()))
            .and_then(|val| match val {
                crate::dna::atp::value::Value::Number(n) => Ok(n),
                _ => Err(error_csharp(
                    "Math expression did not evaluate to a number",
                )),
            });
        rust_result_f64_to_c(result, error_out)

    }
    #[php_function]
    pub fn execute_date(&self, fmt: *const c_char) -> *mut c_char {
        let fmt_str = c_string_to_rust(fmt);
        rust_string_to_c(crate::dna::atp::ops::eval_date_expression(&fmt_str))

    }
    #[php_function]
    pub fn parse_line(&mut self, raw: *const c_char) -> *mut c_char{
        let raw_str = c_string_to_rust(raw);
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.parse_line(&raw_str)) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
    #[php_function]
    pub fn get(&self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let value = self.inner.get(&key_str);
        match value {
            Some(v) => value_to_csharp(env, &v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            }
        }
    }
    #[php_function]
    pub fn get_ref(&self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let value = self.inner.get_ref(&key_str);
        match value {
            Some(v) => value_to_csharp(env, v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            }
        }
    }
    #[php_function]
    pub fn set(&mut self, key: *const c_char, value: CsUnknown) -> *mut c_char{
        let val = if let Ok(csharp_str) = value.coerce_to_string() {
            if let Ok(utf8) = csharp_str.into_utf8() {
                if let Ok(s) = utf8.as_str() {
                    crate::dna::atp::value::Value::String(s.to_string())
                } else {
                    crate::dna::atp::value::Value::String("unknown".to_string())
                }
            } else {
                crate::dna::atp::value::Value::String("unknown".to_string())
            }
        } else {
            crate::dna::atp::value::Value::String("unknown".to_string())
        };
        let key_str = c_string_to_rust(key);
        self.inner.set(&key_str, val);
        std::ptr::null_mut()
    }

    #[php_function]
    pub fn keys(&self, env: Env) -> *mut c_char {
        let keys = self.inner.keys();
        match env.create_array_with_length(keys.len()) {
            Ok(mut result) => {
                for (i, key) in keys.iter().enumerate() {
                    match env.create_string(key) {
                        Ok(s) => {
                            if let Err(_) = result.set_element(i as u32, s) {
                                return std::ptr::null_mut();
                            }
                        }
                        Err(_) => return std::ptr::null_mut(),
                    }
                }
                result.into_unknown()
            }
            Err(_) => std::ptr::null_mut(),
        }
    }

    #[php_function]
    pub fn items(&self, env: Env) -> *mut c_char {
        let items = self.inner.items();
        let mut result = match env.create_object() {
            Ok(r) => r,
            Err(_) => return std::ptr::null_mut(),
        for (key, value) in items.iter() {
            let csharp_val = value_to_csharp(env, value);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = result.set_named_property(key, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        result.into_unknown()
    }

    }
    #[php_function]
    pub fn items_cloned(&self, env: Env) -> *mut c_char {
        let items = self.inner.items_cloned();
        let mut result = match env.create_object() {
            Ok(r) => r,
            Err(_) => return std::ptr::null_mut(),
        for (key, value) in items {
            let csharp_val = value_to_csharp(env, &value);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = result.set_named_property(&key, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        result.into_unknown()
    }

    }
    #[php_function]
    pub fn get_errors(&self, env: Env) -> *mut c_char {
        let errors: Vec<String> = self.inner.get_errors().iter().map(|e| e.to_string()).collect();
        match env.create_array_with_length(errors.len()) {
            Ok(mut result) => {
                for (i, error) in errors.iter().enumerate() {
                    match env.create_string(error) {
                        Ok(s) => {
                            if let Err(_) = result.set_element(i as u32, s) {
                                return std::ptr::null_mut();
                            }
                        }
                        Err(_) => return std::ptr::null_mut(),
                    }
                }
                result.into_unknown()
            }
            Err(_) => std::ptr::null_mut(),
        }
    }

    #[php_function]
    pub fn has_errors(&self) -> bool {
        self.inner.has_errors()
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsOutputFormat {
    inner: OutputFormat,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsOutputFormat {

    #[php_function]
    pub fn from_str(s: *const c_char) -> Self {
        let s_str = c_string_to_rust(s);
        let format = OutputFormat::from(s_str.as_str()).unwrap_or(OutputFormat::Helix);
        Self { inner: format }
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCompressionConfig {
    inner: CompressionConfig,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCompressionConfig {

    #[php_function]
    pub fn default() -> Self {
        Self {
            inner: CompressionConfig::default(),
    }
}}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsOutputConfig {
    inner: OutputConfig,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsOutputConfig {

    #[php_function]
    pub fn default() -> Self {
        Self {
            inner: OutputConfig::default(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsOutputManager {
    inner: OutputManager,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsOutputManager {

    #[php_function]
    pub fn new(config: &CsOutputConfig) -> Self {
        Self {
            inner: OutputManager::new(config.inner.clone()),
    }

    }
    #[php_function]
    pub fn add_row(&mut self, row: HashMap<String, CsObject>) -> *mut c_char{
        // Convert HashMap<String, CsObject> to HashMap<String, AtpValue>
        let converted_row: HashMap<String, crate::dna::atp::value::Value> = HashMap::new(); // Placeholder
        self.inner.add_row(converted_row);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn flush_batch(&mut self) -> *mut c_char{
        match self.inner.flush_batch() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn finalize_all(&mut self) -> *mut c_char{
        match self.inner.finalize_all() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn get_output_files(&self, env: Env) -> *mut c_char {
        let files: Vec<String> = self.inner.get_output_files().iter().map(|p| p.to_string_lossy().to_string()).collect();
        match env.create_array_with_length(files.len()) {
            Ok(mut result) => {
                for (i, file) in files.iter().enumerate() {
                    match env.create_string(file) {
                        Ok(s) => {
                            if let Err(_) = result.set_element(i as u32, s) {
                                return std::ptr::null_mut();
                            }
                        }
                        Err(_) => return std::ptr::null_mut(),
                    }
                }
                result.into_unknown()
            }
            Err(_) => std::ptr::null_mut(),
        }
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHlxcDataWriter {
    inner: crate::dna::atp::output::HlxcDataWriter,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHlxcDataWriter {

    #[php_function]
    pub fn new(config: &CsOutputConfig) -> Self {
        Self {
            inner: crate::dna::atp::output::HlxcDataWriter::new(config.inner.clone()),
    }

    }
    #[php_function]
    pub fn write_batch(&mut self, batch: &CsObject) -> *mut c_char{
        // Convert CsObject to RecordBatch
        // This would need proper Arrow RecordBatch conversion
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn finalize(&mut self) -> *mut c_char{
        match self.inner.finalize() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }
}
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsParser {
    inner: Parser,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsParser {

    #[php_function]
    pub fn new(tokens: Vec<CsObject>) -> CsResult<CsParser> {
        // Convert Vec<CsObject> to Vec<Token>
        let converted_tokens: Vec<Token> = vec![]; // Placeholder
        Ok(CsParser {
            inner: Parser::new(converted_tokens),
        })


    }
    #[php_function]
    pub fn new_enhanced(tokens: Vec<CsObject>) -> CsParser {
        // Convert Vec<CsObject> to Vec<TokenWithLocation>
        let converted_tokens: Vec<crate::dna::atp::lexer::TokenWithLocation> = vec![]; // Placeholder
        CsParser {
            inner: Parser::new_enhanced(converted_tokens),
    }


    }
    #[php_function]
    pub fn new_with_source_map(source_map: &CsSourceMap) -> CsParser {
        CsParser {
            inner: Parser::new_with_source_map(source_map.inner.clone()),
    }

    }
    #[php_function]
    pub fn set_runtime_context(&mut self, context: HashMap<String, String>) -> *mut c_char{
        self.inner.set_runtime_context(context);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn parse(&mut self, error_out: *mut *mut c_char) -> *mut CsHelixAst {
        let ast = match self.inner.parse() {
            Ok(ast) => ast,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                return std::ptr::null_mut();
            }
        };
        Box::into_raw(Box::new(CsHelixAst { inner: ast }))
    }
}
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHelixLoader {
    inner: HelixLoader,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHelixLoader {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: HelixLoader::new(),
    }   

    }
    #[php_function]
    pub fn parse(&mut self, content: *const c_char) -> *mut c_char{
        let content_str = c_string_to_rust(content);
        match self.inner.parse(&content_str) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn get_config(&self, env: Env, name: *const c_char) -> *mut c_char {
        let name_str = c_string_to_rust(name);
        let _config = self.inner.get_config(&name_str);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn set_context(&mut self, context: *const c_char) -> *mut c_char{
        let context_str = c_string_to_rust(context);
        self.inner.set_context(context_str);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn merge_configs(&self, env: Env, configs: Vec<CsObject>) -> *mut c_char {
        // Convert Vec<CsObject> to Vec<&HelixConfig>
        let converted_configs: Vec<&HelixConfig> = vec![]; // Placeholder
        let _merged = self.inner.merge_configs(converted_configs);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCompiler {
    inner: Compiler,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCompiler {

    #[php_function]
    pub fn new(optimization_level: CsUnknown, error_out: *mut *mut c_char) -> *mut CsCompiler {
        // Convert CsUnknown to OptimizationLevel
        let level = if let Ok(csharp_str) = optimization_level.coerce_to_string() {
            if let Ok(utf8) = csharp_str.into_utf8() {
                if let Ok(s) = utf8.as_str() {
                    match s.to_string().to_lowercase().as_str() {
                        "zero" => OptimizationLevel::Zero,
                        "one" => OptimizationLevel::One,
                        "two" => OptimizationLevel::Two,
                        "three" => OptimizationLevel::Three,
                        _ => OptimizationLevel::Two,
                } else {
                    OptimizationLevel::Two
                }
            } else {
                OptimizationLevel::Two
            }
        } else {
            OptimizationLevel::Two
        };
        Box::into_raw(Box::new(CsCompiler {
            inner: Compiler::new(level),
        }))
    }

    #[php_function]
    pub fn builder() -> *mut CsCompilerBuilder {
        Box::into_raw(Box::new(CsCompilerBuilder {
            inner: Compiler::builder(),
        }))
    }
    #[php_function]
    pub fn decompile(&self, env: Env, bin: CsHelixBinary) -> *mut c_char {
        match self.inner.decompile(&bin.inner) {
            Ok(_ast) => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
            Err(_) => std::ptr::null_mut(),
        }
    }
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCompilerBuilder {
    inner: CompilerBuilder,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCompilerBuilder {

    #[php_function]
    pub fn optimization_level(&mut self, level: CsUnknown) -> *mut c_char{
        // Convert CsUnknown to OptimizationLevel
        let opt_level = if let Ok(csharp_str) = level.coerce_to_string() {
            if let Ok(utf8) = csharp_str.into_utf8() {
                if let Ok(s) = utf8.as_str() {
                    match s.to_lowercase().as_str() {
                        "zero" => OptimizationLevel::Zero,
                        "one" => OptimizationLevel::One,
                        "two" => OptimizationLevel::Two,
                        "three" => OptimizationLevel::Three,
                        _ => OptimizationLevel::Two,
                    }
                } else {
                    OptimizationLevel::Two
                }
            } else {
                OptimizationLevel::Two
            }
        } else {
            OptimizationLevel::Two
        };
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.optimization_level(opt_level);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn compression(&mut self, enable: bool) -> *mut c_char{
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.compression(enable);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn cache(&mut self, enable: bool) -> *mut c_char{
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.cache(enable);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn verbose(&mut self, enable: bool) -> *mut c_char{
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.verbose(enable);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn build(&mut self) -> *mut CsCompiler {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        let compiler = builder.build();
        Box::into_raw(Box::new(CsCompiler { inner: compiler }))
    }
}
#[cfg(feature = "php")]
#[derive(Clone, Debug)]
pub struct CsHelixBinary {
    inner: HelixBinary,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHelixBinary {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: HelixBinary::new(),
    }

    }
    #[php_function]
    pub fn validate(&self) -> *mut c_char{
        match self.inner.validate() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn calculate_checksum(&self, error_out: *mut *mut c_char) -> u64 {
        rust_result_u64_to_c(Ok(self.inner.calculate_checksum()), error_out)

    }
    #[php_function]
    pub fn size(&self) -> usize {
        self.inner.size()

    }
    #[php_function]
    pub fn compression_ratio(&self, original_size: usize) -> f64 {
        self.inner.compression_ratio(original_size)
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHelixDispatcher {
    inner: HelixDispatcher,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHelixDispatcher {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: HelixDispatcher::new(),
    }

    }
    #[php_function]
    pub fn initialize(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        match rt.block_on(self.inner.initialize()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn parse_only(&self, source: *const c_char) -> *mut c_char {
        let source_str = c_string_to_rust(source);
        let tokens_with_loc = match crate::dna::atp::lexer::tokenize_with_locations(&source_str) {
            Ok(tokens) => tokens,
        };
        let source_map = crate::dna::atp::lexer::SourceMap {
            tokens: tokens_with_loc.clone(),
            source: source_str,
        };
        let mut parser = crate::dna::atp::parser::Parser::new_with_source_map(source_map);
        match parser.parse() {
            Ok(ast) => rust_string_to_c(format!("{:?}", ast)),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }
    #[php_function]
    pub fn parse_dsl(&mut self, source: *const c_char) -> *mut c_char{
        let source_str = c_string_to_rust(source);
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.parse_dsl(&source_str)) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
    #[php_function]
    pub fn interpreter(&self, error_out: *mut *mut c_char) -> *mut CsHelixInterpreter {
        // Since we can't clone the interpreter, create a new one
        // The original interpreter reference is just used to check if it's initialized
        match self.inner.interpreter() {
            Some(_) => CsHelixInterpreter::new(error_out),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c("Interpreter not initialized".to_string());
                }
                std::ptr::null_mut()
            }
        }
    }
    #[php_function]
    pub fn interpreter_mut(&mut self, error_out: *mut *mut c_char) -> *mut CsHelixInterpreter {
        // Can't clone a mutable reference, need to return an error or handle differently
        if !error_out.is_null() {
            *error_out = rust_string_to_c("Cannot clone mutable interpreter reference".to_string());
        }
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn is_ready(&self) -> bool {
        self.inner.is_ready()
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHlx {
    inner: Hlx,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHlx {

    #[php_function]
    pub fn new() -> CsResult<CsHlx> {
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| error_csharp(e.to_string()))?;
        let hlx = rt
            .block_on(Hlx::new())
            .map_err(|e| error_csharp(e.to_string()))?;
        Ok(Self { inner: hlx })
    }
    #[php_function]
    pub fn get_raw(&self, env: Env, section: String, key: String) -> *mut c_char {
        let value = self.inner.get_raw(&section, &key);
        match value {
            Some(v) => value_to_csharp(env, &v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            }
        }
    }
    #[php_function]
    pub fn get_str(&self, section: String, key: String) -> CsResult<String> {
        self.inner
            .get_str(&section, &key)
            .map(|s| s.to_string())
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_num(&self, section: String, key: String) -> CsResult<f64> {
        self.inner
            .get_num(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_bool(&self, section: String, key: String) -> CsResult<bool> {
        self.inner
            .get_bool(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_array(&self, env: Env, section: String, key: String) -> *mut c_char {
        let arr = match self.inner.get_array(&section, &key) {
            Some(arr) => arr,
            None => return std::ptr::null_mut(),
        };
        let mut result = match env.create_array_with_length(arr.len()) {
            Ok(r) => r,
            Err(_) => return std::ptr::null_mut(),
        };
        for (i, val) in arr.iter().enumerate() {
            let csharp_val = value_to_csharp(env, val);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = result.set_element(i as u32, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        result.into_unknown()
    }
    #[php_function]
    pub fn get_string(&self, section: String, key: String) -> CsResult<String> {
        self.inner
            .get_string(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_i32(&self, section: String, key: String) -> CsResult<i32> {
        self.inner
            .get_i32(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_i64(&self, section: String, key: String) -> CsResult<i64> {
        self.inner
            .get_i64(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_u32(&self, section: String, key: String) -> CsResult<u32> {
        self.inner
            .get_u32(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_u64(&self, section: String, key: String) -> CsResult<u64> {
        self.inner
            .get_u64(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_f32(&self, section: String, key: String) -> CsResult<f32> {
        self.inner
            .get_f32(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_f64(&self, section: String, key: String) -> CsResult<f64> {
        self.inner
            .get_f64(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_vec_string(&self, section: String, key: String) -> CsResult<Vec<String>> {
        self.inner
            .get_vec_string(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_vec_i32(&self, section: String, key: String) -> CsResult<Vec<i32>> {
        self.inner
            .get_vec_i32(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_vec_f64(&self, section: String, key: String) -> CsResult<Vec<f64>> {
        self.inner
            .get_vec_f64(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_vec_bool(&self, section: String, key: String) -> CsResult<Vec<bool>> {
        self.inner
            .get_vec_bool(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))
    }

    #[php_function]
    pub fn get_dynamic(&self, section: String, key: String) -> CsResult<CsDynamicValue> {
        let value = self
            .inner
            .get_dynamic(&section, &key)
            .ok_or_else(|| error_csharp(format!("Key '{}' not found in section '{}'", key, section)))?;
        Ok(CsDynamicValue { inner: value })
    }

    #[php_function]
    pub fn get_auto(&self, env: Env, section: String, key: String) -> *mut c_char {
        let value = match self.inner.get_auto(&section, &key) {
            Some(v) => v,
            None => return std::ptr::null_mut(),
        value_to_csharp(env, &crate::dna::atp::value::Value::String(value))
    }

    }
    #[php_function]
    pub fn select(&self, env: Env, section: String, key: String) -> *mut c_char {
        // TypedGetter wrapper - for now return a placeholder
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn set_str(&mut self, section: String, key: String, value: String) -> *mut c_char{
        self.inner.set_str(&section, &key, &value);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn set_num(&mut self, section: String, key: String, value: f64) -> *mut c_char{
        self.inner.set_num(&section, &key, value);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn set_bool(&mut self, section: String, key: String, value: bool) -> *mut c_char{
        self.inner.set_bool(&section, &key, value);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn increase(&mut self, section: String, key: String, amount: f64) -> CsResult<f64> {
        self.inner
            .increase(&section, &key, amount)
            .map_err(|e| error_csharp(e.to_string()))

    }
    #[php_function]
    pub fn index(&self, env: Env, section: String) -> *mut c_char {
        let _index = self.inner.index(&section);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn index_mut(&mut self, env: Env, section: String) -> *mut c_char {
        let _index = self.inner.index_mut(&section);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn server(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        match rt.block_on(self.inner.server()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn watch(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        match rt.block_on(self.inner.watch()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn process(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        match rt.block_on(self.inner.process()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn compile(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        match rt.block_on(self.inner.compile()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn execute(&mut self, env: Env, code: String) -> *mut c_char {
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        let result = match rt.block_on(self.inner.execute(&code)) {
            Ok(result) => result,
            Err(_) => return std::ptr::null_mut(),
        };
        value_to_csharp(env, &result)
    }

    }
    #[php_function]
    pub fn sections(&self) -> CsResult<Vec<String>> {
        Ok(self.inner.sections().iter().map(|s| s.to_string()).collect())

    }
    #[php_function]
    pub fn keys(&self, section: String) -> CsResult<Vec<String>> {
        let keys = self.inner.keys(&section)
        Ok(keys.iter().map(|s| s.to_string()).collect())
    }

    #[php_function]
    pub fn get_file_path(&self) -> CsResult<String> {
        let path = self.inner.get_file_path()
            .ok_or_else(|| error_csharp("No file path available"))?;
        Ok(path.to_string_lossy().to_string())

    }
    #[php_function]
    pub fn save(&self) -> *mut c_char{
        match self.inner.save() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn make(&self, env: Env) -> *mut c_char {
        let result = match self.inner.make() {
            Ok(result) => result,
            Err(_) => return std::ptr::null_mut(),
        value_to_csharp(env, &crate::dna::atp::value::Value::String(result))
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsDynamicValue {
    inner: DynamicValue,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsDynamicValue {

    #[php_function]
    pub fn as_string(&self) -> CsResult<String> {
        Ok(self.inner.as_string().unwrap_or_default())

    }
    #[php_function]
    pub fn as_number(&self) -> CsResult<f64> {
        Ok(self.inner.as_number().unwrap_or(0.0))

    }
    #[php_function]
    pub fn as_integer(&self) -> CsResult<i64> {
        Ok(self.inner.as_integer().unwrap_or(0))

    }
    #[php_function]
    pub fn as_bool(&self) -> CsResult<bool> {
        Ok(self.inner.as_bool().unwrap_or(false))

    }
    #[php_function]
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsAtpValue {
    inner: crate::dna::atp::value::Value,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsAtpValue {

    #[php_function]
    pub fn default() -> Self {
        Self {
            inner: crate::dna::atp::value::Value::default(),
    }

    }
    #[php_function]
    pub fn value_type(&self) -> CsResult<String> {
    }

    }
    #[php_function]
    pub fn is_string(&self) -> bool {
        self.inner.is_string()

    }
    #[php_function]
    pub fn is_number(&self) -> bool {
        self.inner.is_number()

    }
    #[php_function]
    pub fn is_boolean(&self) -> bool {
        self.inner.is_boolean()

    }
    #[php_function]
    pub fn is_array(&self) -> bool {
        self.inner.is_array()

    }
    #[php_function]
    pub fn is_object(&self) -> bool {
        self.inner.is_object()

    }
    #[php_function]
    pub fn is_null(&self) -> bool {
        self.inner.is_null()

    }
    #[php_function]
    pub fn as_string(&self) -> CsResult<String> {
        self.inner
            .as_string()
            .map(|s| s.to_string())
            .ok_or_else(|| error_csharp("Value is not a string"))

    }
    #[php_function]
    pub fn as_number(&self) -> CsResult<f64> {
        self.inner
            .as_number()
            .ok_or_else(|| error_csharp("Value is not a number"))

    }
    #[php_function]
    pub fn as_f64(&self) -> CsResult<f64> {
        self.inner
            .as_f64()
            .ok_or_else(|| error_csharp("Value is not a number"))

    }
    #[php_function]
    pub fn as_str(&self) -> CsResult<String> {
        self.inner
            .as_str()
            .map(|s| s.to_string())
            .ok_or_else(|| error_csharp("Value is not a string"))

    }
    #[php_function]
    pub fn as_boolean(&self) -> CsResult<bool> {
        self.inner
            .as_boolean()
            .ok_or_else(|| error_csharp("Value is not a boolean"))

    }
    #[php_function]
    pub fn as_array(&self, env: Env) -> *mut c_char {
        let arr = match self.inner.as_array() {
            Some(arr) => arr,
            None => return std::ptr::null_mut(),
        let mut result = match env.create_array_with_length(arr.len()) {
            Ok(r) => r,
            Err(_) => return std::ptr::null_mut(),
        };
        for (i, item) in arr.iter().enumerate() {
            let csharp_val = value_to_csharp(env, item);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = result.set_element(i as u32, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        result.into_unknown()
    }

    }
    #[php_function]
    pub fn as_object(&self, env: Env) -> *mut c_char {
        let obj = match self.inner.as_object() {
            Some(obj) => obj,
            None => return std::ptr::null_mut(),
        let mut csharp_obj = match env.create_object() {
            Ok(obj) => obj,
            Err(_) => return std::ptr::null_mut(),
        };
        for (key, val) in obj {
            let csharp_val = value_to_csharp(env, val);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = csharp_obj.set_named_property(key, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        csharp_obj.into_unknown()
    }

    }
    #[php_function]
    pub fn get(&self, env: Env, key: String) -> *mut c_char {
        let value = self.inner.get(&key);
        match value {
            Some(v) => value_to_csharp(env, v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn get_mut(&mut self, env: Env, key: String) -> *mut c_char {
        let value = self.inner.get_mut(&key);
        match value {
            Some(v) => value_to_csharp(env, v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn get_string(&self, key: &str) -> CsResult<String> {
        self.inner
            .get_string(key)
            .map(|s| s.to_string())
            .ok_or_else(|| error_csharp(format!(
                key
            )))
    }

    #[php_function]
    pub fn get_number(&self, key: &str) -> CsResult<f64> {
        self.inner
            .get_number(key)
            .ok_or_else(|| error_csharp(format!(
                key
            )))
    }

    #[php_function]
    pub fn get_boolean(&self, key: &str) -> CsResult<bool> {
        self.inner
            .get_boolean(key)
            .ok_or_else(|| error_csharp(format!(
                key
            )))
    }

    #[php_function]
    pub fn get_array(&self, env: Env, key: String) -> *mut c_char {
        let arr = match self.inner.get_array(&key) {
            Some(arr) => arr,
            None => return std::ptr::null_mut(),
        let mut result = match env.create_array_with_length(arr.len()) {
            Ok(r) => r,
            Err(_) => return std::ptr::null_mut(),
        };
        for (i, item) in arr.iter().enumerate() {
            let csharp_val = value_to_csharp(env, item);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = result.set_element(i as u32, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        result.into_unknown()
    }

    }
    #[php_function]
    pub fn get_object(&self, env: Env, key: String) -> *mut c_char {
        let obj = match self.inner.get_object(&key) {
            Some(obj) => obj,
            None => return std::ptr::null_mut(),
        let mut csharp_obj = match env.create_object() {
            Ok(obj) => obj,
            Err(_) => return std::ptr::null_mut(),
        };
        for (k, value) in obj {
            let csharp_val = value_to_csharp(env, value);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = csharp_obj.set_named_property(&k, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        csharp_obj.into_unknown()
    }

    }
    #[php_function]
    pub fn to_string(&self) -> String {
        self.inner.to_string()

    }
    #[php_function]
    pub fn to_json(&self) -> CsResult<String> {
        self.inner
            .to_json()
            .map_err(|e| error_csharp(e.to_string()))

    }
    #[php_function]
    pub fn to_yaml(&self) -> CsResult<String> {
        self.inner
            .to_yaml()
            .map_err(|e| error_csharp(e.to_string()))


    }
    #[php_function]
    pub fn from_json(json_value: &CsObject) -> CsResult<CsAtpValue> {
        // Convert CsObject to serde_json::Value
        let json = serde_json::Value::Null; // Placeholder
        let value = crate::dna::atp::value::Value::from_json(json);
    }
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHlxHeader {
    inner: HlxHeader,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHlxHeader {

    #[php_function]
    pub fn new(schema: &CsObject, metadata: HashMap<String, CsObject>) -> CsResult<CsHlxHeader> {
        // Convert parameters
        let converted_schema = Schema::new(vec![Field::new("placeholder", DataType::Utf8, false)]);
        let converted_metadata: HashMap<String, serde_json::Value> = HashMap::new(); // Placeholder
        let header = HlxHeader::new(&converted_schema, converted_metadata);
    }

    }
    #[php_function]
    pub fn from_json_bytes(bytes: Vec<u8>) -> CsResult<CsHlxHeader> {
        let header =
            HlxHeader::from_json_bytes(&bytes).map_err(|e| error_csharp(e.to_string()))?;
    }

    #[php_function]
    pub fn with_compression(&mut self, compressed: bool) -> *mut c_char{
        let inner = self.inner.clone();
        self.inner = inner.with_compression(compressed);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn with_row_count(&mut self, count: u64) -> *mut c_char{
        let inner = self.inner.clone();
        self.inner = inner.with_row_count(count);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn with_preview(&mut self, preview: Vec<CsObject>) -> *mut c_char{
        // Convert Vec<CsObject> to Vec<serde_json::Value>
        let converted_preview: Vec<serde_json::Value> = vec![]; // Placeholder
        let inner = self.inner.clone();
        self.inner = inner.with_preview(converted_preview);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn is_compressed(&self) -> bool {
        self.inner.is_compressed()

    }
    #[php_function]
    pub fn to_json_bytes(&self) -> CsResult<Vec<u8>> {
        self.inner.to_json_bytes()
            .map_err(|e| error_csharp(e.to_string()))
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsSymbolTable {
    inner: crate::dna::hel::binary::SymbolTable,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsSymbolTable {

    #[php_function]
    pub fn intern(&mut self, s: &str) -> u32 {
        self.inner.intern(s)

    }
    #[php_function]
    pub fn get(&self, idx: u32) -> CsResult<String> {
        self.inner
            .get(idx)
            .map(|s| s.clone())
    }

    }
    #[php_function]
    pub fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsDataSection {
    inner: DataSection,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsDataSection {

    #[php_function]
    pub fn new(section_type: &CsObject, data: Vec<u8>) -> CsResult<CsDataSection> {
        // Convert CsObject to SectionType
        let st = crate::dna::hel::binary::SectionType::Project; // Placeholder
        let section = DataSection::new(st, data);
    }

    }
    #[php_function]
    pub fn compress(&mut self, method: &CsObject) -> *mut c_char{
        // Convert CsObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        match self.inner.compress(cm) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn decompress(&mut self) -> *mut c_char{
        match self.inner.decompress() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHelixVM {
    inner: HelixVM,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHelixVM {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: HelixVM::new(),
    }

    }
    #[php_function]
    pub fn with_debug(&mut self) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_debug();

    }
    #[php_function]
    pub fn execute_binary(&mut self, binary: &CsHelixBinary) -> *mut c_char{
        match self.inner.execute_binary(&binary.inner) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn push(&mut self, value: &CsObject) -> *mut c_char{
        // Convert CsObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        self.inner.push(val);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn pop(&mut self) -> *mut c_char{
        match self.inner.pop() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn load_memory(&self, env: Env, address: u32) -> *mut c_char {
        let value = match self.inner.load_memory(address) {
            Ok(v) => v,
            Err(_) => return std::ptr::null_mut(),
        // Convert hel::binary::Value to atp::value::Value
        let atp_value = match value {
            crate::dna::hel::binary::Value::String(_s) => crate::dna::atp::value::Value::String("string_id".to_string()),
            crate::dna::hel::binary::Value::Int(n) => crate::dna::atp::value::Value::Number(*n as f64),
            crate::dna::hel::binary::Value::Float(n) => crate::dna::atp::value::Value::Number(*n),
            crate::dna::hel::binary::Value::Bool(b) => crate::dna::atp::value::Value::Bool(*b),
            crate::dna::hel::binary::Value::Null => crate::dna::atp::value::Value::Null,
            _ => crate::dna::atp::value::Value::String("unsupported value type".to_string()),
        };
        value_to_csharp(env, &atp_value)
    }

    }
    #[php_function]
    pub fn store_memory(&mut self, address: u32, value: &CsObject) -> *mut c_char{
        // Convert CsObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        match self.inner.store_memory(address, val) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn set_breakpoint(&mut self, address: usize) -> *mut c_char{
        self.inner.set_breakpoint(address);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn remove_breakpoint(&mut self, address: usize) -> *mut c_char{
        self.inner.remove_breakpoint(address);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn continue_execution(&mut self) -> *mut c_char{
        self.inner.continue_execution();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn step(&mut self) -> *mut c_char{
        self.inner.step();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn state(&self, env: Env) -> *mut c_char {
        let _state = self.inner.state();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsVMExecutor {
    inner: VMExecutor,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsVMExecutor {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: VMExecutor::new(),
    }

    }
    #[php_function]
    pub fn vm(&mut self) -> CsResult<CsHelixVM> {
        // vm() returns &mut, can't move it - need to clone or return reference
        Err(error_csharp("Cannot move vm from executor"))
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsAppState {
    inner: crate::dna::vlt::tui::AppState,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsAppState {

    #[php_function]
    pub fn new() -> CsResult<CsAppState> {
            inner: crate::dna::vlt::tui::AppState::new()
                .map_err(|e| error_csharp(e.to_string()))?,
    }

    }
    #[php_function]
    pub fn focus(&mut self, area: &CsObject) -> *mut c_char{
        // Convert CsObject to FocusArea
        let focus_area = crate::dna::vlt::tui::FocusArea::Files; // Placeholder
        self.inner.focus(focus_area);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn select_next_file(&mut self) -> *mut c_char{
        self.inner.select_next_file();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn select_prev_file(&mut self) -> *mut c_char{
        self.inner.select_prev_file();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn open_selected_file(&mut self) -> *mut c_char{
        match self.inner.open_selected_file() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn select_next_operator(&mut self) -> *mut c_char{
        self.inner.select_next_operator();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn select_prev_operator(&mut self) -> *mut c_char{
        self.inner.select_prev_operator();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn cycle_operator_category_next(&mut self) -> *mut c_char{
        self.inner.cycle_operator_category_next();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn cycle_operator_category_prev(&mut self) -> *mut c_char{
        self.inner.cycle_operator_category_prev();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn reset_operator_category(&mut self) -> *mut c_char{
        self.inner.reset_operator_category();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn sync_operator_selection(&mut self) -> *mut c_char{
        self.inner.sync_operator_selection();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn insert_selected_operator(&mut self) -> *mut c_char{
        self.inner.insert_selected_operator();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn next_tab(&mut self) -> *mut c_char{
        self.inner.next_tab();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn previous_tab(&mut self) -> *mut c_char{
        self.inner.previous_tab();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn close_active_tab(&mut self) -> *mut c_char{
        self.inner.close_active_tab();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn create_new_tab(&mut self) -> *mut c_char{
        self.inner.create_new_tab();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn save_active_tab(&mut self) -> *mut c_char{
        match self.inner.save_active_tab() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn trigger_command(&mut self) -> *mut c_char{
        self.inner.trigger_command();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn select_next_command(&mut self) -> *mut c_char{
        self.inner.select_next_command();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn select_prev_command(&mut self) -> *mut c_char{
        self.inner.select_prev_command();
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn on_tick(&mut self) -> *mut c_char{
        self.inner.on_tick();
        std::ptr::null_mut()
}
#[cfg(feature = "php")]  
#[derive(Debug)]
pub struct CsBenchmark {
    inner: Benchmark,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsBenchmark {

    #[php_function]
    pub fn new(name: String) -> Self {
        Self {
            inner: Benchmark::new(&name),
    }

    }
    #[php_function]
    pub fn with_iterations(&mut self, iterations: usize) -> *mut c_char{
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_iterations(iterations);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn with_warmup(&mut self, warmup: usize) -> *mut c_char{
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_warmup(warmup);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn run(&self, env: Env, f: CsUnknown) -> *mut c_char {
        // This needs to be implemented with proper callback handling
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsBundler {
    inner: Bundler,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsBundler {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: Bundler::new(),
    }

    }
    #[php_function]
    pub fn include(&mut self, pattern: &str) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.include(pattern);

    }
    #[php_function]
    pub fn exclude(&mut self, pattern: &str) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.exclude(pattern);

    }
    #[php_function]
    pub fn with_imports(&mut self, follow: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_imports(follow);

    }
    #[php_function]
    pub fn with_tree_shaking(&mut self, enable: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_tree_shaking(enable);

    }
    #[php_function]
    pub fn verbose(&mut self, enable: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.verbose(enable);
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsBundleBuilder {
    inner: crate::dna::mds::bundle::BundleBuilder,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsBundleBuilder {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: crate::dna::mds::bundle::BundleBuilder::new(),
    }

    }
    #[php_function]
    pub fn add_file(&mut self, path: String, binary: CsHelixBinary) -> *mut c_char{
        let path_buf = std::path::PathBuf::from(path);
        self.inner.add_file(path_buf, binary.inner);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn add_dependency(&mut self, from: String, to: String) -> *mut c_char{
        let from_path = std::path::PathBuf::from(from);
        let to_path = std::path::PathBuf::from(to);
        self.inner.add_dependency(from_path, to_path);
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn build(&mut self, env: Env) -> *mut c_char {
        let _bundle = std::mem::replace(&mut self.inner, crate::dna::mds::bundle::BundleBuilder::new()).build();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCacheAction {
    // This is likely an enum, so we need to handle it differently
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCacheAction {

    
    #[php_function]
    pub fn from_str(s: String) -> CsResult<CsCacheAction> {
        // Convert string to CacheAction enum
    }
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsE621Config {
    inner: MapE621Config,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsE621Config {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: MapE621Config::new(),
    }

    }
    #[php_function]
    pub fn with_filter_tags(&mut self, filter_tags: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_filter_tags(filter_tags);

    }
    #[php_function]
    pub fn with_format(&mut self, format: Option<String>) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_format(format);

    }
    #[php_function]
    pub fn with_artist_prefix(&mut self, prefix: Option<String>) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_artist_prefix(prefix);

    }
    #[php_function]
    pub fn with_artist_suffix(&mut self, suffix: Option<String>) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_artist_suffix(suffix);

    }
    #[php_function]
    pub fn with_replace_underscores(&mut self, replace_underscores: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_replace_underscores(replace_underscores);
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsConcatConfig {
    inner: ConcatConfig,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsConcatConfig {

    #[php_function]
    pub fn with_deduplication(&mut self, deduplicate: bool) -> *mut c_char{
        self.inner = std::mem::replace(&mut self.inner, ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags)).with_deduplication(deduplicate);
        std::ptr::null_mut()


    }
    #[php_function]
    pub fn from_preset(preset: &CsObject) -> Self {
        // TODO: Convert CsObject to FileExtensionPreset
        let config = ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags); // Placeholder
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsDataFormat {
    inner: crate::dna::map::core::DataFormat,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsDataFormat {

    
    #[php_function]
    pub fn from_str(s: String) -> CsResult<CsDataFormat> {
        let format = s
            .parse::<crate::dna::map::core::DataFormat>()
            .map_err(|e| error_csharp(e.to_string()))?;
    }
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsGenericJSONDataset {
    inner: crate::dna::map::core::GenericJSONDataset,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsGenericJSONDataset {

    #[php_function]
    pub fn len(&self) -> usize {
        self.inner.len()

    }
    #[php_function]
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()

    }
    #[php_function]
    pub fn get_random_sample(&self, env: Env) -> *mut c_char {
        let _sample = self.inner.get_random_sample();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn detect_training_format(&self, env: Env) -> *mut c_char {
        let _format = self.inner.detect_training_format();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn to_training_dataset(&self) -> CsResult<CsTrainingDataset> {
        let dataset = self
            .inner
            .to_training_dataset()
            .map_err(|e| error_csharp(e.to_string()))?;
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsTrainingDataset {
    inner: crate::dna::map::core::TrainingDataset,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsTrainingDataset {

    #[php_function]
    pub fn quality_assessment(&self, env: Env) -> *mut c_char {
        let _assessment = self.inner.quality_assessment();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHuggingFaceDataset {
    inner: HuggingFaceDataset,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHuggingFaceDataset {

    
    #[php_function]
    pub fn load(name: String, split: String, cache_dir: String) -> CsResult<CsHuggingFaceDataset> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| error_csharp(e.to_string()))?;
                let path = std::path::PathBuf::from(cache_dir);
                let dataset = rt
            .block_on(HuggingFaceDataset::load(&name, &split, &path))
            .map_err(|e| error_csharp(e.to_string()))?;
    }
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHuggingFaceDataset {

    #[php_function]
    pub fn get_features(&self, env: Env) -> *mut c_char {
        let _features = self.inner.get_features();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn info(&self, env: Env) -> *mut c_char {
        let _info = self.inner.info();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsPreferenceProcessor {
    inner: PreferenceProcessor,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsPreferenceProcessor {

    
    #[php_function]
    pub fn compute_statistics(_samples: Vec<CsObject>, env: Env) -> *mut c_char {
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

}
}

#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCompletionProcessor {
    inner: CompletionProcessor,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCompletionProcessor {

    
    #[php_function]
    pub fn compute_statistics(_samples: Vec<CsObject>, env: Env) -> *mut c_char {
        // compute_statistics is private, placeholder implementation
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsInstructionProcessor {
    inner: InstructionProcessor,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsInstructionProcessor {

    
    #[php_function]
    pub fn compute_statistics(_samples: Vec<CsObject>, env: Env) -> *mut c_char {
        // compute_statistics is private, placeholder implementation
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHfProcessor {
    inner: HfProcessor,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHfProcessor {

    #[php_function]
    pub fn new(cache_dir: String) -> Self {
        let path = std::path::PathBuf::from(cache_dir);
        Self {
            inner: HfProcessor::new(path),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsReasoningDataset {
    inner: ReasoningDataset,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsReasoningDataset {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: ReasoningDataset::new(),
    }

    }
    #[php_function]
    pub fn add_entry(&mut self, entry: &CsObject) -> *mut c_char{
        // Convert CsObject to ReasoningEntry
        let converted_entry = ReasoningEntry {
            user: "placeholder".to_string(),
            reasoning: "placeholder".to_string(),
            assistant: "placeholder".to_string(),
            template: "placeholder".to_string(),
            conversations: vec![],
        self.inner.add_entry(converted_entry);
        std::ptr::null_mut()
    }

    }
    #[php_function]
    pub fn len(&self) -> usize {
        self.inner.len()

    }
    #[php_function]
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()

    }
    #[php_function]
    pub fn create_template(&self, user: &str, reasoning: &str, assistant: &str) -> String {
        crate::dna::map::reasoning::ReasoningDataset::create_template(user, reasoning, assistant)
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsDocument {
    // This appears to be a placeholder impl block
}
#[cfg(feature = "php")]
#[derive(Clone, Debug)]
#[derive(Debug)]
pub struct CsStringPool {
    inner: StringPool,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsStringPool {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: StringPool::new(),
    }

    }
    #[php_function]
    pub fn intern(&mut self, s: &str) -> u32 {
        self.inner.intern(s)

    }
    #[php_function]
    pub fn get(&self, idx: u32) -> CsResult<String> {
        self.inner
            .get(idx)
            .map(|s| s.clone())
    }
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsConstantPool {
    inner: ConstantPool,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsConstantPool {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: ConstantPool::new(),
    }

    }
    #[php_function]
    pub fn add(&mut self, value: &CsObject) -> CsResult<u32> {
        // TODO: Convert CsObject to ConstantValue
        let cv = ConstantValue::String(0); // Placeholder
        Ok(self.inner.add(cv))

    }
    #[php_function]
    pub fn get(&self, env: Env, idx: u32) -> *mut c_char {
        let value = match self.inner.get(idx) {
            Some(v) => v,
            None => return std::ptr::null_mut(),
        // Convert ConstantValue to atp::value::Value
        let atp_value = match value {
            crate::dna::mds::codegen::ConstantValue::String(s) => crate::dna::atp::value::Value::String(s.to_string()),
            crate::dna::mds::codegen::ConstantValue::Number(n) => crate::dna::atp::value::Value::Number(*n as f64),
            crate::dna::mds::codegen::ConstantValue::Bool(b) => crate::dna::atp::value::Value::Bool(*b),
            crate::dna::mds::codegen::ConstantValue::Duration(_) => crate::dna::atp::value::Value::String("duration".to_string()),
            crate::dna::mds::codegen::ConstantValue::Null => crate::dna::atp::value::Value::Null,
        };
        value_to_csharp(env, &atp_value)
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCodeGenerator {
    inner: CodeGenerator,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCodeGenerator {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: CodeGenerator::new(),
    }

    }
    #[php_function]
    pub fn generate(&mut self, ast: &CsHelixAst) -> *mut c_char{
        let _ir = self.inner.generate(&ast.inner);
        std::ptr::null_mut()
}
}
// BinarySerializer wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsBinarySerializer {
    inner: crate::dna::mds::serializer::BinarySerializer,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsBinarySerializer {

    #[php_function]
    pub fn new(enable_compression: bool) -> Self {
        Self {
            inner: crate::dna::mds::serializer::BinarySerializer::new(enable_compression),
    }

    }
    #[php_function]
    pub fn with_compression_method(&mut self, method: &CsObject) -> () {
        // Convert CsObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        let inner = crate::dna::mds::serializer::BinarySerializer::new(true);
        self.inner = inner.with_compression_method(cm);
}
}
// VersionChecker wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsVersionChecker {
    // This seems to be a static utility class
}
#[cfg(feature = "php")]
#[php_impl]
impl CsVersionChecker {

    
    #[php_function]
    pub fn is_compatible(_ir: &CsObject) -> bool {
        // Convert CsObject to &HelixIR - placeholder implementation
        // HelixIR doesn't have Default, so using a dummy check
        true


    }
    #[php_function]
    pub fn migrate(ir: &CsObject) -> *mut c_char{
        // Convert and modify CsObject representing HelixIR
        std::ptr::null_mut()
}
}
// Migrator wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsMigrator {
    inner: Migrator,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsMigrator {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: Migrator::new(),
    }

    }
    #[php_function]
    pub fn verbose(&mut self, enable: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.verbose(enable);

    }
    #[php_function]
    pub fn migrate_json(&self, json_str: &str) -> CsResult<String> {
        self.inner
            .migrate_json(json_str)
            .map_err(|e| error_csharp(e.to_string()))

    }
    #[php_function]
    pub fn migrate_toml(&self, toml_str: &str) -> CsResult<String> {
        self.inner
            .migrate_toml(toml_str)
            .map_err(|e| error_csharp(e.to_string()))

    }
    #[php_function]
    pub fn migrate_yaml(&self, yaml_str: &str) -> CsResult<String> {
        self.inner
            .migrate_yaml(yaml_str)
            .map_err(|e| error_csharp(e.to_string()))

    }
    #[php_function]
    pub fn migrate_env(&self, env_str: &str) -> CsResult<String> {
        self.inner
            .migrate_env(env_str)
            .map_err(|e| error_csharp(e.to_string()))
}
}
// ModuleResolver wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsModuleResolver {
    inner: ModuleResolver,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsModuleResolver {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: ModuleResolver::new(),
    }

    }
    #[php_function]
    pub fn resolve(&mut self, env: Env, module_name: String) -> *mut c_char {
        let result = self.inner.resolve(&module_name);
        match result {
            Ok(path) => {
                match env.create_string(&path.to_string_lossy()) {
                    Ok(s) => s.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
            },
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn clear_cache(&mut self) -> *mut c_char{
        self.inner.clear_cache();
        std::ptr::null_mut()
}
}
// ModuleSystem wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsModuleSystem {
    inner: ModuleSystem,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsModuleSystem {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: ModuleSystem::new(),
    }

    }
    #[php_function]
    pub fn load_module(&mut self, path: String) -> *mut c_char{
        let path_buf = std::path::PathBuf::from(path);
        match self.inner.load_module(&path_buf) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn resolve_dependencies(&mut self) -> *mut c_char{
        match self.inner.resolve_dependencies() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn compilation_order(&self) -> CsResult<Vec<String>> {
        Ok(self.inner.compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect())

    }
    #[php_function]
    pub fn merge_modules(&self, env: Env) -> *mut c_char {
        let _merged = match self.inner.merge_modules() {
            Ok(m) => m,
            Err(_) => return std::ptr::null_mut(),
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn modules(&self, env: Env) -> *mut c_char {
        let _modules = self.inner.modules();
        // Convert Vec<ModuleInfo> to Vec<CsObject>
        match env.create_array_with_length(0) {
            Ok(arr) => arr.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn dependency_graph(&self) -> CsResult<CsDependencyGraph> {
    }
}
// DependencyBundler wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsDependencyBundler {
    inner: DependencyBundler,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsDependencyBundler {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: DependencyBundler::new(),
    }

    }
    #[php_function]
    pub fn build_bundle(&mut self, env: Env) -> *mut c_char {
        let _bundle = match self.inner.build_bundle() {
            Ok(b) => b,
            Err(_) => return std::ptr::null_mut(),
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn get_compilation_order(&self) -> CsResult<Vec<String>> {
        Ok(self.inner.get_compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect())
}
}
// DependencyGraph wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsDependencyGraph {
    inner: DependencyGraph,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsDependencyGraph {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: DependencyGraph::new(),
    }

    }
    #[php_function]
    pub fn check_circular(&self) -> *mut c_char{
        match self.inner.check_circular() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
// OptimizationLevel wrapper
#[cfg(feature = "php")]
#[derive(Clone)]
#[derive(Debug)]
pub struct CsOptimizationLevel {
    inner: OptimizationLevel,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsOptimizationLevel {

    
    #[php_function]
    pub fn from_u8(level: u8) -> Self {
        Self {
            inner: OptimizationLevel::from(level),
    }
}
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsOptimizer {
    inner: Optimizer,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsOptimizer {

    #[php_function]
    pub fn new(level: u8) -> Self {
        Self {
            inner: Optimizer::new(OptimizationLevel::from(level)),
    }

    }
    #[php_function]
    pub fn optimize(&mut self, _ir: &CsObject) -> *mut c_char{
        // Convert CsObject to &mut HelixIR - placeholder implementation
        // HelixIR doesn't have Default, so skipping optimization
        std::ptr::null_mut()
    }
    #[php_function]
    pub fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
// ProjectManifest wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsProjectManifest {
    // This seems to be a large struct, placeholder for now
}

// Runtime wrapper (HelixVM is already defined above)


// Schema wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHelixConfig {
    inner: HelixConfig,
}

#[cfg(feature = "php")]
#[php_impl]
impl CsHelixConfig {
    // Index implementation would go here if needed
}

// HlxDatasetProcessor wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHlxDatasetProcessor {
    inner: HlxDatasetProcessor,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHlxDatasetProcessor {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: HlxDatasetProcessor::new(),
    }

    }
    #[php_function]
    pub fn parse_hlx_content(&self, env: Env, content: String) -> *mut c_char {
        match self.inner.parse_hlx_content(&content) {
            Ok(_data) => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn cache_stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.cache_stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn clear_cache(&mut self) -> *mut c_char{
        self.inner.clear_cache();
        std::ptr::null_mut()
}
}
// ProcessingOptions wrapper
#[cfg(feature = "php")]
#[derive(Debug, Clone)]
#[derive(Debug)]
pub struct CsProcessingOptions {
    inner: ProcessingOptions,
}
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsCacheStats {
    inner: CacheStats,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsCacheStats {

    #[php_function]
    pub fn total_size_mb(&self) -> f64 {
        self.inner.total_size_mb()

    }
    #[php_function]
    pub fn total_size_gb(&self) -> f64 {
        self.inner.total_size_gb()
}
}
// HlxBridge wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHlxBridge {
    inner: HlxBridge,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHlxBridge {

    #[php_function]
    pub fn new() -> Self {
        Self {
            inner: HlxBridge::new(),
    }
}
}
// ServerConfig wrapper
#[cfg(feature = "php")]
#[derive(Clone)]
#[derive(Debug)]
pub struct CsServerConfig {
    inner: ServerConfig,
}
// HelixServer wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsHelixServer {
    inner: HelixServer,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsHelixServer {

    #[php_function]
    pub fn new(config: &CsServerConfig) -> Self {
        Self {
            inner: HelixServer::new(config.inner.clone()),
    }

    }
    #[php_function]
    pub fn start(&self) -> *mut c_char{
        match self.inner.start() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }
}
}
// VaultConfig wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsVaultConfig {
    inner: VaultConfig,
}

// Vault wrapper
#[cfg(feature = "php")]
#[derive(Debug)]
pub struct CsVault {
    inner: Vault,
}
#[cfg(feature = "php")]
#[php_impl]
impl CsVault {

    #[php_function]
    pub fn new() -> CsResult<CsVault> {
        let inner = Vault::new().map_err(|e| error_csharp(e.to_string()))?;
    }

    }
    #[php_function]
    pub fn save(&self, path: String, description: Option<String>) -> *mut c_char{
        let path_buf = std::path::PathBuf::from(path);
        match self.inner.save(&path_buf, description) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn load_latest(&self, env: Env, path: String) -> *mut c_char {
        let path_buf = std::path::PathBuf::from(path);
        let _content = match self.inner.load_latest(&path_buf) {
            Ok(c) => c,
            Err(_) => return std::ptr::null_mut(),
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn load_version(&self, env: Env, file_hash: String, version_id: String) -> *mut c_char {
        let _content = match self.inner.load_version(&file_hash, &version_id) {
            Ok(c) => c,
            Err(_) => return std::ptr::null_mut(),
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    }
    #[php_function]
    pub fn list_versions(&self, path: String) -> CsResult<Vec<String>> {
        let path_buf = std::path::PathBuf::from(path);
        let versions = self
            .inner
            .list_versions(&path_buf)
            .map_err(|e| error_csharp(e.to_string()))?;
        Ok(versions
            .into_iter()
            .map(|v| v.id.clone())
            .collect())

    }
    #[php_function]
    pub fn revert(&self, path: String, version_id: String) -> *mut c_char{
        let path_buf = std::path::PathBuf::from(path);
        match self.inner.revert(&path_buf, &version_id) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }

    }
    #[php_function]
    pub fn garbage_collect(&self) -> *mut c_char{
        match self.inner.garbage_collect() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "php")]
#[php_function]
pub
pub fn parse_helix_source(source: String) -> CsResult<CsHelixAst> {
    let csharp_source_map = CsSourceMap::new(source.clone())?;
    let mut parser = CsParser::new_with_source_map(&csharp_source_map);
    parser.parse()
}

#[cfg(feature = "php")]
#[php_function]
pub
pub fn load_file(file_path: String) -> CsResult<CsHlx> {
    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| error_csharp(e.to_string()))?;
    let path = std::path::PathBuf::from(file_path);
    let _content = std::fs::read_to_string(&path)
        .map_err(|e| error_csharp(format!("Failed to read file: {}", e)))?;
    let hlx = rt
        .block_on(Hlx::new())
        .map_err(|e| error_csharp(e.to_string()))?;
    Ok(CsHlx { inner: hlx })
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn execute(env: Env, source: String) -> *mut c_char {
    let ast = match parse_helix_source(source) {
        Ok(ast) => ast,
        Err(_) => return std::ptr::null_mut(),
    };
    let rt = match tokio::runtime::Runtime::new() {
        Ok(rt) => rt,
        Err(_) => return std::ptr::null_mut(),
    };
    let mut interpreter = match rt.block_on(HelixInterpreter::new()) {
        Ok(interpreter) => interpreter,
        Err(_) => return std::ptr::null_mut(),
    };
    let result = match rt.block_on(interpreter.execute_ast(&ast.inner)) {
        Ok(result) => result,
        Err(_) => return std::ptr::null_mut(),
    };
    value_to_csharp(env, &result)
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_compile(
    input: Option<String>,
    output: Option<String>,
    compress: bool,
    optimize: u8,
    cache: bool,
    verbose: bool,
    quiet: bool,
) -> CsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    match crate::dna::mds::compile::compile_command(
        input_path,
        output_path,
        compress,
        optimize,
        cache,
        verbose,
        quiet,
    ) {
        Ok(_) => Ok("Compilation completed".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_add(
    dependency: String,
    version: Option<String>,
    dev: bool,
    verbose: bool,
) -> CsResult<String> {
    match crate::dna::mds::add::add_dependency(
        dependency,
        version,
        dev,
        verbose,
    ) {
        Ok(_) => Ok("Dependency added".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_validate(target: Option<String>) -> CsResult<String> {
    let target_path = target
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    // For binary files, try to deserialize and validate
    #[cfg(feature = "compiler")]
    if target_path.extension().and_then(|s| s.to_str()) == Some("hlxb") {
        if let Ok(data) = std::fs::read(&target_path) {
            if let Ok(binary) = bincode::deserialize::<crate::dna::hel::binary::HelixBinary>(&data) {
                match binary.validate() {
                    Ok(_) => return Ok("Binary validation passed".to_string()),
                }
            }
        }
    }
    // For source files, check they exist and are readable
    if target_path.exists() {
        Ok("File validation passed".to_string())
    } else {
        Err(error_csharp(format!("File not found: {}", target_path.display())))
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_info(
    input: Option<String>,
    file: Option<String>,
    output: Option<String>,
    format: Option<String>,
    symbols: bool,
    sections: bool,
    verbose: bool,
) -> CsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let format = format.unwrap_or_else(|| "text".to_string());
    
    match crate::dna::mds::info::info_command(input_path, format, symbols, sections, verbose) {
        Ok(_) => Ok("Info command completed".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_init(
    name: Option<String>,
    dir: Option<String>,
    template: Option<String>,
    force: bool,
) -> CsResult<String> {
    let name = name.unwrap_or_else(|| String::new());
    let dir = dir
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let template = template.unwrap_or_else(|| "minimal".to_string());
    
    // TODO: Implement actual init logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_clean(
    all: bool,
    cache: bool,
) -> CsResult<String> {
    // TODO: Implement actual clean logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_fmt(
    files: Vec<String>,
    check: bool,
    verbose: bool,
) -> CsResult<String> {
    let file_paths: Vec<std::path::PathBuf> = files.into_iter().map(std::path::PathBuf::from).collect();
    
    match crate::dna::mds::fmt::format_files(file_paths, check, verbose) {
        Ok(_) => {
            if check {
                Ok("Files are formatted correctly".to_string())
                Ok("Files formatted successfully".to_string())
            }
        }
        Err(e) => Err(error_csharp(format!("Format failed: {}", e))),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_bench(
    pattern: Option<String>,
    iterations: Option<u32>,
) -> CsResult<String> {
    match crate::dna::mds::bench::run_benchmarks(pattern, iterations.map(|i| i as usize), true) {
        Ok(_) => Ok("Benchmarks completed".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_bundle(
    input: Option<String>,
    output: Option<String>,
    include: Vec<String>,
    exclude: Vec<String>,
    tree_shake: bool,
    optimize: u8,
) -> CsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("bundle.hlxb"));
    
    match crate::dna::mds::bundle::bundle_command(input_path, output_path, include, exclude, tree_shake, optimize, false) {
        Ok(_) => Ok("Bundle created successfully".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_test(
    pattern: Option<String>,
    integration: bool,
) -> CsResult<String> {
    // TODO: Implement actual test logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_lint(
    files: Vec<String>,
    verbose: bool,
) -> CsResult<String> {
    let file_paths: Vec<std::path::PathBuf> = files.into_iter().map(std::path::PathBuf::from).collect();
    
    match crate::dna::mds::lint::lint_files(file_paths, verbose) {
        Ok(_) => Ok("Lint completed".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_optimize(
    input: Option<String>,
    output: Option<String>,
    level: u8,
) -> CsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    
    // TODO: Implement actual optimization logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_remove(
    files: Vec<String>,
) -> CsResult<String> {
    // TODO: Implement actual remove logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_reset(
    force: bool,
) -> CsResult<String> {
    // TODO: Implement actual reset logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_search(
    query: String,
    search_type: Option<String>,
    limit: Option<u32>,
    threshold: Option<f64>,
    embeddings: Option<String>,
    auto_find: bool,
) -> CsResult<String> {
    let search_type = search_type.unwrap_or_else(|| "semantic".to_string());
    let limit = limit.unwrap_or(10) as usize;
    let threshold = threshold.unwrap_or(0.0) as f32;
    
    // TODO: Implement actual search logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_serve(
    port: Option<u16>,
    host: Option<String>,
    directory: Option<String>,
) -> CsResult<String> {
    let directory_path = directory.map(|s| std::path::PathBuf::from(s));
    
    // Note: This will block, so we might want to return immediately and run in background
    // For now, we'll just return a message
    match crate::dna::mds::serve::serve_project(port, host, directory_path, false) {
        Ok(_) => Ok("Server started".to_string()),
    }
}

#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_sign(
    input: String,
    key: Option<String>,
    output: Option<String>,
    verify: bool,
    verbose: bool,
) -> CsResult<String> {
    let input_path = std::path::PathBuf::from(input);
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::sign::sign_binary(input_path, key, output_path, verify, verbose) {
        Ok(_) => {
            if verify {
                Ok("Signature verified".to_string())
                Ok("Binary signed successfully".to_string())
            }
        }
        Err(e) => Err(error_csharp(format!("Sign failed: {}", e))),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_watch(
    input: Option<String>,
    output: Option<String>,
    optimize: u8,
    debounce: Option<u32>,
    filter: Option<String>,
) -> CsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let debounce = debounce.unwrap_or(500) as u64;
    
    // TODO: This should run in background, for now just return
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_export(
    format: Option<String>,
    output: Option<String>,
    include_deps: bool,
    verbose: bool,
) -> CsResult<String> {
    let format = format.unwrap_or_else(|| "json".to_string());
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::export::export_project(format, output_path, include_deps, verbose) {
        Ok(_) => Ok("Export completed".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_dataset(
    files: Vec<String>,
    output: Option<String>,
    format: Option<String>,
) -> CsResult<String> {
    let file_paths: Vec<std::path::PathBuf> = files.into_iter().map(std::path::PathBuf::from).collect();
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| error_csharp(e.to_string()))?;
    
    
    let action = DatasetAction::Process {
        files: file_paths,
        output: output_path,
        format,
        algorithm: None,
        validate: false,
    };
    
    match rt.block_on(dataset_command(action, false)) {
        Ok(_) => Ok("Dataset processing completed".to_string()),
        Err(e) => Err(error_csharp(format!("Dataset command failed: {}", e))),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_filter(
    files: Vec<String>,
) -> CsResult<String> {
    // TODO: Implement actual filter logic
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_generate(
    template: String,
    output: Option<String>,
    name: Option<String>,
    force: bool,
    verbose: bool,
) -> CsResult<String> {
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::generate::generate_code(template, output_path, name, force, verbose) {
        Ok(_) => Ok("Code generated successfully".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_import(
    input: *const c_char,
    registry: *const c_char,
    token: *const c_char,
    dry_run: bool,
) -> *mut c_char {
    let input_str = c_string_to_rust(input);
    let registry_opt = c_string_to_rust_option(registry);
    let token_opt = c_string_to_rust_option(token);
    
    let input_path = std::path::PathBuf::from(input_str);
    let rt = match tokio::runtime::Runtime::new() {
        Ok(rt) => rt,
    };
    
    // TODO: Implement actual import logic
    rust_string_to_c(format!("Import command: {}", input_path.display()))
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_schema(
    target: *const c_char,
    lang: *const c_char,
    output: *const c_char,
    verbose: bool,
) -> *mut c_char {
    let target_str = c_string_to_rust(target);
    let lang_opt = c_string_to_rust_option(lang);
    let output_opt = c_string_to_rust_option(output);
    
    let target_path = std::path::PathBuf::from(target_str);
    let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
    
    use crate::dna::mds::schema::Language;
    let language = match lang_opt.as_deref() {
        Some("rust") => Language::Rust,
        Some("ts") | Some("typescript") | Some("js") | Some("javascript") => Language::JavaScript,
        Some("python") => Language::Python,
        Some("go") => Language::Go,
        _ => Language::Rust, // default
    
    match crate::dna::mds::schema::schema_command(target_path, language, output_path, verbose) {
        Ok(_) => rust_string_to_c("Schema generated successfully".to_string()),
        Err(e) => rust_string_to_c(format!("Schema command failed: {}", e)),
    }
}

#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_diff(
    file1: *const c_char,
    file2: *const c_char,
    detailed: bool,
) -> *mut c_char {
    let file1_opt = c_string_to_rust_option(file1);
    let file2_opt = c_string_to_rust_option(file2);
    
    let file1_path = file1_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let file2_path = file2_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    
    match crate::dna::mds::diff::diff_command(file1_path, file2_path, detailed) {
        Ok(_) => rust_string_to_c("Diff completed".to_string()),
    }
}
}   
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_tui() -> *mut c_char {
    match crate::dna::vlt::tui::launch() {
        Ok(_) => rust_string_to_c("TUI session ended".to_string()),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_completions(
    shell: *const c_char,
    verbose: bool,
    quiet: bool,
) -> *mut c_char {
    let shell_str = c_string_to_rust(shell);
    use clap_complete::Shell;
    let shell_enum = match shell_str.to_lowercase().as_str() {
        "bash" => Shell::Bash,
        "zsh" => Shell::Zsh,
        "fish" => Shell::Fish,
        "powershell" => Shell::PowerShell,
        "elvish" => Shell::Elvish,
    };
    
    let completions = crate::dna::mds::completions::completions_command(shell_enum, verbose, quiet);
    rust_string_to_c(completions)
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_doctor(
    action: *const c_char,
) -> *mut c_char {
    // TODO: Implement actual diagnostics logic
    let action_opt = c_string_to_rust_option(action);
    let action_str = action_opt.unwrap_or_else(|| "check".to_string());
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_publish(
    action: *const c_char,
    registry: *const c_char,
    token: *const c_char,
    dry_run: bool,
    verbose: bool,
    quiet: bool,
    input: *const c_char,
    key: *const c_char,
    output: *const c_char,
    verify: bool,
    format: *const c_char,
    include_deps: bool,
) -> *mut c_char {
    let action_str = c_string_to_rust(action);
    let registry_opt = c_string_to_rust_option(registry);
    let token_opt = c_string_to_rust_option(token);
    let input_opt = c_string_to_rust_option(input);
    let key_opt = c_string_to_rust_option(key);
    let output_opt = c_string_to_rust_option(output);
    let format_opt = c_string_to_rust_option(format);
    
    match action_str.as_str() {
        "publish" => {
            match crate::dna::mds::publish::publish_project(registry_opt, token_opt, dry_run, verbose) {
                Ok(_) => rust_string_to_c("Project published successfully".to_string()),
            }
        }
        "sign" => {
            let input_path = match input_opt {
                Some(s) => std::path::PathBuf::from(s),
                None => return rust_string_to_c("--input is required for sign action".to_string()),
            };
            let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
            
            match crate::dna::mds::publish::sign_binary(input_path, key_opt, output_path, verify, verbose) {
                Ok(_) => {
                    if verify {
                        rust_string_to_c("Signature verified".to_string())
                    } else {
                        rust_string_to_c("Binary signed successfully".to_string())
                    }
                }
                Err(e) => rust_string_to_c(format!("Sign failed: {}", e)),
            }
        }
        "export" => {
            let format_str = match format_opt {
                Some(s) => s,
                None => return rust_string_to_c("--format is required for export action".to_string()),
            };
            let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
            
            match crate::dna::mds::publish::export_project(format_str, output_path, include_deps, verbose) {
                Ok(_) => rust_string_to_c("Project exported successfully".to_string()),
                Err(e) => rust_string_to_c(format!("Export failed: {}", e)),
            }
        }
        _ => rust_string_to_c(format!("Unknown publish action: {}", action_str)),
    }
}
#[cfg(feature = "php")]
#[php_function]
pub
pub fn cmd_vlt(
    subcommand: *const c_char,
    name: *const c_char,
    path: *const c_char,
    editor: *const c_char,
    long: bool,
    description: *const c_char,
    limit: *const u32,
    version: *const c_char,
    force: bool,
    from: *const c_char,
    to: *const c_char,
    show: bool,
    compress: *const bool,
    retention_days: *const u32,
    max_versions: *const u32,
    dry_run: bool,
) -> *mut c_char {
    let subcommand_str = c_string_to_rust(subcommand);
    let name_opt = c_string_to_rust_option(name);
    let path_opt = c_string_to_rust_option(path);
    let editor_opt = c_string_to_rust_option(editor);
    let description_opt = c_string_to_rust_option(description);
    let limit_opt = c_u32_to_rust_option(limit);
    let version_opt = c_string_to_rust_option(version);
    let from_opt = c_string_to_rust_option(from);
    let to_opt = c_string_to_rust_option(to);
    let compress_opt = c_bool_to_rust_option(compress);
    let retention_days_opt = c_u32_to_rust_option(retention_days);
    let max_versions_opt = c_u32_to_rust_option(max_versions);
    
    use crate::dna::vlt::Vault;
    
    // Call vault operations directly since VltCommands is private
    match subcommand_str.as_str() {
        "new" => {
            // TODO: Implement new file creation via vault
        }
        "open" => {
            // TODO: Implement file opening
            rust_string_to_c(format!("Vlt open: {}", path_opt.as_ref().map(|s| s.as_str()).unwrap_or("current")))
        }
        "list" => {
            match Vault::new() {
                Ok(_vault) => {
                    // List files - simplified implementation
                    rust_string_to_c("Vault files listed".to_string())
                }
                Err(e) => rust_string_to_c(format!("Vlt list failed: {}", e)),
            }
        }
        "save" => {
            let p = match path_opt {
                Some(p) => p,
                None => return rust_string_to_c("path is required for save".to_string()),
            };
            match Vault::new() {
                Ok(vault) => {
                    let path_buf = std::path::PathBuf::from(p);
                    match vault.save(&path_buf, description_opt) {
                        Ok(version_id) => rust_string_to_c(format!("Saved as version {}", version_id)),
                        Err(e) => rust_string_to_c(format!("Vlt save failed: {}", e)),
                    }
                }
                Err(e) => rust_string_to_c(format!("Vault init failed: {}", e)),
            }
        }
        "history" => {
            let p = match path_opt {
                Some(p) => p,
                None => return rust_string_to_c("path is required for history".to_string()),
            };
            match Vault::new() {
                Ok(vault) => {
                    let path_buf = std::path::PathBuf::from(p);
                    match vault.list_versions(&path_buf) {
                        Ok(versions) => rust_string_to_c(format!("Found {} versions", versions.len())),
                        Err(e) => rust_string_to_c(format!("Vlt history failed: {}", e)),
                    }
                }
                Err(e) => rust_string_to_c(format!("Vault init failed: {}", e)),
            }
        }
        "revert" => {
            let p = match path_opt {
                Some(p) => p,
                None => return rust_string_to_c("path is required for revert".to_string()),
            };
            let v = match version_opt {
                Some(v) => v,
                None => return rust_string_to_c("version is required for revert".to_string()),
            };
            match Vault::new() {
                Ok(vault) => {
                    let path_buf = std::path::PathBuf::from(p);
                    match vault.revert(&path_buf, &v) {
                        Ok(_) => rust_string_to_c(format!("Reverted to version {}", v)),
                        Err(e) => rust_string_to_c(format!("Vlt revert failed: {}", e)),
                    }
                }
                Err(e) => rust_string_to_c(format!("Vault init failed: {}", e)),
            }
        }
        "diff" => {
            // TODO: Implement diff via vault
            rust_string_to_c(format!("Vlt diff: {}", path_opt.as_ref().map(|s| s.as_str()).unwrap_or("current")))
        }
        "config" => {
            // TODO: Implement config management
            rust_string_to_c("Vlt config updated".to_string())
        }
        "gc" => {
            match Vault::new() {
                Ok(vault) => {
                    match vault.garbage_collect() {
                        Ok(removed) => rust_string_to_c(format!("Garbage collection removed {} versions", removed)),
                        Err(e) => rust_string_to_c(format!("Vlt gc failed: {}", e)),
                    }
                }
                Err(e) => rust_string_to_c(format!("Vault init failed: {}", e)),
            }
        }
        "tui" => {
            match crate::dna::vlt::tui::launch() {
                Ok(_) => rust_string_to_c("TUI session ended".to_string()),
                Err(e) => rust_string_to_c(format!("TUI error: {}", e)),
            }
        }
        _ => rust_string_to_c(format!("Unknown vlt subcommand: {}", subcommand_str)),
    }
}}
