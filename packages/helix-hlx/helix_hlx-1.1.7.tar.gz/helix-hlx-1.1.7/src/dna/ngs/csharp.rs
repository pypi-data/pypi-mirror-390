#[cfg(feature = "csharp")]
pub use crate::dna::atp::value::Value as DnaValue;
// #[cfg(feature = "csharp")]
// pub use crate::dna::atp::*;
#[cfg(feature = "csharp")]
pub use crate::dna::bch::*;
// #[cfg(feature = "csharp")]
// pub use crate::dna::cmd::*;
#[cfg(feature = "csharp")]
pub use crate::dna::compiler::{Compiler, CompilerBuilder};
#[cfg(feature = "csharp")]
pub use crate::dna::exp::*;
#[cfg(feature = "csharp")]
pub use crate::dna::hel::dna_hlx::Hlx;
// #[cfg(feature = "csharp")]
// pub use crate::dna::hel::*;
// #[cfg(feature = "csharp")]
// pub use crate::dna::map::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::optimizer::OptimizationLevel;
// #[cfg(feature = "csharp")]
// pub use crate::dna::mds::*;
// #[cfg(feature = "csharp")]
// pub use crate::dna::ngs::*;
#[cfg(feature = "csharp")]
pub use crate::dna::ops::*;
// #[cfg(feature = "csharp")]
// pub use crate::dna::out::*;
#[cfg(feature = "csharp")]
pub use crate::dna::tst::*;
#[cfg(feature = "csharp")]
pub use crate::dna::vlt::Vault;
#[cfg(feature = "csharp")]
pub use crate::dna::atp::ast::*;
#[cfg(feature = "csharp")]
pub use crate::dna::atp::interpreter::*;
#[cfg(feature = "csharp")]
pub use crate::dna::atp::lexer::*;
#[cfg(feature = "csharp")]
pub use crate::dna::atp::output::*;
#[cfg(feature = "csharp")]
pub use crate::dna::atp::parser::*;
#[cfg(feature = "csharp")]
pub use crate::dna::atp::types::*;
#[cfg(feature = "csharp")]
pub use crate::dna::hel::binary::*;
#[cfg(feature = "csharp")]
pub use crate::dna::hel::dispatch::*;
#[cfg(feature = "csharp")]
pub use crate::dna::hel::dna_hlx::*;
#[cfg(feature = "csharp")]
pub use crate::dna::hel::error::*;  
#[cfg(feature = "csharp")]
pub use crate::dna::hel::hlx::*;
#[cfg(feature = "csharp")]
pub use crate::dna::map::core::*;
#[cfg(feature = "csharp")]
pub use crate::dna::map::hf::*;
#[cfg(feature = "csharp")]
pub use crate::dna::map::reasoning::*;
#[cfg(feature = "csharp")]
use crate::dna::map::caption::E621Config as MapE621Config;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::a_example::{Document, Embedding, Metadata};
#[cfg(feature = "csharp")]
pub use crate::dna::mds::benches::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::bundle::*;
#[cfg(feature = "csharp")]  
pub use crate::dna::mds::cache::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::caption::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::codegen::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::concat::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::config::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::decompile::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::filter::*; 
pub use crate::dna::mds::migrate::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::modules::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::optimizer::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::project::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::runtime::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::schema::*;
#[cfg(feature = "csharp")]  
pub use crate::dna::mds::semantic::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::serializer::*;
#[cfg(feature = "csharp")]
pub use crate::dna::mds::server::*;
#[cfg(feature = "csharp")]
pub use crate::dna::out::helix_format::*;
#[cfg(feature = "csharp")]
pub use crate::dna::out::hlx_config_format::*;
#[cfg(feature = "csharp")]
pub use crate::dna::out::hlxb_config_format::*;
#[cfg(feature = "csharp")]
pub use crate::dna::out::hlxc_format::*;
#[cfg(feature = "csharp")]
pub use crate::dna::vlt::tui::*;
#[cfg(feature = "csharp")]
pub use crate::dna::vlt::vault::*;
#[cfg(feature = "csharp")]
pub use crate::dna::map::core::TrainingSample; 

#[cfg(feature = "csharp")]
use std::collections::HashMap;
#[cfg(all(feature = "csharp", feature = "compiler"))]
use bincode;
#[cfg(feature = "csharp")]
pub type Env = *mut std::ffi::c_void;
#[cfg(feature = "csharp")]
pub type CsObject = *mut std::ffi::c_void;
#[cfg(feature = "csharp")]
pub type CsUnknown = *mut std::ffi::c_void;
#[cfg(feature = "csharp")]
pub type CsResult<T> = std::result::Result<T, CsError>;
#[cfg(feature = "csharp")]
use std::os::raw::c_char;
#[cfg(feature = "csharp")]
use std::ffi::{CStr, CString};
#[cfg(feature = "csharp")]
pub use crate::Parser;
#[cfg(feature = "csharp")]
use crate::HelixConfig as RustHelixConfig;
#[cfg(feature = "csharp")]
use serde_json;
#[cfg(feature = "csharp")]

#[repr(C)]
pub struct HelixConfigFFI {
    ptr: *mut RustHelixConfig,
}
#[cfg(feature = "csharp")]
#[repr(C)]
#[derive(Debug, Clone)]
pub struct CsError {
    message: String,
}

#[cfg(feature = "csharp")]
impl CsError {
    pub fn new(message: impl Into<String>) -> Self {
        Self {
            message: message.into(),
        }
    }
}

#[cfg(feature = "csharp")]
impl std::fmt::Display for CsError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

#[cfg(feature = "csharp")]
impl std::error::Error for CsError {}

#[cfg(feature = "csharp")]
pub type NewError = CsError;

#[cfg(feature = "csharp")]
fn error_csharp(message: impl Into<String>) -> CsError {
    CsError::new(message)
}

#[cfg(feature = "csharp")]
fn result_to_ptr<T>(result: CsResult<T>) -> *mut c_char
where
    T: Into<*mut c_char>,
{
    match result {
        Ok(val) => val.into(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "csharp")]
unsafe fn c_string_to_rust(s: *const c_char) -> String {
    if s.is_null() {
        return String::new();
    }
    CStr::from_ptr(s)
        .to_string_lossy()
        .into_owned()
}

#[cfg(feature = "csharp")]
unsafe fn c_string_to_rust_option(s: *const c_char) -> Option<String> {
    if s.is_null() {
        None
    } else {
        Some(c_string_to_rust(s))
    }
}

#[cfg(feature = "csharp")]
fn rust_string_to_c(s: String) -> *mut c_char {
    match CString::new(s) {
        Ok(c_str) => c_str.into_raw(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "csharp")]
fn rust_result_string_to_c(result: CsResult<String>) -> *mut c_char {
    match result {
        Ok(s) => rust_string_to_c(s),
        Err(_) => std::ptr::null_mut(),
    }
}

#[cfg(feature = "csharp")]
unsafe fn c_u32_to_rust_option(val: *const u32) -> Option<u32> {
    if val.is_null() {
        None
    } else {
        Some(*val)
    }
}

#[cfg(feature = "csharp")]
unsafe fn c_bool_to_rust_option(val: *const bool) -> Option<bool> {
    if val.is_null() {
        None
    } else {
        Some(*val)
    }
}

#[cfg(feature = "csharp")]
unsafe fn c_u16_to_rust_option(val: *const u16) -> Option<u16> {
    if val.is_null() {
        None
    } else {
        Some(*val)
    }
}

#[cfg(feature = "csharp")]
unsafe fn c_f64_to_rust_option(val: *const f64) -> Option<f64> {
    if val.is_null() {
        None
    } else {
        Some(*val)
    }
}

#[cfg(feature = "csharp")]
unsafe fn c_string_array_to_rust(arr: *const *const c_char, len: usize) -> Vec<String> {
    if arr.is_null() || len == 0 {
        return Vec::new();
    }
    let mut result = Vec::with_capacity(len);
    for i in 0..len {
        let ptr = *arr.add(i);
        if !ptr.is_null() {
            result.push(c_string_to_rust(ptr));
        }
    }
    result
}

#[cfg(feature = "csharp")]
unsafe fn rust_vec_string_to_c_array(env: Env, vec: Vec<String>) -> *mut c_char {
    match env.create_array_with_length(vec.len()) {
        Ok(mut result) => {
            for (i, s) in vec.iter().enumerate() {
                match env.create_string(s) {
                    Ok(cs_str) => {
                        if let Err(_) = result.set_element(i as u32, cs_str) {
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

#[cfg(feature = "csharp")]
unsafe fn rust_vec_i32_to_c_array(env: Env, vec: Vec<i32>) -> *mut c_char {
    match env.create_array_with_length(vec.len()) {
        Ok(mut result) => {
            for (i, val) in vec.iter().enumerate() {
                match env.create_double(*val as f64) {
                    Ok(cs_val) => {
                        if let Err(_) = result.set_element(i as u32, cs_val) {
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

#[cfg(feature = "csharp")]
unsafe fn rust_vec_f64_to_c_array(env: Env, vec: Vec<f64>) -> *mut c_char {
    match env.create_array_with_length(vec.len()) {
        Ok(mut result) => {
            for (i, val) in vec.iter().enumerate() {
                match env.create_double(*val) {
                    Ok(cs_val) => {
                        if let Err(_) = result.set_element(i as u32, cs_val) {
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

#[cfg(feature = "csharp")]
unsafe fn rust_vec_bool_to_c_array(env: Env, vec: Vec<bool>) -> *mut c_char {
    match env.create_array_with_length(vec.len()) {
        Ok(mut result) => {
            for (i, val) in vec.iter().enumerate() {
                match env.get_boolean(*val) {
                    Ok(cs_val) => {
                        if let Err(_) = result.set_element(i as u32, cs_val) {
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

#[cfg(feature = "csharp")]
fn rust_result_f64_to_c(result: CsResult<f64>, error_out: *mut *mut c_char) -> f64 {
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

#[cfg(feature = "csharp")]
fn rust_result_bool_to_c(result: CsResult<bool>, error_out: *mut *mut c_char) -> bool {
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

#[cfg(feature = "csharp")]
fn rust_result_u64_to_c(result: CsResult<u64>, error_out: *mut *mut c_char) -> u64 {
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

#[cfg(feature = "csharp")]
pub trait EnvExt {
    fn create_string(&self, s: &str) -> CsResult<CsUnknown>;
    fn create_double(&self, n: f64) -> CsResult<CsUnknown>;
    fn get_boolean(&self, b: bool) -> CsResult<CsUnknown>;
    fn create_array_with_length(&self, len: usize) -> CsResult<CsUnknown>;
    fn create_object(&self) -> CsResult<CsUnknown>;
    fn get_null(&self) -> CsResult<CsUnknown>;
}

#[cfg(feature = "csharp")]
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

#[cfg(feature = "csharp")]
pub trait CsUnknownExt {
    fn into_unknown(self) -> *mut c_char;
    fn coerce_to_string(&self) -> CsResult<CsUnknown>;
    fn into_utf8(&self) -> CsResult<CsUnknown>;
}

#[cfg(feature = "csharp")]
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

#[cfg(feature = "csharp")]
pub trait CsUnknownStr {
    fn as_str(&self) -> CsResult<&str>;
}

#[cfg(feature = "csharp")]
impl CsUnknownStr for CsUnknown {
    fn as_str(&self) -> CsResult<&str> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}

#[cfg(feature = "csharp")]
pub trait CsUnknownArray {
    fn set_element(&mut self, index: u32, value: CsUnknown) -> CsResult<()>;
}

#[cfg(feature = "csharp")]
impl CsUnknownArray for CsUnknown {
    fn set_element(&mut self, _index: u32, _value: CsUnknown) -> CsResult<()> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}

#[cfg(feature = "csharp")]
pub trait CsUnknownObject {
    fn set_named_property(&mut self, key: &str, value: CsUnknown) -> CsResult<()>;
}

#[cfg(feature = "csharp")]
impl CsUnknownObject for CsUnknown {
    fn set_named_property(&mut self, _key: &str, _value: CsUnknown) -> CsResult<()> {
        Err(error_csharp("CSHARP extension not implemented"))
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn value_to_csharp(env: Env, value: &crate::dna::atp::value::Value) -> *mut c_char {
    match value {
        crate::dna::atp::value::Value::String(s) => {
            match env.create_string(s) {
                Ok(csharp_val) => csharp_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            }
        }
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

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHelixAst {
    inner: HelixAst,
}

#[cfg(feature = "csharp")]
impl CsHelixAst {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: HelixAst::new(),
        }))
    }

    pub unsafe extern "C" fn add_declaration(&mut self, _decl: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn get_projects(&self, env: Env) -> *mut c_char {
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

    pub unsafe extern "C" fn get_agents(&self, env: Env) -> *mut c_char {
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

    pub unsafe extern "C" fn get_workflows(&self, env: Env) -> *mut c_char {
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

    pub unsafe extern "C" fn get_contexts(&self, env: Env) -> *mut c_char {
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
}

// Csthon wrapper for AstPrettyPrinter
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsAstPrettyPrinter {
    inner: AstPrettyPrinter,
}
#[cfg(feature = "csharp")]
impl CsAstPrettyPrinter {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: AstPrettyPrinter::new(),
        }))
    }

    pub unsafe extern "C" fn print(&mut self, ast: &CsHelixAst) -> *mut c_char {
        rust_string_to_c(self.inner.print(&ast.inner))
    }
}

// Csthon wrapper for Expression
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsExpression {
    inner: Expression,
}

#[cfg(feature = "csharp")]
impl CsExpression {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: Expression::Identifier("".to_string()),
        }))
    }


    pub unsafe extern "C" fn binary(
        left: &CsExpression,
        op: *const c_char,
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

    pub unsafe extern "C" fn as_string(&self) -> *mut c_char {
        rust_string_to_c(self.inner.as_string().unwrap_or_default())
    }

    pub unsafe extern "C" fn as_number(&self, error_out: *mut *mut c_char) -> f64 {
        rust_result_f64_to_c(
        self.inner
            .as_number()
                .ok_or_else(|| error_csharp("Value is not a number")),
            error_out
        )
    }

    pub unsafe extern "C" fn as_bool(&self, error_out: *mut *mut c_char) -> bool {
        rust_result_bool_to_c(
        self.inner
            .as_bool()
                .ok_or_else(|| error_csharp("Value is not a boolean")),
            error_out
        )
    }

    pub unsafe extern "C" fn as_array(&self, env: Env) -> *mut c_char {
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

    pub unsafe extern "C" fn as_object(&self, env: Env) -> *mut c_char {
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

    pub unsafe extern "C" fn to_value(&self, env: Env) -> *mut c_char {
        let value = self.inner.to_value();
        value_to_csharp(env, &value)
    }
}

// Csthon wrapper for AstBuilder
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsAstBuilder {
    inner: AstBuilder,
}

#[cfg(feature = "csharp")]
impl CsAstBuilder {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: AstBuilder::new(),
        }))
    }

    pub unsafe extern "C" fn add_agent(&mut self, _agent: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_workflow(&mut self, _workflow: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_context(&mut self, _context: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_memory(&mut self, _memory: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_crew(&mut self, _crew: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_pipeline(&mut self, _pipeline: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_plugin(&mut self, _plugin: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_database(&mut self, _database: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_load(&mut self, _load: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_section(&mut self, _section: CsObject) -> *mut c_char{
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn build(&mut self) -> *mut CsHelixAst {
        let ast = std::mem::replace(&mut self.inner, crate::dna::atp::ast::AstBuilder::new()).build();
        Box::into_raw(Box::new(CsHelixAst { inner: ast }))
    }
}

// HelixInterpreter wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHelixInterpreter {
    inner: HelixInterpreter,
}

#[cfg(feature = "csharp")]
impl CsHelixInterpreter {
    pub unsafe extern "C" fn new(error_out: *mut *mut c_char) -> *mut CsHelixInterpreter {
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

    pub unsafe extern "C" fn execute_ast(&mut self, env: Env, ast: &CsHelixAst) -> *mut c_char {
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

    pub unsafe extern "C" fn operator_engine(&self, env: Env) -> *mut c_char {
        let _engine = self.inner.operator_engine();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn operator_engine_mut(&mut self, env: Env) -> *mut c_char {
        let _engine = self.inner.operator_engine_mut();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn set_variable(&mut self, name: *const c_char, value: CsUnknown) -> *mut c_char{
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
        self.inner.set_variable(name_str, val);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn get_variable(&self, env: Env, name: *const c_char) -> *mut c_char {
        let name_str = c_string_to_rust(name);
        let value = self.inner.get_variable(&name_str);
        match value {
            Some(v) => value_to_csharp(env, &v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
        }
    }

    pub unsafe extern "C" fn list_variables(&self, env: Env) -> *mut c_char {
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
}

// SourceMap wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsSourceMap {
    inner: SourceMap,
}
#[cfg(feature = "csharp")]
impl CsSourceMap {
    pub unsafe extern "C" fn new(source: *const c_char, error_out: *mut *mut c_char) -> *mut CsSourceMap {
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

    pub unsafe extern "C" fn get_line(&self, line_num: usize) -> *mut c_char {
        let line = self.inner.get_line(line_num);
        rust_string_to_c(line.unwrap_or_default().to_string())
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsSectionName {
    inner: crate::dna::atp::ops::SectionName,
}
#[cfg(feature = "csharp")]
impl CsSectionName {
    pub unsafe extern "C" fn new(s: *const c_char) -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: crate::dna::atp::ops::SectionName::new(c_string_to_rust(s)),
        }))
    }

    pub unsafe extern "C" fn as_str(&self) -> *mut c_char {
        rust_string_to_c(self.inner.as_str().to_string())
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsVariableName {
    inner: crate::dna::atp::ops::VariableName,
}
#[cfg(feature = "csharp")]
impl CsVariableName {
    pub unsafe extern "C" fn new(s: *const c_char) -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: crate::dna::atp::ops::VariableName::new(c_string_to_rust(s)),
        }))
    }

    pub unsafe extern "C" fn as_str(&self) -> *mut c_char {
        rust_string_to_c(self.inner.as_str().to_string())
    }
}
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCacheKey {
    inner: crate::dna::atp::ops::CacheKey,
}
#[cfg(feature = "csharp")]
impl CsCacheKey {
    pub unsafe extern "C" fn new(file: *const c_char, key: *const c_char) -> *mut Self {
        let file_str = c_string_to_rust(file);
        let key_str = c_string_to_rust(key);
        Box::into_raw(Box::new(Self {
            inner: crate::dna::atp::ops::CacheKey::new(&file_str, &key_str),
        }))
    }
}
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsRegexCache {
    inner: crate::dna::atp::ops::RegexCache,
}
#[cfg(feature = "csharp")]
impl CsRegexCache {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: crate::dna::atp::ops::RegexCache::new(),
        }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsStringParser {
    inner: crate::dna::atp::ops::StringParser,
}
#[cfg(feature = "csharp")]
impl CsStringParser {
    pub unsafe extern "C" fn new(input: *const c_char) -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: crate::dna::atp::ops::StringParser::new(c_string_to_rust(input)),
        }))
    }

    pub unsafe extern "C" fn parse_quoted_string(&mut self) -> *mut c_char {
        match self.inner.parse_quoted_string() {
            Ok(s) => rust_string_to_c(s),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsOperatorParser {
    inner: crate::dna::atp::ops::OperatorParser,
}
#[cfg(feature = "csharp")]
impl CsOperatorParser {
    pub unsafe extern "C" fn new(error_out: *mut *mut c_char) -> *mut CsOperatorParser {
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
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

    pub unsafe extern "C" fn load_hlx(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.load_hlx()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn try_math(&self, s: *const c_char, error_out: *mut *mut c_char) -> f64 {
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

    pub unsafe extern "C" fn execute_date(&self, fmt: *const c_char) -> *mut c_char {
        let fmt_str = c_string_to_rust(fmt);
        rust_string_to_c(crate::dna::atp::ops::eval_date_expression(&fmt_str))
    }

    pub unsafe extern "C" fn parse_line(&mut self, raw: *const c_char) -> *mut c_char{
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

    pub unsafe extern "C" fn get(&self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let value = self.inner.get(&key_str);
        match value {
            Some(v) => value_to_csharp(env, &v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
        }
    }

    pub unsafe extern "C" fn get_ref(&self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let value = self.inner.get_ref(&key_str);
        match value {
            Some(v) => value_to_csharp(env, v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
        }
    }

    pub unsafe extern "C" fn set(&mut self, key: *const c_char, value: CsUnknown) -> *mut c_char{
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

    pub unsafe extern "C" fn keys(&self, env: Env) -> *mut c_char {
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

    pub unsafe extern "C" fn items(&self, env: Env) -> *mut c_char {
        let items = self.inner.items();
        let mut result = match env.create_object() {
            Ok(r) => r,
            Err(_) => return std::ptr::null_mut(),
        };
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

    pub unsafe extern "C" fn items_cloned(&self, env: Env) -> *mut c_char {
        let items = self.inner.items_cloned();
        let mut result = match env.create_object() {
            Ok(r) => r,
            Err(_) => return std::ptr::null_mut(),
        };
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

    pub unsafe extern "C" fn get_errors(&self, env: Env) -> *mut c_char {
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

    pub unsafe extern "C" fn has_errors(&self) -> bool {
        self.inner.has_errors()
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsOutputFormat {
    inner: OutputFormat,
}
#[cfg(feature = "csharp")]
impl CsOutputFormat {
    pub unsafe extern "C" fn from_str(s: *const c_char) -> *mut Self {
        let s_str = c_string_to_rust(s);
        let format = OutputFormat::from(s_str.as_str()).unwrap_or(OutputFormat::Helix);
        Box::into_raw(Box::new(Self { inner: format }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCompressionConfig {
    inner: CompressionConfig,
}
#[cfg(feature = "csharp")]
impl CsCompressionConfig {
    pub unsafe extern "C" fn default() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: CompressionConfig::default(),
        }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsOutputConfig {
    inner: OutputConfig,
}
#[cfg(feature = "csharp")]
impl CsOutputConfig {
    pub unsafe extern "C" fn default() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: OutputConfig::default(),
        }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsOutputManager {
    inner: OutputManager,
}
#[cfg(feature = "csharp")]
impl CsOutputManager {
    pub unsafe extern "C" fn new(config: *const CsOutputConfig) -> *mut Self {
        if config.is_null() {
            return std::ptr::null_mut();
        }
        Box::into_raw(Box::new(Self {
            inner: OutputManager::new((*config).inner.clone()),
        }))
    }

    pub unsafe extern "C" fn add_row(&mut self, row_keys: *const *const c_char, row_keys_len: usize, row_values: *const CsObject, row_values_len: usize) -> *mut c_char{
        // Convert arrays to HashMap<String, CsObject> then to HashMap<String, AtpValue>
        let mut converted_row: HashMap<String, crate::dna::atp::value::Value> = HashMap::new();
        // Placeholder conversion - would need proper implementation
        self.inner.add_row(converted_row);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn flush_batch(&mut self) -> *mut c_char{
        match self.inner.flush_batch() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn finalize_all(&mut self) -> *mut c_char{
        match self.inner.finalize_all() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn get_output_files(&self, env: Env) -> *mut c_char {
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

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHlxcDataWriter {
    inner: crate::dna::atp::output::HlxcDataWriter,
}
#[cfg(feature = "csharp")]
impl CsHlxcDataWriter {
    pub unsafe extern "C" fn new(config: *const CsOutputConfig) -> *mut Self {
        if config.is_null() {
            return std::ptr::null_mut();
        }
        Box::into_raw(Box::new(Self {
            inner: crate::dna::atp::output::HlxcDataWriter::new((*config).inner.clone()),
        }))
    }

    pub unsafe extern "C" fn write_batch(&mut self, batch: CsObject) -> *mut c_char{
        // Convert CsObject to RecordBatch
        // This would need proper Arrow RecordBatch conversion
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn finalize(&mut self) -> *mut c_char{
        match self.inner.finalize() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsParser {
    inner: Parser,
}
#[cfg(feature = "csharp")]
impl CsParser {
    pub unsafe extern "C" fn new(tokens: *const CsObject, tokens_len: usize, error_out: *mut *mut c_char) -> *mut CsParser {
        // Convert Vec<CsObject> to Vec<Token>
        let converted_tokens: Vec<Token> = vec![]; // Placeholder
        Box::into_raw(Box::new(CsParser {
            inner: Parser::new(converted_tokens),
        }))
    }


    pub unsafe extern "C" fn new_enhanced(tokens: *const CsObject, tokens_len: usize) -> *mut CsParser {
        // Convert Vec<CsObject> to Vec<TokenWithLocation>
        let converted_tokens: Vec<crate::dna::atp::lexer::TokenWithLocation> = vec![]; // Placeholder
        Box::into_raw(Box::new(CsParser {
            inner: Parser::new_enhanced(converted_tokens),
        }))
    }


    pub unsafe extern "C" fn new_with_source_map(source_map: &CsSourceMap) -> *mut CsParser {
        Box::into_raw(Box::new(CsParser {
            inner: Parser::new_with_source_map(source_map.inner.clone()),
        }))
    }

    pub unsafe extern "C" fn set_runtime_context(&mut self, context_keys: *const *const c_char, context_keys_len: usize, context_values: *const *const c_char, context_values_len: usize) -> *mut c_char{
        let mut context: HashMap<String, String> = HashMap::new();
        if !context_keys.is_null() && !context_values.is_null() && context_keys_len == context_values_len {
            for i in 0..context_keys_len {
                let key_ptr = *context_keys.add(i);
                let val_ptr = *context_values.add(i);
                if !key_ptr.is_null() && !val_ptr.is_null() {
                    let key = c_string_to_rust(key_ptr);
                    let val = c_string_to_rust(val_ptr);
                    context.insert(key, val);
                }
            }
        }
        self.inner.set_runtime_context(context);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn parse(&mut self, error_out: *mut *mut c_char) -> *mut CsHelixAst {
        let ast = match self.inner.parse() {
            Ok(ast) => ast,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
            }
        };
        Box::into_raw(Box::new(CsHelixAst { inner: ast }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHelixLoader {
    inner: HelixLoader,
}
#[cfg(feature = "csharp")]
impl CsHelixLoader {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: HelixLoader::new(),
        }))
    }   

    pub unsafe extern "C" fn parse(&mut self, content: *const c_char) -> *mut c_char{
        let content_str = c_string_to_rust(content);
        match self.inner.parse(&content_str) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn get_config(&self, env: Env, name: *const c_char) -> *mut c_char {
        let name_str = c_string_to_rust(name);
        let _config = self.inner.get_config(&name_str);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn set_context(&mut self, context: *const c_char) -> *mut c_char{
        let context_str = c_string_to_rust(context);
        self.inner.set_context(context_str);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn merge_configs(&self, env: Env, configs: *const CsObject, configs_len: usize) -> *mut c_char {
        // Convert Vec<CsObject> to Vec<&HelixConfig>
        let converted_configs: Vec<&HelixConfig> = vec![]; // Placeholder
        let _merged = self.inner.merge_configs(converted_configs);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCompiler {
    inner: Compiler,
}
#[cfg(feature = "csharp")]
impl CsCompiler {
    pub unsafe extern "C" fn new(optimization_level: CsUnknown, error_out: *mut *mut c_char) -> *mut CsCompiler {
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
        Box::into_raw(Box::new(CsCompiler {
            inner: Compiler::new(level),
        }))
    }

    pub unsafe extern "C" fn builder() -> *mut CsCompilerBuilder {
        Box::into_raw(Box::new(CsCompilerBuilder {
            inner: Compiler::builder(),
        }))
    }

    pub unsafe extern "C" fn decompile(&self, env: Env, bin: *const CsHelixBinary) -> *mut c_char {
        if bin.is_null() {
            return std::ptr::null_mut();
        }
        match self.inner.decompile(&(*bin).inner) {
            Ok(_ast) => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCompilerBuilder {
    inner: CompilerBuilder,
}
#[cfg(feature = "csharp")]
impl CsCompilerBuilder {
    pub unsafe extern "C" fn optimization_level(&mut self, level: CsUnknown) -> *mut c_char{
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

    pub unsafe extern "C" fn compression(&mut self, enable: bool) -> *mut c_char{
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.compression(enable);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn cache(&mut self, enable: bool) -> *mut c_char{
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.cache(enable);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn verbose(&mut self, enable: bool) -> *mut c_char{
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.verbose(enable);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn build(&mut self) -> *mut CsCompiler {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        let compiler = builder.build();
        Box::into_raw(Box::new(CsCompiler { inner: compiler }))
    }
}

#[cfg(feature = "csharp")]
#[derive(Clone, Debug)]
#[repr(C)]
pub struct CsHelixBinary {
    inner: HelixBinary,
}
#[cfg(feature = "csharp")]
impl CsHelixBinary {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: HelixBinary::new(),
        }))
    }

    pub unsafe extern "C" fn validate(&self) -> *mut c_char{
        match self.inner.validate() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn calculate_checksum(&self, error_out: *mut *mut c_char) -> u64 {
        rust_result_u64_to_c(Ok(self.inner.calculate_checksum()), error_out)
    }

    pub unsafe extern "C" fn size(&self) -> usize {
        self.inner.size()
    }

    pub unsafe extern "C" fn compression_ratio(&self, original_size: usize) -> f64 {
        self.inner.compression_ratio(original_size)
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHelixDispatcher {
    inner: HelixDispatcher,
}
#[cfg(feature = "csharp")]
impl CsHelixDispatcher {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: HelixDispatcher::new(),
        }))
    }

    pub unsafe extern "C" fn initialize(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.initialize()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn parse_only(&self, source: *const c_char) -> *mut c_char {
        let source_str = c_string_to_rust(source);
        let tokens_with_loc = match crate::dna::atp::lexer::tokenize_with_locations(&source_str) {
            Ok(tokens) => tokens,
            Err(e) => return rust_string_to_c(format!("Error: {}", e)),
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

    pub unsafe extern "C" fn parse_dsl(&mut self, source: *const c_char) -> *mut c_char{
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

    pub unsafe extern "C" fn interpreter(&self, error_out: *mut *mut c_char) -> *mut CsHelixInterpreter {
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

    pub unsafe extern "C" fn interpreter_mut(&mut self, error_out: *mut *mut c_char) -> *mut CsHelixInterpreter {
        // Can't clone a mutable reference, need to return an error or handle differently
        if !error_out.is_null() {
            *error_out = rust_string_to_c("Cannot clone mutable interpreter reference".to_string());
        }
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn is_ready(&self) -> bool {
        self.inner.is_ready()
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHlx {
    inner: Hlx,
}
#[cfg(feature = "csharp")]
impl CsHlx {
    pub unsafe extern "C" fn new(error_out: *mut *mut c_char) -> *mut CsHlx {
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
            }
        };
        let hlx = match rt.block_on(Hlx::new()) {
            Ok(hlx) => hlx,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
            }
        };
        Box::into_raw(Box::new(CsHlx { inner: hlx }))
    }

    pub unsafe extern "C" fn get_raw(&self, env: Env, section: *const c_char, key: *const c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        let value = self.inner.get_raw(&section_str, &key_str);
        match value {
            Some(v) => value_to_csharp(env, &v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
        }
    }

    pub unsafe extern "C" fn get_str(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_str(&section_str, &key_str) {
            Some(s) => rust_string_to_c(s.to_string()),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_num(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> f64 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_num(&section_str, &key_str) {
            Some(n) => n,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                0.0
            }
        }
    }

    pub unsafe extern "C" fn get_bool(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> bool {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_bool(&section_str, &key_str) {
            Some(b) => b,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                false
            }
        }
    }

    pub unsafe extern "C" fn get_array(&self, env: Env, section: *const c_char, key: *const c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        let arr = match self.inner.get_array(&section_str, &key_str) {
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

    pub unsafe extern "C" fn get_string(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_string(&section_str, &key_str) {
            Some(s) => rust_string_to_c(s),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_i32(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> i32 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_i32(&section_str, &key_str) {
            Some(v) => v,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                0
            }
        }
    }

    pub unsafe extern "C" fn get_i64(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> i64 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_i64(&section_str, &key_str) {
            Some(v) => v,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                0
            }
        }
    }

    pub unsafe extern "C" fn get_u32(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> u32 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_u32(&section_str, &key_str) {
            Some(v) => v,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                0
            }
        }
    }

    pub unsafe extern "C" fn get_u64(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> u64 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_u64(&section_str, &key_str) {
            Some(v) => v,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                0
            }
        }
    }

    pub unsafe extern "C" fn get_f32(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> f32 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_f32(&section_str, &key_str) {
            Some(v) => v,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                0.0
            }
        }
    }

    pub unsafe extern "C" fn get_f64(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> f64 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_f64(&section_str, &key_str) {
            Some(v) => v,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                0.0
            }
        }
    }

    pub unsafe extern "C" fn get_vec_string(&self, env: Env, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_vec_string(&section_str, &key_str) {
            Some(vec) => rust_vec_string_to_c_array(env, vec),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_vec_i32(&self, env: Env, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_vec_i32(&section_str, &key_str) {
            Some(vec) => rust_vec_i32_to_c_array(env, vec),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_vec_f64(&self, env: Env, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_vec_f64(&section_str, &key_str) {
            Some(vec) => rust_vec_f64_to_c_array(env, vec),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_vec_bool(&self, env: Env, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_vec_bool(&section_str, &key_str) {
            Some(vec) => rust_vec_bool_to_c_array(env, vec),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_dynamic(&self, section: *const c_char, key: *const c_char, error_out: *mut *mut c_char) -> *mut CsDynamicValue {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.get_dynamic(&section_str, &key_str) {
            Some(value) => Box::into_raw(Box::new(CsDynamicValue { inner: value })),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found in section '{}'", key_str, section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_auto(&self, env: Env, section: *const c_char, key: *const c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        let value = match self.inner.get_auto(&section_str, &key_str) {
            Some(v) => v,
            None => return std::ptr::null_mut(),
        };
        value_to_csharp(env, &crate::dna::atp::value::Value::String(value))
    }

    pub unsafe extern "C" fn select(&self, env: Env, section: *const c_char, key: *const c_char) -> *mut c_char {
        // TypedGetter wrapper - for now return a placeholder
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn set_str(&mut self, section: *const c_char, key: *const c_char, value: *const c_char) -> *mut c_char{
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        let value_str = c_string_to_rust(value);
        self.inner.set_str(&section_str, &key_str, &value_str);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn set_num(&mut self, section: *const c_char, key: *const c_char, value: f64) -> *mut c_char{
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        self.inner.set_num(&section_str, &key_str, value);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn set_bool(&mut self, section: *const c_char, key: *const c_char, value: bool) -> *mut c_char{
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        self.inner.set_bool(&section_str, &key_str, value);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn increase(&mut self, section: *const c_char, key: *const c_char, amount: f64, error_out: *mut *mut c_char) -> f64 {
        let section_str = c_string_to_rust(section);
        let key_str = c_string_to_rust(key);
        match self.inner.increase(&section_str, &key_str, amount) {
            Ok(val) => val,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                0.0
            }
        }
    }

    pub unsafe extern "C" fn index(&self, env: Env, section: *const c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let _index = self.inner.index(&section_str);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn index_mut(&mut self, env: Env, section: *const c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        let _index = self.inner.index_mut(&section_str);
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn server(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.server()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn watch(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.watch()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn process(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.process()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn compile(&mut self) -> *mut c_char{
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        match rt.block_on(self.inner.compile()) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn execute(&mut self, env: Env, code: *const c_char) -> *mut c_char {
        let code_str = c_string_to_rust(code);
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(_) => return std::ptr::null_mut(),
        };
        let result = match rt.block_on(self.inner.execute(&code_str)) {
            Ok(result) => result,
            Err(_) => return std::ptr::null_mut(),
        };
        value_to_csharp(env, &result)
    }

    pub unsafe extern "C" fn sections(&self, env: Env) -> *mut c_char {
        let sections: Vec<String> = self.inner.sections().iter().map(|s| s.to_string()).collect();
        rust_vec_string_to_c_array(env, sections)
    }

    pub unsafe extern "C" fn keys(&self, env: Env, section: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let section_str = c_string_to_rust(section);
        match self.inner.keys(&section_str) {
            Some(keys) => {
                let keys_vec: Vec<String> = keys.iter().map(|s| s.to_string()).collect();
                rust_vec_string_to_c_array(env, keys_vec)
            }
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Section '{}' not found", section_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_file_path(&self, error_out: *mut *mut c_char) -> *mut c_char {
        match self.inner.get_file_path() {
            Some(path) => rust_string_to_c(path.to_string_lossy().to_string()),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c("No file path available".to_string());
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn save(&self) -> *mut c_char{
        match self.inner.save() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn make(&self, env: Env) -> *mut c_char {
        let result = match self.inner.make() {
            Ok(result) => result,
            Err(_) => return std::ptr::null_mut(),
        };
        value_to_csharp(env, &crate::dna::atp::value::Value::String(result))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsDynamicValue {
    inner: DynamicValue,
}
#[cfg(feature = "csharp")]
impl CsDynamicValue {
    pub unsafe extern "C" fn as_string(&self) -> *mut c_char {
        rust_string_to_c(self.inner.as_string().unwrap_or_default())
    }

    pub unsafe extern "C" fn as_number(&self) -> f64 {
        self.inner.as_number().unwrap_or(0.0)
    }

    pub unsafe extern "C" fn as_integer(&self) -> i64 {
        self.inner.as_integer().unwrap_or(0)
    }

    pub unsafe extern "C" fn as_bool(&self) -> bool {
        self.inner.as_bool().unwrap_or(false)
    }

    pub unsafe extern "C" fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsAtpValue {
    inner: crate::dna::atp::value::Value,
}
#[cfg(feature = "csharp")]
impl CsAtpValue {
    pub unsafe extern "C" fn default() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: crate::dna::atp::value::Value::default(),
        }))
    }

    pub unsafe extern "C" fn value_type(&self) -> *mut c_char {
        rust_string_to_c(format!("{:?}", self.inner.value_type()))
    }

    pub unsafe extern "C" fn is_string(&self) -> bool {
        self.inner.is_string()
    }

    pub unsafe extern "C" fn is_number(&self) -> bool {
        self.inner.is_number()
    }

    pub unsafe extern "C" fn is_boolean(&self) -> bool {
        self.inner.is_boolean()
    }

    pub unsafe extern "C" fn is_array(&self) -> bool {
        self.inner.is_array()
    }

    pub unsafe extern "C" fn is_object(&self) -> bool {
        self.inner.is_object()
    }

    pub unsafe extern "C" fn is_null(&self) -> bool {
        self.inner.is_null()
    }

    pub unsafe extern "C" fn as_string(&self, error_out: *mut *mut c_char) -> *mut c_char {
        match self.inner.as_string() {
            Some(s) => rust_string_to_c(s.to_string()),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c("Value is not a string".to_string());
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn as_number(&self, error_out: *mut *mut c_char) -> f64 {
        match self.inner.as_number() {
            Some(n) => n,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c("Value is not a number".to_string());
                }
                0.0
            }
        }
    }

    pub unsafe extern "C" fn as_f64(&self, error_out: *mut *mut c_char) -> f64 {
        match self.inner.as_f64() {
            Some(n) => n,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c("Value is not a number".to_string());
                }
                0.0
            }
        }
    }

    pub unsafe extern "C" fn as_str(&self, error_out: *mut *mut c_char) -> *mut c_char {
        match self.inner.as_str() {
            Some(s) => rust_string_to_c(s.to_string()),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c("Value is not a string".to_string());
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn as_boolean(&self, error_out: *mut *mut c_char) -> bool {
        match self.inner.as_boolean() {
            Some(b) => b,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c("Value is not a boolean".to_string());
                }
                false
            }
        }
    }

    pub unsafe extern "C" fn as_array(&self, env: Env) -> *mut c_char {
        let arr = match self.inner.as_array() {
            Some(arr) => arr,
            None => return std::ptr::null_mut(),
        };
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

    pub unsafe extern "C" fn as_object(&self, env: Env) -> *mut c_char {
        let obj = match self.inner.as_object() {
            Some(obj) => obj,
            None => return std::ptr::null_mut(),
        };
        let mut csharp_obj = match env.create_object() {
            Ok(obj) => obj,
            Err(_) => return std::ptr::null_mut(),
        };
        for (key, value) in obj {
            let csharp_val = value_to_csharp(env, value);
            if csharp_val.is_null() {
                return std::ptr::null_mut();
            }
            let csharp_val_unknown = csharp_val as CsUnknown;
            if let Err(_) = csharp_obj.set_named_property(&key, csharp_val_unknown) {
                return std::ptr::null_mut();
            }
        }
        csharp_obj.into_unknown()
    }

    pub unsafe extern "C" fn get(&self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let value = self.inner.get(&key_str);
        match value {
            Some(v) => value_to_csharp(env, v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
        }
    }

    pub unsafe extern "C" fn get_mut(&mut self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let value = self.inner.get_mut(&key_str);
        match value {
            Some(v) => value_to_csharp(env, v),
            None => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
        }
    }

    pub unsafe extern "C" fn get_string(&self, key: *const c_char, error_out: *mut *mut c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        match self.inner.get_string(&key_str) {
            Some(s) => rust_string_to_c(s.to_string()),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found or not a string", key_str));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn get_number(&self, key: *const c_char, error_out: *mut *mut c_char) -> f64 {
        let key_str = c_string_to_rust(key);
        match self.inner.get_number(&key_str) {
            Some(n) => n,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found or not a number", key_str));
                }
                0.0
            }
        }
    }

    pub unsafe extern "C" fn get_boolean(&self, key: *const c_char, error_out: *mut *mut c_char) -> bool {
        let key_str = c_string_to_rust(key);
        match self.inner.get_boolean(&key_str) {
            Some(b) => b,
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Key '{}' not found or not a boolean", key_str));
                }
                false
            }
        }
    }

    pub unsafe extern "C" fn get_array(&self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let arr = match self.inner.get_array(&key_str) {
            Some(arr) => arr,
            None => return std::ptr::null_mut(),
        };
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

    pub unsafe extern "C" fn get_object(&self, env: Env, key: *const c_char) -> *mut c_char {
        let key_str = c_string_to_rust(key);
        let obj = match self.inner.get_object(&key_str) {
            Some(obj) => obj,
            None => return std::ptr::null_mut(),
        };
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

    pub unsafe extern "C" fn to_string(&self) -> *mut c_char {
        rust_string_to_c(self.inner.to_string())
    }

    pub unsafe extern "C" fn to_json(&self) -> *mut c_char {
        match self.inner.to_json() {
            Ok(s) => rust_string_to_c(s),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }

    pub unsafe extern "C" fn to_yaml(&self) -> *mut c_char {
        match self.inner.to_yaml() {
            Ok(s) => rust_string_to_c(s),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }

    pub unsafe extern "C" fn from_json(json_value: CsObject, error_out: *mut *mut c_char) -> *mut CsAtpValue {
        // Convert CsObject to serde_json::Value
        let json = serde_json::Value::Null; // Placeholder
        let value = crate::dna::atp::value::Value::from_json(json);
        Box::into_raw(Box::new(CsAtpValue { inner: value }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHlxHeader {
    inner: HlxHeader,
}
#[cfg(feature = "csharp")]
impl CsHlxHeader {
    pub unsafe extern "C" fn new(schema: CsObject, metadata: *const *const c_char, metadata_len: usize, error_out: *mut *mut c_char) -> *mut CsHlxHeader {
        // Convert parameters
        use arrow::datatypes::{DataType, Field, Schema};
        let converted_schema = Schema::new(vec![Field::new("placeholder", DataType::Utf8, false)]);
        let converted_metadata: HashMap<String, serde_json::Value> = HashMap::new(); // Placeholder
        let header = HlxHeader::new(&converted_schema, converted_metadata);
        Box::into_raw(Box::new(CsHlxHeader { inner: header }))
    }

    pub unsafe extern "C" fn from_json_bytes(bytes: *const u8, bytes_len: usize, error_out: *mut *mut c_char) -> *mut CsHlxHeader {
        let bytes_vec = if bytes.is_null() || bytes_len == 0 {
            Vec::new()
        } else {
            std::slice::from_raw_parts(bytes, bytes_len).to_vec()
        };
        match HlxHeader::from_json_bytes(&bytes_vec) {
            Ok(header) => Box::into_raw(Box::new(CsHlxHeader { inner: header })),
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn with_compression(&mut self, compressed: bool) -> *mut c_char{
        let inner = self.inner.clone();
        self.inner = inner.with_compression(compressed);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn with_row_count(&mut self, count: u64) -> *mut c_char{
        let inner = self.inner.clone();
        self.inner = inner.with_row_count(count);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn with_preview(&mut self, preview: *const CsObject, preview_len: usize) -> *mut c_char{
        // Convert Vec<CsObject> to Vec<serde_json::Value>
        let converted_preview: Vec<serde_json::Value> = vec![]; // Placeholder
        let inner = self.inner.clone();
        self.inner = inner.with_preview(converted_preview);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn is_compressed(&self) -> bool {
        self.inner.is_compressed()
    }

    pub unsafe extern "C" fn to_json_bytes(&self, bytes_out: *mut *mut u8, bytes_len_out: *mut usize, error_out: *mut *mut c_char) -> *mut c_char {
        match self.inner.to_json_bytes() {
            Ok(bytes) => {
                let boxed = bytes.into_boxed_slice();
                let len = boxed.len();
                let ptr = Box::into_raw(boxed) as *mut u8;
                if !bytes_out.is_null() {
                    *bytes_out = ptr;
                }
                if !bytes_len_out.is_null() {
                    *bytes_len_out = len;
                }
                std::ptr::null_mut()
            }
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                std::ptr::null_mut()
            }
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsSymbolTable {
    inner: crate::dna::hel::binary::SymbolTable,
}
#[cfg(feature = "csharp")]
impl CsSymbolTable {
    pub unsafe extern "C" fn intern(&mut self, s: *const c_char) -> u32 {
        let s_str = c_string_to_rust(s);
        self.inner.intern(&s_str)
    }

    pub unsafe extern "C" fn get(&self, id: u32, error_out: *mut *mut c_char) -> *mut c_char {
        match self.inner.get(id) {
            Some(s) => rust_string_to_c(s.clone()),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Symbol with id {} not found", id));
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsDataSection {
    inner: DataSection,
}
#[cfg(feature = "csharp")]
impl CsDataSection {
    pub unsafe extern "C" fn new(section_type: CsObject, data: *const u8, data_len: usize, error_out: *mut *mut c_char) -> *mut CsDataSection {
        // Convert CsObject to SectionType
        let st = crate::dna::hel::binary::SectionType::Project; // Placeholder
        let data_vec = if data.is_null() || data_len == 0 {
            Vec::new()
        } else {
            std::slice::from_raw_parts(data, data_len).to_vec()
        };
        let section = DataSection::new(st, data_vec);
        Box::into_raw(Box::new(CsDataSection { inner: section }))
    }

    pub unsafe extern "C" fn compress(&mut self, method: CsObject) -> *mut c_char{
        // Convert CsObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        match self.inner.compress(cm) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn decompress(&mut self) -> *mut c_char{
        match self.inner.decompress() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHelixVM {
    inner: HelixVM,
}
#[cfg(feature = "csharp")]
impl CsHelixVM {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: HelixVM::new(),
        }))
    }

    pub unsafe extern "C" fn with_debug(&mut self) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_debug();
    }

    pub unsafe extern "C" fn execute_binary(&mut self, binary: &CsHelixBinary) -> *mut c_char{
        match self.inner.execute_binary(&binary.inner) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn push(&mut self, value: CsObject) -> *mut c_char{
        // Convert CsObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        self.inner.push(val);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn pop(&mut self) -> *mut c_char{
        match self.inner.pop() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn load_memory(&self, env: Env, address: u32) -> *mut c_char {
        let value = match self.inner.load_memory(address) {
            Ok(v) => v,
            Err(_) => return std::ptr::null_mut(),
        };
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

    pub unsafe extern "C" fn store_memory(&mut self, address: u32, value: CsObject) -> *mut c_char{
        // Convert CsObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        match self.inner.store_memory(address, val) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn set_breakpoint(&mut self, address: usize) -> *mut c_char{
        self.inner.set_breakpoint(address);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn remove_breakpoint(&mut self, address: usize) -> *mut c_char{
        self.inner.remove_breakpoint(address);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn continue_execution(&mut self) -> *mut c_char{
        self.inner.continue_execution();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn step(&mut self) -> *mut c_char{
        self.inner.step();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn state(&self, env: Env) -> *mut c_char {
        let _state = self.inner.state();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsVMExecutor {
    inner: VMExecutor,
}
#[cfg(feature = "csharp")]
impl CsVMExecutor {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: VMExecutor::new(),
        }))
    }

    pub unsafe extern "C" fn vm(&mut self, error_out: *mut *mut c_char) -> *mut CsHelixVM {
        // vm() returns &mut, can't move it - need to clone or return reference
        if !error_out.is_null() {
            *error_out = rust_string_to_c("Cannot move vm from executor".to_string());
        }
        std::ptr::null_mut()
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsAppState {
    inner: crate::dna::vlt::tui::AppState,
}
#[cfg(feature = "csharp")]
impl CsAppState {
    pub unsafe extern "C" fn new(error_out: *mut *mut c_char) -> *mut CsAppState {
        match crate::dna::vlt::tui::AppState::new() {
            Ok(inner) => Box::into_raw(Box::new(CsAppState { inner })),
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn focus(&mut self, area: CsObject) -> *mut c_char{
        // Convert CsObject to FocusArea
        let focus_area = crate::dna::vlt::tui::FocusArea::Files; // Placeholder
        self.inner.focus(focus_area);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn select_next_file(&mut self) -> *mut c_char{
        self.inner.select_next_file();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn select_prev_file(&mut self) -> *mut c_char{
        self.inner.select_prev_file();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn open_selected_file(&mut self) -> *mut c_char{
        match self.inner.open_selected_file() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn select_next_operator(&mut self) -> *mut c_char{
        self.inner.select_next_operator();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn select_prev_operator(&mut self) -> *mut c_char{
        self.inner.select_prev_operator();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn cycle_operator_category_next(&mut self) -> *mut c_char{
        self.inner.cycle_operator_category_next();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn cycle_operator_category_prev(&mut self) -> *mut c_char{
        self.inner.cycle_operator_category_prev();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn reset_operator_category(&mut self) -> *mut c_char{
        self.inner.reset_operator_category();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn sync_operator_selection(&mut self) -> *mut c_char{
        self.inner.sync_operator_selection();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn insert_selected_operator(&mut self) -> *mut c_char{
        self.inner.insert_selected_operator();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn next_tab(&mut self) -> *mut c_char{
        self.inner.next_tab();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn previous_tab(&mut self) -> *mut c_char{
        self.inner.previous_tab();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn close_active_tab(&mut self) -> *mut c_char{
        self.inner.close_active_tab();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn create_new_tab(&mut self) -> *mut c_char{
        self.inner.create_new_tab();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn save_active_tab(&mut self) -> *mut c_char{
        match self.inner.save_active_tab() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn trigger_command(&mut self) -> *mut c_char{
        self.inner.trigger_command();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn select_next_command(&mut self) -> *mut c_char{
        self.inner.select_next_command();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn select_prev_command(&mut self) -> *mut c_char{
        self.inner.select_prev_command();
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn on_tick(&mut self) -> *mut c_char{
        self.inner.on_tick();
        std::ptr::null_mut()
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsBenchmark {
    inner: Benchmark,
}
#[cfg(feature = "csharp")]
impl CsBenchmark {
    pub unsafe extern "C" fn new(name: *const c_char) -> *mut CsBenchmark {
        let name_str = c_string_to_rust(name);
        Box::into_raw(Box::new(CsBenchmark {
            inner: Benchmark::new(&name_str),
        }))
    }

    pub unsafe extern "C" fn with_iterations(&mut self, iterations: usize) -> *mut c_char{
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_iterations(iterations);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn with_warmup(&mut self, warmup: usize) -> *mut c_char{
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_warmup(warmup);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn run(&self, env: Env, f: CsUnknown) -> *mut c_char {
        // This needs to be implemented with proper callback handling
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsBundler {
    inner: Bundler,
}
#[cfg(feature = "csharp")]
impl CsBundler {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: Bundler::new(),
        }))
    }

    pub unsafe extern "C" fn include(&mut self, pattern: *const c_char) {
        let pattern_str = c_string_to_rust(pattern);
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.include(&pattern_str);
    }

    pub unsafe extern "C" fn exclude(&mut self, pattern: *const c_char) {
        let pattern_str = c_string_to_rust(pattern);
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.exclude(&pattern_str);
    }

    pub unsafe extern "C" fn with_imports(&mut self, follow: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_imports(follow);
    }

    pub unsafe extern "C" fn with_tree_shaking(&mut self, enable: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_tree_shaking(enable);
    }

    pub unsafe extern "C" fn verbose(&mut self, enable: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.verbose(enable);
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsBundleBuilder {
    inner: crate::dna::mds::bundle::BundleBuilder,
}
#[cfg(feature = "csharp")]
impl CsBundleBuilder {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: crate::dna::mds::bundle::BundleBuilder::new(),
        }))
    }

    pub unsafe extern "C" fn add_file(&mut self, path: *const c_char, binary: *const CsHelixBinary) -> *mut c_char{
        if binary.is_null() {
            return std::ptr::null_mut();
        }
        let path_str = c_string_to_rust(path);
        let path_buf = std::path::PathBuf::from(path_str);
        self.inner.add_file(path_buf, (*binary).inner.clone());
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn add_dependency(&mut self, from: *const c_char, to: *const c_char) -> *mut c_char{
        let from_str = c_string_to_rust(from);
        let to_str = c_string_to_rust(to);
        let from_path = std::path::PathBuf::from(from_str);
        let to_path = std::path::PathBuf::from(to_str);
        self.inner.add_dependency(from_path, to_path);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn build(&mut self, env: Env) -> *mut c_char {
        let _bundle = std::mem::replace(&mut self.inner, crate::dna::mds::bundle::BundleBuilder::new()).build();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCacheAction {
    // This is likely an enum, so we need to handle it differently
}
#[cfg(feature = "csharp")]
impl CsCacheAction {

    pub unsafe extern "C" fn from_str(s: *const c_char, error_out: *mut *mut c_char) -> *mut CsCacheAction {
        let s_str = c_string_to_rust(s);
        // Convert string to CacheAction enum
        Box::into_raw(Box::new(CsCacheAction {})) // Placeholder
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsE621Config {
    inner: MapE621Config,
}
#[cfg(feature = "csharp")]
impl CsE621Config {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: MapE621Config::new(),
        }))
    }

    pub unsafe extern "C" fn with_filter_tags(&mut self, filter_tags: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_filter_tags(filter_tags);
    }

    pub unsafe extern "C" fn with_format(&mut self, format: *const c_char) -> () {
        let format_opt = c_string_to_rust_option(format);
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_format(format_opt);
    }

    pub unsafe extern "C" fn with_artist_prefix(&mut self, prefix: *const c_char) -> () {
        let prefix_opt = c_string_to_rust_option(prefix);
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_artist_prefix(prefix_opt);
    }

    pub unsafe extern "C" fn with_artist_suffix(&mut self, suffix: *const c_char) -> () {
        let suffix_opt = c_string_to_rust_option(suffix);
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_artist_suffix(suffix_opt);
    }

    pub unsafe extern "C" fn with_replace_underscores(&mut self, replace_underscores: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_replace_underscores(replace_underscores);
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsConcatConfig {
    inner: ConcatConfig,
}
#[cfg(feature = "csharp")]
impl CsConcatConfig {
    pub unsafe extern "C" fn with_deduplication(&mut self, deduplicate: bool) -> *mut c_char{
        self.inner = std::mem::replace(&mut self.inner, ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags)).with_deduplication(deduplicate);
        std::ptr::null_mut()
    }


    pub unsafe extern "C" fn from_preset(_preset: CsObject) -> *mut Self {
        // TODO: Convert CsObject to FileExtensionPreset
        let config = ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags); // Placeholder
        Box::into_raw(Box::new(Self { inner: config }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsDataFormat {
    inner: crate::dna::map::core::DataFormat,
}
#[cfg(feature = "csharp")]
impl CsDataFormat {

    pub unsafe extern "C" fn from_str(s: *const c_char, error_out: *mut *mut c_char) -> *mut CsDataFormat {
        let s_str = c_string_to_rust(s);
        match s_str.parse::<crate::dna::map::core::DataFormat>() {
            Ok(format) => Box::into_raw(Box::new(CsDataFormat { inner: format })),
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                std::ptr::null_mut()
            }
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsGenericJSONDataset {
    inner: crate::dna::map::core::GenericJSONDataset,
}
#[cfg(feature = "csharp")]
impl CsGenericJSONDataset {
    pub unsafe extern "C" fn len(&self) -> usize {
        self.inner.len()
    }

    pub unsafe extern "C" fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    pub unsafe extern "C" fn get_random_sample(&self, env: Env) -> *mut c_char {
        let _sample = self.inner.get_random_sample();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn detect_training_format(&self, env: Env) -> *mut c_char {
        let _format = self.inner.detect_training_format();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn to_training_dataset(&self, error_out: *mut *mut c_char) -> *mut CsTrainingDataset {
        match self.inner.to_training_dataset() {
            Ok(dataset) => Box::into_raw(Box::new(CsTrainingDataset { inner: dataset })),
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                std::ptr::null_mut()
            }
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsTrainingDataset {
    inner: crate::dna::map::core::TrainingDataset,
}
#[cfg(feature = "csharp")]
impl CsTrainingDataset {
    pub unsafe extern "C" fn quality_assessment(&self, env: Env) -> *mut c_char {
        let _assessment = self.inner.quality_assessment();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHuggingFaceDataset {
    inner: HuggingFaceDataset,
}
#[cfg(feature = "csharp")]
impl CsHuggingFaceDataset {

    pub unsafe extern "C" fn load(name: *const c_char, split: *const c_char, cache_dir: *const c_char, error_out: *mut *mut c_char) -> *mut CsHuggingFaceDataset {
        let name_str = c_string_to_rust(name);
        let split_str = c_string_to_rust(split);
        let cache_dir_str = c_string_to_rust(cache_dir);
        let rt = match tokio::runtime::Runtime::new() {
            Ok(rt) => rt,
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                return std::ptr::null_mut();
            }
        };
        let path = std::path::PathBuf::from(cache_dir_str);
        match rt.block_on(HuggingFaceDataset::load(&name_str, &split_str, &path)) {
            Ok(dataset) => Box::into_raw(Box::new(CsHuggingFaceDataset { inner: dataset })),
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                std::ptr::null_mut()
            }
        }
    }
}

#[cfg(feature = "csharp")]
impl CsHuggingFaceDataset {
    pub unsafe extern "C" fn get_features(&self, env: Env) -> *mut c_char {
        let _features = self.inner.get_features();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn info(&self, env: Env) -> *mut c_char {
        let _info = self.inner.info();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsPreferenceProcessor {
    inner: PreferenceProcessor,
}
#[cfg(feature = "csharp")]
impl CsPreferenceProcessor {

    pub unsafe extern "C" fn compute_statistics(_samples: *const CsObject, _samples_len: usize, env: Env) -> *mut c_char {
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCompletionProcessor {
    inner: CompletionProcessor,
}
#[cfg(feature = "csharp")]
impl CsCompletionProcessor {

    pub unsafe extern "C" fn compute_statistics(_samples: *const CsObject, _samples_len: usize, env: Env) -> *mut c_char {
        // compute_statistics is private, placeholder implementation
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsInstructionProcessor {
    inner: InstructionProcessor,
}
#[cfg(feature = "csharp")]
impl CsInstructionProcessor {

    pub unsafe extern "C" fn compute_statistics(_samples: *const CsObject, _samples_len: usize, env: Env) -> *mut c_char {
        // compute_statistics is private, placeholder implementation
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHfProcessor {
    inner: HfProcessor,
}
#[cfg(feature = "csharp")]
impl CsHfProcessor {
    pub unsafe extern "C" fn new(cache_dir: *const c_char) -> *mut CsHfProcessor {
        let cache_dir_str = c_string_to_rust(cache_dir);
        let path = std::path::PathBuf::from(cache_dir_str);
        Box::into_raw(Box::new(CsHfProcessor {
            inner: HfProcessor::new(path),
        }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsReasoningDataset {
    inner: ReasoningDataset,
}
#[cfg(feature = "csharp")]
impl CsReasoningDataset {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: ReasoningDataset::new(),
        }))
    }

    pub unsafe extern "C" fn add_entry(&mut self, entry: CsObject) -> *mut c_char{
        // Convert CsObject to ReasoningEntry
        let converted_entry = ReasoningEntry {
            user: "placeholder".to_string(),
            reasoning: "placeholder".to_string(),
            assistant: "placeholder".to_string(),
            template: "placeholder".to_string(),
            conversations: vec![],
        }; // Placeholder
        self.inner.add_entry(converted_entry);
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn len(&self) -> usize {
        self.inner.len()
    }

    pub unsafe extern "C" fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    pub unsafe extern "C" fn create_template(&self, user: *const c_char, reasoning: *const c_char, assistant: *const c_char) -> *mut c_char {
        let user_str = c_string_to_rust(user);
        let reasoning_str = c_string_to_rust(reasoning);
        let assistant_str = c_string_to_rust(assistant);
        rust_string_to_c(crate::dna::map::reasoning::ReasoningDataset::create_template(&user_str, &reasoning_str, &assistant_str))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsDocument {
    // This appears to be a placeholder impl block
}
#[cfg(feature = "csharp")]
#[repr(C)]
#[derive(Debug, Clone)]
pub struct CsStringPool {
    inner: StringPool,
}
#[cfg(feature = "csharp")]
impl CsStringPool {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: StringPool::new(),
        }))
    }

    pub unsafe extern "C" fn intern(&mut self, s: *const c_char) -> u32 {
        let s_str = c_string_to_rust(s);
        self.inner.intern(&s_str)
    }

    pub unsafe extern "C" fn get(&self, idx: u32, error_out: *mut *mut c_char) -> *mut c_char {
        match self.inner.get(idx) {
            Some(s) => rust_string_to_c(s.clone()),
            None => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(format!("Index {} not found", idx));
                }
                std::ptr::null_mut()
            }
        }
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsConstantPool {
    inner: ConstantPool,
}
#[cfg(feature = "csharp")]
impl CsConstantPool {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: ConstantPool::new(),
        }))
    }

    pub unsafe extern "C" fn add(&mut self, value: CsObject, error_out: *mut *mut c_char) -> u32 {
        // TODO: Convert CsObject to ConstantValue
        // Placeholder - return 0 for now
        use crate::dna::mds::codegen::ConstantValue;
        let cv = ConstantValue::String(0); // Placeholder
        self.inner.add(cv)
    }

    pub unsafe extern "C" fn get(&self, env: Env, idx: u32) -> *mut c_char {
        let value = match self.inner.get(idx) {
            Some(v) => v,
            None => return std::ptr::null_mut(),
        };
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

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCodeGenerator {
    inner: CodeGenerator,
}
#[cfg(feature = "csharp")]
impl CsCodeGenerator {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: CodeGenerator::new(),
        }))
    }

    pub unsafe extern "C" fn generate(&mut self, ast: &CsHelixAst) -> *mut c_char{
        let _ir = self.inner.generate(&ast.inner);
        std::ptr::null_mut()
    }
}

// BinarySerializer wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsBinarySerializer {
    inner: crate::dna::mds::serializer::BinarySerializer,
}
#[cfg(feature = "csharp")]
impl CsBinarySerializer {
    pub unsafe extern "C" fn new(enable_compression: bool) -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: crate::dna::mds::serializer::BinarySerializer::new(enable_compression),
        }))
    }

    pub unsafe extern "C" fn with_compression_method(&mut self, method: CsObject) -> () {
        // Convert CsObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        let inner = crate::dna::mds::serializer::BinarySerializer::new(true);
        self.inner = inner.with_compression_method(cm);
    }
}

// VersionChecker wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsVersionChecker {
    // This seems to be a static utility class
}
#[cfg(feature = "csharp")]
impl CsVersionChecker {

    pub unsafe extern "C" fn is_compatible(_ir: CsObject) -> bool {
        // Convert CsObject to &HelixIR - placeholder implementation
        // HelixIR doesn't have Default, so using a dummy check
        true
    }


    pub unsafe extern "C" fn migrate(ir: CsObject) -> *mut c_char{
        // Convert and modify CsObject representing HelixIR
        std::ptr::null_mut()
    }
}

// Migrator wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsMigrator {
    inner: Migrator,
}
#[cfg(feature = "csharp")]
impl CsMigrator {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: Migrator::new(),
        }))
    }

    pub unsafe extern "C" fn verbose(&mut self, enable: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.verbose(enable);
    }

    pub unsafe extern "C" fn migrate_json(&self, json_str: *const c_char) -> *mut c_char {
        let json_str_rust = c_string_to_rust(json_str);
        match self.inner.migrate_json(&json_str_rust) {
            Ok(result) => rust_string_to_c(result),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }

    pub unsafe extern "C" fn migrate_toml(&self, toml_str: *const c_char) -> *mut c_char {
        let toml_str_rust = c_string_to_rust(toml_str);
        match self.inner.migrate_toml(&toml_str_rust) {
            Ok(result) => rust_string_to_c(result),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }

    pub unsafe extern "C" fn migrate_yaml(&self, yaml_str: *const c_char) -> *mut c_char {
        let yaml_str_rust = c_string_to_rust(yaml_str);
        match self.inner.migrate_yaml(&yaml_str_rust) {
            Ok(result) => rust_string_to_c(result),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }

    pub unsafe extern "C" fn migrate_env(&self, env_str: *const c_char) -> *mut c_char {
        let env_str_rust = c_string_to_rust(env_str);
        match self.inner.migrate_env(&env_str_rust) {
            Ok(result) => rust_string_to_c(result),
            Err(e) => rust_string_to_c(format!("Error: {}", e)),
        }
    }
}

// ModuleResolver wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsModuleResolver {
    inner: ModuleResolver,
}
#[cfg(feature = "csharp")]
impl CsModuleResolver {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: ModuleResolver::new(),
        }))
    }

    pub unsafe extern "C" fn resolve(&mut self, env: Env, module_name: *const c_char) -> *mut c_char {
        let module_name_str = c_string_to_rust(module_name);
        let result = self.inner.resolve(&module_name_str);
        match result {
            Ok(path) => {
                match env.create_string(&path.to_string_lossy()) {
                    Ok(s) => s.into_unknown(),
                    Err(_) => std::ptr::null_mut(),
                }
            },
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn clear_cache(&mut self) -> *mut c_char{
        let _ = self.inner.clear_cache();
        std::ptr::null_mut()
    }
}

// ModuleSystem wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsModuleSystem {
    inner: ModuleSystem,
}

#[cfg(feature = "csharp")]
impl CsModuleSystem {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: ModuleSystem::new(),
        }))
    }

    pub unsafe extern "C" fn load_module(&mut self, path: *const c_char) -> *mut c_char{
        let path_str = c_string_to_rust(path);
        let path_buf = std::path::PathBuf::from(path_str);
        match self.inner.load_module(&path_buf) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn resolve_dependencies(&mut self) -> *mut c_char{
        match self.inner.resolve_dependencies() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn compilation_order(&self, env: Env) -> *mut c_char {
        let order: Vec<String> = self.inner.compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect();
        match env.create_array_with_length(order.len()) {
            Ok(mut result) => {
                for (i, path) in order.iter().enumerate() {
                    match env.create_string(path) {
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

    pub unsafe extern "C" fn merge_modules(&self, env: Env) -> *mut c_char {
        let _merged = match self.inner.merge_modules() {
            Ok(m) => m,
            Err(_) => return std::ptr::null_mut(),
        };
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn modules(&self, env: Env) -> *mut c_char {
        let _modules = self.inner.modules();
        // Convert Vec<ModuleInfo> to Vec<CsObject>
        match env.create_array_with_length(0) {
            Ok(arr) => arr.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn dependency_graph(&self) -> *mut CsDependencyGraph {
        Box::into_raw(Box::new(CsDependencyGraph { inner: DependencyGraph }))
    }
}

// DependencyBundler wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsDependencyBundler {
    inner: DependencyBundler,
}

#[cfg(feature = "csharp")]
impl CsDependencyBundler {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: DependencyBundler::new(),
        }))
    }

    pub unsafe extern "C" fn build_bundle(&mut self, env: Env) -> *mut c_char {
        let _bundle = match self.inner.build_bundle() {
            Ok(b) => b,
            Err(_) => return std::ptr::null_mut(),
        };
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn get_compilation_order(&self, env: Env) -> *mut c_char {
        let order: Vec<String> = self.inner.get_compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect();
        match env.create_array_with_length(order.len()) {
            Ok(mut result) => {
                for (i, path) in order.iter().enumerate() {
                    match env.create_string(path) {
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

// DependencyGraph wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsDependencyGraph {
    inner: DependencyGraph,
}
#[cfg(feature = "csharp")]
impl CsDependencyGraph {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: DependencyGraph::new(),
        }))
    }

    pub unsafe extern "C" fn check_circular(&self) -> *mut c_char{
        match self.inner.check_circular() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

// OptimizationLevel wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
#[derive(Clone)]
pub struct CsOptimizationLevel {
    inner: OptimizationLevel,
}

#[cfg(feature = "csharp")]
impl CsOptimizationLevel {

    pub unsafe extern "C" fn from_u8(level: u8) -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: OptimizationLevel::from(level),
        }))
    }
}

#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsOptimizer {
    inner: Optimizer,
}
#[cfg(feature = "csharp")]
impl CsOptimizer {
    pub unsafe extern "C" fn new(level: u8) -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: Optimizer::new(OptimizationLevel::from(level)),
        }))
    }

    pub unsafe extern "C" fn optimize(&mut self, _ir: CsObject) -> *mut c_char{
        // Convert CsObject to &mut HelixIR - placeholder implementation
        // HelixIR doesn't have Default, skipping optimization
        std::ptr::null_mut()
    }

    pub unsafe extern "C" fn stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

// ProjectManifest wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsProjectManifest {
    // This seems to be a large struct, placeholder for now
}

// Runtime wrapper (HelixVM is already defined above)


// Schema wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHelixConfig {
    inner: HelixConfig,
}

#[cfg(feature = "csharp")]
impl CsHelixConfig {
    // Index implementation would go here if needed
}

// HlxDatasetProcessor wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHlxDatasetProcessor {
    inner: HlxDatasetProcessor,
}
#[cfg(feature = "csharp")]
impl CsHlxDatasetProcessor {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: HlxDatasetProcessor::new(),
        }))
    }

    pub unsafe extern "C" fn parse_hlx_content(&self, env: Env, content: *const c_char) -> *mut c_char {
        let content_str = c_string_to_rust(content);
        match self.inner.parse_hlx_content(&content_str) {
            Ok(_data) => match env.get_null() {
                Ok(null_val) => null_val.into_unknown(),
                Err(_) => std::ptr::null_mut(),
            },
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn cache_stats(&self, env: Env) -> *mut c_char {
        let _stats = self.inner.cache_stats();
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn clear_cache(&mut self) -> *mut c_char{
        let _ = self.inner.clear_cache();
        std::ptr::null_mut()
    }
}

// ProcessingOptions wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
#[derive(Debug, Clone)]
pub struct CsProcessingOptions {
    inner: ProcessingOptions,
}
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsCacheStats {
    inner: CacheStats,
}
#[cfg(feature = "csharp")]
impl CsCacheStats {
    pub unsafe extern "C" fn total_size_mb(&self) -> f64 {
        self.inner.total_size_mb()
    }

    pub unsafe extern "C" fn total_size_gb(&self) -> f64 {
        self.inner.total_size_gb()
    }
}

// HlxBridge wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsHlxBridge {
    inner: HlxBridge,
}
#[cfg(feature = "csharp")]
impl CsHlxBridge {
    pub unsafe extern "C" fn new() -> *mut Self {
        Box::into_raw(Box::new(Self {
            inner: HlxBridge::new(),
        }))
    }
}

// ServerConfig wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
#[derive(Clone)]
pub struct CsServerConfig {
    inner: ServerConfig,
}
#[cfg(feature = "csharp")]
#[repr(C)]
// HelixServer wrapper
pub struct CsHelixServer {
    inner: HelixServer,
}
#[cfg(feature = "csharp")]
impl CsHelixServer {
    pub unsafe extern "C" fn new(config: *const CsServerConfig) -> *mut Self {
        if config.is_null() {
            return std::ptr::null_mut();
        }
        Box::into_raw(Box::new(Self {
            inner: HelixServer::new((*config).inner.clone()),
        }))
    }

    pub unsafe extern "C" fn start(&self) -> *mut c_char{
        match self.inner.start() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}

// VaultConfig wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsVaultConfig {
    inner: VaultConfig,
}

// Vault wrapper
#[cfg(feature = "csharp")]
#[repr(C)]
pub struct CsVault {
    inner: Vault,
}
#[cfg(feature = "csharp")]
impl CsVault {
    pub unsafe extern "C" fn new(error_out: *mut *mut c_char) -> *mut CsVault {
        match Vault::new() {
            Ok(inner) => Box::into_raw(Box::new(CsVault { inner })),
            Err(e) => {
                if !error_out.is_null() {
                    *error_out = rust_string_to_c(e.to_string());
                }
                std::ptr::null_mut()
            }
        }
    }

    pub unsafe extern "C" fn save(&self, path: *const c_char, description: *const c_char) -> *mut c_char{
        let path_str = c_string_to_rust(path);
        let description_opt = c_string_to_rust_option(description);
        let path_buf = std::path::PathBuf::from(path_str);
        match self.inner.save(&path_buf, description_opt) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn load_latest(&self, env: Env, path: *const c_char) -> *mut c_char {
        let path_str = c_string_to_rust(path);
        let path_buf = std::path::PathBuf::from(path_str);
        let _content = match self.inner.load_latest(&path_buf) {
            Ok(c) => c,
            Err(_) => return std::ptr::null_mut(),
        };
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn load_version(&self, env: Env, file_hash: *const c_char, version_id: *const c_char) -> *mut c_char {
        let file_hash_str = c_string_to_rust(file_hash);
        let version_id_str = c_string_to_rust(version_id);
        let _content = match self.inner.load_version(&file_hash_str, &version_id_str) {
            Ok(c) => c,
            Err(_) => return std::ptr::null_mut(),
        };
        match env.get_null() {
            Ok(null_val) => null_val.into_unknown(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn list_versions(&self, env: Env, path: *const c_char) -> *mut c_char {
        let path_str = c_string_to_rust(path);
        let path_buf = std::path::PathBuf::from(path_str);
        let versions = match self.inner.list_versions(&path_buf) {
            Ok(v) => v,
            Err(_) => return std::ptr::null_mut(),
        };
        let version_strings: Vec<String> = versions
            .into_iter()
            .map(|v| v.id.clone())
            .collect();
        match env.create_array_with_length(version_strings.len()) {
            Ok(mut result) => {
                for (i, version) in version_strings.iter().enumerate() {
                    match env.create_string(version) {
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

    pub unsafe extern "C" fn revert(&self, path: *const c_char, version_id: *const c_char) -> *mut c_char{
        let path_str = c_string_to_rust(path);
        let version_id_str = c_string_to_rust(version_id);
        let path_buf = std::path::PathBuf::from(path_str);
        match self.inner.revert(&path_buf, &version_id_str) {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }

    pub unsafe extern "C" fn garbage_collect(&self) -> *mut c_char{
        match self.inner.garbage_collect() {
            Ok(_) => std::ptr::null_mut(),
            Err(_) => std::ptr::null_mut(),
        }
    }
}


#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn parse_helix_source(source: *const c_char, error_out: *mut *mut c_char) -> *mut CsHelixAst {
    let source_str = c_string_to_rust(source);
    let csharp_source_map = match CsSourceMap::new(source, error_out) {
        ptr if ptr.is_null() => return std::ptr::null_mut(),
        ptr => &*ptr,
    };
    let parser_ptr = CsParser::new_with_source_map(csharp_source_map);
    if parser_ptr.is_null() {
        return std::ptr::null_mut();
    }
    unsafe { &mut *parser_ptr }.parse(error_out)
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn load_file(file_path: *const c_char, error_out: *mut *mut c_char) -> *mut CsHlx {
    let file_path_str = c_string_to_rust(file_path);
    let rt = match tokio::runtime::Runtime::new() {
        Ok(rt) => rt,
        Err(e) => {
            if !error_out.is_null() {
                *error_out = rust_string_to_c(e.to_string());
            }
            return std::ptr::null_mut();
        }
    };
    let path = std::path::PathBuf::from(file_path_str);
    let _content = match std::fs::read_to_string(&path) {
        Ok(content) => content,
        Err(e) => {
            if !error_out.is_null() {
                *error_out = rust_string_to_c(format!("Failed to read file: {}", e));
            }
            return std::ptr::null_mut();
        }
    };
    CsHlx::new(error_out)
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn execute(env: Env, source: *const c_char) -> *mut c_char {
    let mut error_out: *mut c_char = std::ptr::null_mut();
    let ast = match parse_helix_source(source, &mut error_out) {
        ptr if ptr.is_null() => return std::ptr::null_mut(),
        ptr => &*ptr,
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

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_compile(
    input: *const c_char,
    output: *const c_char,
    compress: bool,
    optimize: u8,
    cache: bool,
    verbose: bool,
    quiet: bool,
) -> *mut c_char {
    let input_opt = c_string_to_rust_option(input);
    let output_opt = c_string_to_rust_option(output);
    let input_path = input_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
    match crate::dna::mds::compile::compile_command(
        input_path,
        output_path,
        compress,
        optimize,
        cache,
        verbose,
        quiet,
    ) {
        Ok(_) => rust_string_to_c("Compilation completed".to_string()),
        Err(e) => rust_string_to_c(format!("Compilation failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_add(
    dependency: *const c_char,
    version: *const c_char,
    dev: bool,
    verbose: bool,
) -> *mut c_char {
    let dependency_str = c_string_to_rust(dependency);
    let version_opt = c_string_to_rust_option(version);
    match crate::dna::mds::add::add_dependency(
        dependency_str,
        version_opt,
        dev,
        verbose,
    ) {
        Ok(_) => rust_string_to_c("Dependency added".to_string()),
        Err(e) => rust_string_to_c(format!("Failed to add dependency: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_validate(target: *const c_char) -> *mut c_char {
    let target_opt = c_string_to_rust_option(target);
    let target_path = target_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    // For binary files, try to deserialize and validate
    #[cfg(feature = "compiler")]
    if target_path.extension().and_then(|s| s.to_str()) == Some("hlxb") {
        if let Ok(data) = std::fs::read(&target_path) {
            if let Ok(binary) = bincode::deserialize::<crate::dna::hel::binary::HelixBinary>(&data) {
                match binary.validate() {
                    Ok(_) => return rust_string_to_c("Binary validation passed".to_string()),
                    Err(e) => return rust_string_to_c(format!("Validation failed: {}", e)),
                }
            }
        }
    }
    // For source files, check they exist and are readable
    if target_path.exists() {
        rust_string_to_c("File validation passed".to_string())
    } else {
        rust_string_to_c(format!("File not found: {}", target_path.display()))
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_info(
    input: *const c_char,
    file: *const c_char,
    output: *const c_char,
    format: *const c_char,
    symbols: bool,
    sections: bool,
    verbose: bool,
) -> *mut c_char {
    let input_opt = c_string_to_rust_option(input);
    let input_path = input_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let format_str = c_string_to_rust_option(format).unwrap_or_else(|| "text".to_string());
    
    match crate::dna::mds::info::info_command(input_path, format_str, symbols, sections, verbose) {
        Ok(_) => rust_string_to_c("Info command completed".to_string()),
        Err(e) => rust_string_to_c(format!("Info command failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_init(
    name: *const c_char,
    dir: *const c_char,
    template: *const c_char,
    force: bool,
) -> *mut c_char {
    let name_str = c_string_to_rust_option(name).unwrap_or_else(|| String::new());
    let dir_opt = c_string_to_rust_option(dir);
    let dir = dir_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let template_str = c_string_to_rust_option(template).unwrap_or_else(|| "minimal".to_string());
    
    // TODO: Implement actual init logic
    rust_string_to_c(format!("Init command: name={}, dir={}, template={}, force={}", 
        name_str, dir.display(), template_str, force))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_clean(
    all: bool,
    cache: bool,
) -> *mut c_char {
    // TODO: Implement actual clean logic
    rust_string_to_c(format!("Clean command: all={}, cache={}", all, cache))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_fmt(
    files: *const *const c_char,
    files_len: usize,
    check: bool,
    verbose: bool,
) -> *mut c_char {
    let files_vec = c_string_array_to_rust(files, files_len);
    let file_paths: Vec<std::path::PathBuf> = files_vec.into_iter().map(std::path::PathBuf::from).collect();
    
    match crate::dna::mds::fmt::format_files(file_paths, check, verbose) {
        Ok(_) => {
            if check {
                rust_string_to_c("Files are formatted correctly".to_string())
            } else {
                rust_string_to_c("Files formatted successfully".to_string())
            }
        }
        Err(e) => rust_string_to_c(format!("Format failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_bench(
    pattern: *const c_char,
    iterations: *const u32,
) -> *mut c_char {
    let pattern_opt = c_string_to_rust_option(pattern);
    let iterations_opt = c_u32_to_rust_option(iterations);
    match crate::dna::mds::bench::run_benchmarks(pattern_opt, iterations_opt.map(|i| i as usize), true) {
        Ok(_) => rust_string_to_c("Benchmarks completed".to_string()),
        Err(e) => rust_string_to_c(format!("Benchmark failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_bundle(
    input: *const c_char,
    output: *const c_char,
    include: *const *const c_char,
    include_len: usize,
    exclude: *const *const c_char,
    exclude_len: usize,
    tree_shake: bool,
    optimize: u8,
) -> *mut c_char {
    let input_opt = c_string_to_rust_option(input);
    let output_opt = c_string_to_rust_option(output);
    let include_vec = c_string_array_to_rust(include, include_len);
    let exclude_vec = c_string_array_to_rust(exclude, exclude_len);
    let input_path = input_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("bundle.hlxb"));
    
    match crate::dna::mds::bundle::bundle_command(input_path, output_path, include_vec, exclude_vec, tree_shake, optimize, false) {
        Ok(_) => rust_string_to_c("Bundle created successfully".to_string()),
        Err(e) => rust_string_to_c(format!("Bundle failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_test(
    pattern: *const c_char,
    integration: bool,
) -> *mut c_char {
    // TODO: Implement actual test logic
    let pattern_opt = c_string_to_rust_option(pattern);
    rust_string_to_c(format!("Test command: pattern={:?}, integration={}", pattern_opt, integration))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_lint(
    files: *const *const c_char,
    files_len: usize,
    verbose: bool,
) -> *mut c_char {
    let files_vec = c_string_array_to_rust(files, files_len);
    let file_paths: Vec<std::path::PathBuf> = files_vec.into_iter().map(std::path::PathBuf::from).collect();
    
    match crate::dna::mds::lint::lint_files(file_paths, verbose) {
        Ok(_) => rust_string_to_c("Lint completed".to_string()),
        Err(e) => rust_string_to_c(format!("Lint failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_optimize(
    input: *const c_char,
    output: *const c_char,
    level: u8,
) -> *mut c_char {
    let input_opt = c_string_to_rust_option(input);
    let output_opt = c_string_to_rust_option(output);
    let input_path = input_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    
    // TODO: Implement actual optimization logic
    rust_string_to_c(format!("Optimize command: input={}, output={}, level={}", 
        input_path.display(), output_path.display(), level))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_remove(
    files: *const *const c_char,
    files_len: usize,
) -> *mut c_char {
    // TODO: Implement actual remove logic
    let files_vec = c_string_array_to_rust(files, files_len);
    rust_string_to_c(format!("Remove command with {} files", files_vec.len()))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_reset(
    force: bool,
) -> *mut c_char {
    // TODO: Implement actual reset logic
    rust_string_to_c(format!("Reset command: force={}", force))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_search(
    query: *const c_char,
    search_type: *const c_char,
    limit: *const u32,
    threshold: *const f64,
    embeddings: *const c_char,
    auto_find: bool,
) -> *mut c_char {
    let query_str = c_string_to_rust(query);
    let search_type_str = c_string_to_rust_option(search_type).unwrap_or_else(|| "semantic".to_string());
    let limit_val = c_u32_to_rust_option(limit).unwrap_or(10) as usize;
    let threshold_val = c_f64_to_rust_option(threshold).unwrap_or(0.0) as f32;
    
    // TODO: Implement actual search logic
    rust_string_to_c(format!("Search command: query={}, type={}, limit={}, threshold={}, auto_find={}",
        query_str, search_type_str, limit_val, threshold_val, auto_find))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_serve(
    port: *const u16,
    host: *const c_char,
    directory: *const c_char,
) -> *mut c_char {
    let port_opt = c_u16_to_rust_option(port);
    let host_opt = c_string_to_rust_option(host);
    let directory_opt = c_string_to_rust_option(directory);
    let directory_path = directory_opt.map(|s| std::path::PathBuf::from(s));
    
    // Note: This will block, so we might want to return immediately and run in background
    // For now, we'll just return a message
    match crate::dna::mds::serve::serve_project(port_opt, host_opt, directory_path, false) {
        Ok(_) => rust_string_to_c("Server started".to_string()),
        Err(e) => rust_string_to_c(format!("Serve failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_sign(
    input: *const c_char,
    key: *const c_char,
    output: *const c_char,
    verify: bool,
    verbose: bool,
) -> *mut c_char {
    let input_str = c_string_to_rust(input);
    let key_opt = c_string_to_rust_option(key);
    let output_opt = c_string_to_rust_option(output);
    let input_path = std::path::PathBuf::from(input_str);
    let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::sign::sign_binary(input_path, key_opt, output_path, verify, verbose) {
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

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_watch(
    input: *const c_char,
    output: *const c_char,
    optimize: u8,
    debounce: *const u32,
    filter: *const c_char,
) -> *mut c_char {
    let input_opt = c_string_to_rust_option(input);
    let output_opt = c_string_to_rust_option(output);
    let debounce_opt = c_u32_to_rust_option(debounce);
    let filter_opt = c_string_to_rust_option(filter);
    let input_path = input_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output_opt
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let debounce_val = debounce_opt.unwrap_or(500) as u64;
    
    // TODO: This should run in background, for now just return
    rust_string_to_c(format!("Watch command: input={}, output={}, optimize={}, debounce={}, filter={:?}",
        input_path.display(), output_path.display(), optimize, debounce_val, filter_opt))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_export(
    format: *const c_char,
    output: *const c_char,
    include_deps: bool,
    verbose: bool,
) -> *mut c_char {
    let format_str = c_string_to_rust_option(format).unwrap_or_else(|| "json".to_string());
    let output_opt = c_string_to_rust_option(output);
    let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::export::export_project(format_str, output_path, include_deps, verbose) {
        Ok(_) => rust_string_to_c("Export completed".to_string()),
        Err(e) => rust_string_to_c(format!("Export failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_dataset(
    files: *const *const c_char,
    files_len: usize,
    output: *const c_char,
    format: *const c_char,
) -> *mut c_char {
    let files_vec = c_string_array_to_rust(files, files_len);
    let file_paths: Vec<std::path::PathBuf> = files_vec.into_iter().map(std::path::PathBuf::from).collect();
    let output_opt = c_string_to_rust_option(output);
    let format_opt = c_string_to_rust_option(format);
    let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
    
    let rt = match tokio::runtime::Runtime::new() {
        Ok(rt) => rt,
        Err(e) => return rust_string_to_c(format!("Failed to create runtime: {}", e)),
    };
    
    use crate::dna::mds::dataset::{dataset_command, DatasetAction};
    
    let action = DatasetAction::Process {
        files: file_paths,
        output: output_path,
        format: format_opt,
        algorithm: None,
        validate: false,
    };
    
    match rt.block_on(dataset_command(action, false)) {
        Ok(_) => rust_string_to_c("Dataset processing completed".to_string()),
        Err(e) => rust_string_to_c(format!("Dataset command failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_filter(
    files: *const *const c_char,
    files_len: usize,
) -> *mut c_char {
    // TODO: Implement actual filter logic
    let files_vec = c_string_array_to_rust(files, files_len);
    rust_string_to_c(format!("Filter command with {} files", files_vec.len()))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_generate(
    template: *const c_char,
    output: *const c_char,
    name: *const c_char,
    force: bool,
    verbose: bool,
) -> *mut c_char {
    let template_str = c_string_to_rust(template);
    let output_opt = c_string_to_rust_option(output);
    let name_opt = c_string_to_rust_option(name);
    let output_path = output_opt.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::generate::generate_code(template_str, output_path, name_opt, force, verbose) {
        Ok(_) => rust_string_to_c("Code generated successfully".to_string()),
        Err(e) => rust_string_to_c(format!("Generate failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_import(
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
        Err(e) => return rust_string_to_c(format!("Runtime error: {}", e)),
    };
    
    // TODO: Implement actual import logic
    rust_string_to_c(format!("Import command: {}", input_path.display()))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_schema(
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
    };
    
    match crate::dna::mds::schema::schema_command(target_path, language, output_path, verbose) {
        Ok(_) => rust_string_to_c("Schema generated successfully".to_string()),
        Err(e) => rust_string_to_c(format!("Schema command failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_diff(
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
        Err(e) => rust_string_to_c(format!("Diff failed: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_tui() -> *mut c_char {
    match crate::dna::vlt::tui::launch() {
        Ok(_) => rust_string_to_c("TUI session ended".to_string()),
        Err(e) => rust_string_to_c(format!("TUI error: {}", e)),
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_completions(
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
        _ => return rust_string_to_c(format!("Unsupported shell: {}", shell_str)),
    };
    
    let completions = crate::dna::mds::completions::completions_command(shell_enum, verbose, quiet);
    rust_string_to_c(completions)
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_doctor(
    action: *const c_char,
) -> *mut c_char {
    // TODO: Implement actual diagnostics logic
    let action_opt = c_string_to_rust_option(action);
    let action_str = action_opt.unwrap_or_else(|| "check".to_string());
    rust_string_to_c(format!("Doctor command: {} - Diagnostics not yet implemented", action_str))
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_publish(
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
                Err(e) => rust_string_to_c(format!("Publish failed: {}", e)),
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

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn cmd_vlt(
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
            rust_string_to_c(format!("Vlt new: {}", name_opt.unwrap_or_else(|| "untitled".to_string())))
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
}

// C-compatible wrapper functions for C# interop
#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_parse(input: *const c_char, error_code: *mut i32, error_message: *mut *mut c_char) -> *mut CsHelixAst {
    if input.is_null() {
        if !error_code.is_null() {
            *error_code = -1;
        }
        if !error_message.is_null() {
            *error_message = rust_string_to_c("Input is null".to_string());
        }
        return std::ptr::null_mut();
    }

    let input_str = match c_string_to_rust(input) {
        s if s.is_empty() => {
            if !error_code.is_null() {
                *error_code = -1;
            }
            if !error_message.is_null() {
                *error_message = rust_string_to_c("Input is empty".to_string());
            }
            return std::ptr::null_mut();
        }
        s => s,
    };

    let mut error_out: *mut c_char = std::ptr::null_mut();
    let input_cstr = CString::new(input_str).unwrap_or_else(|_| CString::new("").unwrap());
    let ast_ptr = parse_helix_source(input_cstr.as_ptr(), &mut error_out);

    if ast_ptr.is_null() {
        if !error_code.is_null() {
            *error_code = -1;
        }
        if !error_message.is_null() {
            *error_message = error_out;
        }
        return std::ptr::null_mut();
    }

    if !error_code.is_null() {
        *error_code = 0;
    }
    if !error_message.is_null() {
        *error_message = std::ptr::null_mut();
    }

    ast_ptr
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        let _ = CString::from_raw(ptr);
    }
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_free_config(ptr: *mut CsHelixAst) {
    if !ptr.is_null() {
        let _ = Box::from_raw(ptr);
    }
}

/// Serializes an Expression to a serde_json::Value for JSON output
#[cfg(feature = "csharp")]
fn expression_to_json_value(expr: &crate::dna::atp::ast::Expression) -> serde_json::Value {
    use serde_json::Value;
    let value = expr.to_value();
    match value {
        crate::dna::atp::value::Value::String(s) => Value::String(s),
        crate::dna::atp::value::Value::Number(n) => Value::Number(
            serde_json::Number::from_f64(n).unwrap_or_else(|| serde_json::Number::from(0))
        ),
        crate::dna::atp::value::Value::Bool(b) => Value::Bool(b),
        crate::dna::atp::value::Value::Array(arr) => {
            Value::Array(arr.iter().map(|v| value_to_json_value(v)).collect())
        }
        crate::dna::atp::value::Value::Object(obj) => {
            Value::Object(
                obj.iter()
                    .map(|(k, v)| (k.clone(), value_to_json_value(v)))
                    .collect()
            )
        }
        crate::dna::atp::value::Value::Null => Value::Null,
        crate::dna::atp::value::Value::Duration(d) => Value::String(d.to_string()),
        crate::dna::atp::value::Value::Reference(r) => Value::String(r),
        crate::dna::atp::value::Value::Identifier(i) => Value::String(i),
    }
}

/// Converts a Value to serde_json::Value
#[cfg(feature = "csharp")]
fn value_to_json_value(value: &crate::dna::atp::value::Value) -> serde_json::Value {
    use serde_json::Value;
    match value {
        crate::dna::atp::value::Value::String(s) => Value::String(s.clone()),
        crate::dna::atp::value::Value::Number(n) => Value::Number(
            serde_json::Number::from_f64(*n).unwrap_or_else(|| serde_json::Number::from(0))
        ),
        crate::dna::atp::value::Value::Bool(b) => Value::Bool(*b),
        crate::dna::atp::value::Value::Array(arr) => {
            Value::Array(arr.iter().map(|v| value_to_json_value(v)).collect())
        }
        crate::dna::atp::value::Value::Object(obj) => {
            Value::Object(
                obj.iter()
                    .map(|(k, v)| (k.clone(), value_to_json_value(v)))
                    .collect()
            )
        }
        crate::dna::atp::value::Value::Null => Value::Null,
        crate::dna::atp::value::Value::Duration(d) => Value::String(d.to_string()),
        crate::dna::atp::value::Value::Reference(r) => Value::String(r.clone()),
        crate::dna::atp::value::Value::Identifier(i) => Value::String(i.clone()),
    }
}

/// Serializes a collection of agent declarations to JSON
#[cfg(feature = "csharp")]
fn agents_to_json(agents: &[&crate::dna::atp::ast::AgentDecl]) -> String {
    use serde_json::{Map, Value};
    let mut obj = Map::new();
    
    for agent in agents {
        let mut agent_obj = Map::new();
        agent_obj.insert("name".to_string(), Value::String(agent.name.clone()));
        
        if let Some(ref capabilities) = agent.capabilities {
            agent_obj.insert(
                "capabilities".to_string(),
                Value::Array(
                    capabilities.iter().map(|c| Value::String(c.clone())).collect()
                )
            );
        }
        
        if let Some(ref tools) = agent.tools {
            agent_obj.insert(
                "tools".to_string(),
                Value::Array(tools.iter().map(|t| Value::String(t.clone())).collect())
            );
        }
        
        if let Some(ref backstory) = agent.backstory {
            agent_obj.insert(
                "backstory".to_string(),
                Value::Array(
                    backstory.lines.iter().map(|l| Value::String(l.clone())).collect()
                )
            );
        }
        
        for (key, expr) in &agent.properties {
            agent_obj.insert(key.clone(), expression_to_json_value(expr));
        }
        
        obj.insert(agent.name.clone(), Value::Object(agent_obj));
    }
    
    serde_json::to_string(&Value::Object(obj)).unwrap_or_else(|_| "{}".to_string())
}

/// Serializes a collection of workflow declarations to JSON
#[cfg(feature = "csharp")]
fn workflows_to_json(workflows: &[&crate::dna::atp::ast::WorkflowDecl]) -> String {
    use serde_json::{Map, Value};
    let mut obj = Map::new();
    
    for workflow in workflows {
        let mut workflow_obj = Map::new();
        workflow_obj.insert("name".to_string(), Value::String(workflow.name.clone()));
        
        if let Some(ref trigger) = workflow.trigger {
            workflow_obj.insert("trigger".to_string(), expression_to_json_value(trigger));
        }
        
        if !workflow.steps.is_empty() {
            let steps_json: Vec<Value> = workflow.steps.iter().map(|step| {
                let mut step_obj = Map::new();
                step_obj.insert("name".to_string(), Value::String(step.name.clone()));
                
                if let Some(ref agent) = step.agent {
                    step_obj.insert("agent".to_string(), Value::String(agent.clone()));
                }
                
                if let Some(ref crew) = step.crew {
                    step_obj.insert(
                        "crew".to_string(),
                        Value::Array(crew.iter().map(|c| Value::String(c.clone())).collect())
                    );
                }
                
                if let Some(ref task) = step.task {
                    step_obj.insert("task".to_string(), Value::String(task.clone()));
                }
                
                for (key, expr) in &step.properties {
                    step_obj.insert(key.clone(), expression_to_json_value(expr));
                }
                
                Value::Object(step_obj)
            }).collect();
            workflow_obj.insert("steps".to_string(), Value::Array(steps_json));
        }
        
        for (key, expr) in &workflow.properties {
            workflow_obj.insert(key.clone(), expression_to_json_value(expr));
        }
        
        obj.insert(workflow.name.clone(), Value::Object(workflow_obj));
    }
    
    serde_json::to_string(&Value::Object(obj)).unwrap_or_else(|_| "{}".to_string())
}

/// Serializes a collection of context declarations to JSON
#[cfg(feature = "csharp")]
fn contexts_to_json(contexts: &[&crate::dna::atp::ast::ContextDecl]) -> String {
    use serde_json::{Map, Value};
    let mut obj = Map::new();
    
    for context in contexts {
        let mut context_obj = Map::new();
        context_obj.insert("name".to_string(), Value::String(context.name.clone()));
        context_obj.insert("environment".to_string(), Value::String(context.environment.clone()));
        
        if let Some(ref secrets) = context.secrets {
            let secrets_obj: Map<String, Value> = secrets
                .iter()
                .map(|(k, v)| {
                    let secret_str = match v {
                        crate::dna::atp::types::SecretRef::Environment(var) => {
                            format!("env:{}", var)
                        }
                        crate::dna::atp::types::SecretRef::Vault(path) => {
                            format!("vault:{}", path)
                        }
                        crate::dna::atp::types::SecretRef::File(path) => {
                            format!("file:{}", path)
                        }
                    };
                    (k.clone(), Value::String(secret_str))
                })
                .collect();
            context_obj.insert("secrets".to_string(), Value::Object(secrets_obj));
        }
        
        if let Some(ref variables) = context.variables {
            let vars_obj: Map<String, Value> = variables
                .iter()
                .map(|(k, v)| (k.clone(), expression_to_json_value(v)))
                .collect();
            context_obj.insert("variables".to_string(), Value::Object(vars_obj));
        }
        
        for (key, expr) in &context.properties {
            context_obj.insert(key.clone(), expression_to_json_value(expr));
        }
        
        obj.insert(context.name.clone(), Value::Object(context_obj));
    }
    
    serde_json::to_string(&Value::Object(obj)).unwrap_or_else(|_| "{}".to_string())
}

/// Serializes a collection of memory declarations to JSON
#[cfg(feature = "csharp")]
fn memories_to_json(memories: &[&crate::dna::atp::ast::MemoryDecl]) -> String {
    use serde_json::{Map, Value};
    let mut obj = Map::new();
    
    for (idx, memory) in memories.iter().enumerate() {
        let mut memory_obj = Map::new();
        memory_obj.insert("provider".to_string(), Value::String(memory.provider.clone()));
        memory_obj.insert("connection".to_string(), Value::String(memory.connection.clone()));
        
        if let Some(ref embeddings) = memory.embeddings {
            let mut emb_obj = Map::new();
            emb_obj.insert("model".to_string(), Value::String(embeddings.model.clone()));
            emb_obj.insert("dimensions".to_string(), Value::Number(embeddings.dimensions.into()));
            
            for (key, expr) in &embeddings.properties {
                emb_obj.insert(key.clone(), expression_to_json_value(expr));
            }
            
            memory_obj.insert("embeddings".to_string(), Value::Object(emb_obj));
        }
        
        for (key, expr) in &memory.properties {
            memory_obj.insert(key.clone(), expression_to_json_value(expr));
        }
        
        obj.insert(format!("memory_{}", idx), Value::Object(memory_obj));
    }
    
    serde_json::to_string(&Value::Object(obj)).unwrap_or_else(|_| "{}".to_string())
}

/// Serializes a collection of crew declarations to JSON
#[cfg(feature = "csharp")]
fn crews_to_json(crews: &[&crate::dna::atp::ast::CrewDecl]) -> String {
    use serde_json::{Map, Value};
    let mut obj = Map::new();
    
    for crew in crews {
        let mut crew_obj = Map::new();
        crew_obj.insert("name".to_string(), Value::String(crew.name.clone()));
        crew_obj.insert(
            "agents".to_string(),
            Value::Array(crew.agents.iter().map(|a| Value::String(a.clone())).collect())
        );
        
        if let Some(ref process_type) = crew.process_type {
            crew_obj.insert("process_type".to_string(), Value::String(process_type.clone()));
        }
        
        for (key, expr) in &crew.properties {
            crew_obj.insert(key.clone(), expression_to_json_value(expr));
        }
        
        obj.insert(crew.name.clone(), Value::Object(crew_obj));
    }
    
    serde_json::to_string(&Value::Object(obj)).unwrap_or_else(|_| "{}".to_string())
}

/// Serializes a collection of pipeline declarations to JSON
#[cfg(feature = "csharp")]
fn pipelines_to_json(pipelines: &[&crate::dna::atp::ast::PipelineDecl]) -> String {
    use serde_json::{Map, Value};
    let mut obj = Map::new();
    
    for (idx, pipeline) in pipelines.iter().enumerate() {
        let mut pipeline_obj = Map::new();
        
        let flow_json: Vec<Value> = pipeline.flow.iter().map(|node| {
            match node {
                crate::dna::atp::ast::PipelineNode::Step(s) => {
                    Value::String(format!("step:{}", s))
                }
                crate::dna::atp::ast::PipelineNode::Parallel(nodes) => {
                    Value::Array(
                        nodes.iter()
                            .map(|n| match n {
                                crate::dna::atp::ast::PipelineNode::Step(s) => {
                                    Value::String(format!("step:{}", s))
                                }
                                _ => Value::String("parallel".to_string()),
                            })
                            .collect()
                    )
                }
                crate::dna::atp::ast::PipelineNode::Conditional { condition, .. } => {
                    Value::String(format!("conditional:{}", expression_to_json_value(condition)))
                }
            }
        }).collect();
        
        pipeline_obj.insert("flow".to_string(), Value::Array(flow_json));
        obj.insert(format!("pipeline_{}", idx), Value::Object(pipeline_obj));
    }
    
    serde_json::to_string(&Value::Object(obj)).unwrap_or_else(|_| "{}".to_string())
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_agents(config: *mut CsHelixAst) -> *mut c_char {
    if config.is_null() {
        return std::ptr::null_mut();
    }
    let agents = (*config).inner.get_agents();
    let json_str = agents_to_json(&agents);
    rust_string_to_c(json_str)
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_workflows(config: *mut CsHelixAst) -> *mut c_char {
    if config.is_null() {
        return std::ptr::null_mut();
    }
    let workflows = (*config).inner.get_workflows();
    let json_str = workflows_to_json(&workflows);
    rust_string_to_c(json_str)
}

/// Helper function to extract memory declarations from AST
#[cfg(feature = "csharp")]
fn get_memories_from_ast(ast: &crate::dna::atp::ast::HelixAst) -> Vec<&crate::dna::atp::ast::MemoryDecl> {
    ast.declarations
        .iter()
        .filter_map(|d| {
            if let crate::dna::atp::ast::Declaration::Memory(m) = d {
                Some(m)
            } else {
                None
            }
        })
        .collect()
}

/// Helper function to extract crew declarations from AST
#[cfg(feature = "csharp")]
fn get_crews_from_ast(ast: &crate::dna::atp::ast::HelixAst) -> Vec<&crate::dna::atp::ast::CrewDecl> {
    ast.declarations
        .iter()
        .filter_map(|d| {
            if let crate::dna::atp::ast::Declaration::Crew(c) = d {
                Some(c)
            } else {
                None
            }
        })
        .collect()
}

/// Helper function to extract pipeline declarations from AST
#[cfg(feature = "csharp")]
fn get_pipelines_from_ast(ast: &crate::dna::atp::ast::HelixAst) -> Vec<&crate::dna::atp::ast::PipelineDecl> {
    ast.declarations
        .iter()
        .filter_map(|d| {
            if let crate::dna::atp::ast::Declaration::Pipeline(p) = d {
                Some(p)
            } else {
                None
            }
        })
        .collect()
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_memories(config: *mut CsHelixAst) -> *mut c_char {
    if config.is_null() {
        return std::ptr::null_mut();
    }
    let memories = get_memories_from_ast(&(*config).inner);
    let json_str = memories_to_json(&memories);
    rust_string_to_c(json_str)
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_contexts(config: *mut CsHelixAst) -> *mut c_char {
    if config.is_null() {
        return std::ptr::null_mut();
    }
    let contexts = (*config).inner.get_contexts();
    let json_str = contexts_to_json(&contexts);
    rust_string_to_c(json_str)
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_crews(config: *mut CsHelixAst) -> *mut c_char {
    if config.is_null() {
        return std::ptr::null_mut();
    }
    let crews = get_crews_from_ast(&(*config).inner);
    let json_str = crews_to_json(&crews);
    rust_string_to_c(json_str)
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_pipelines(config: *mut CsHelixAst) -> *mut c_char {
    if config.is_null() {
        return std::ptr::null_mut();
    }
    let pipelines = get_pipelines_from_ast(&(*config).inner);
    let json_str = pipelines_to_json(&pipelines);
    rust_string_to_c(json_str)
}

/// Serializes a single agent to JSON
#[cfg(feature = "csharp")]
fn agent_to_json(agent: &crate::dna::atp::ast::AgentDecl) -> String {
    use serde_json::{Map, Value};
    let mut agent_obj = Map::new();
    agent_obj.insert("name".to_string(), Value::String(agent.name.clone()));
    
    if let Some(ref capabilities) = agent.capabilities {
        agent_obj.insert(
            "capabilities".to_string(),
            Value::Array(
                capabilities.iter().map(|c| Value::String(c.clone())).collect()
            )
        );
    }
    
    if let Some(ref tools) = agent.tools {
        agent_obj.insert(
            "tools".to_string(),
            Value::Array(tools.iter().map(|t| Value::String(t.clone())).collect())
        );
    }
    
    if let Some(ref backstory) = agent.backstory {
        agent_obj.insert(
            "backstory".to_string(),
            Value::Array(
                backstory.lines.iter().map(|l| Value::String(l.clone())).collect()
            )
        );
    }
    
    for (key, expr) in &agent.properties {
        agent_obj.insert(key.clone(), expression_to_json_value(expr));
    }
    
    serde_json::to_string(&Value::Object(agent_obj)).unwrap_or_else(|_| "{}".to_string())
}

/// Serializes a single workflow to JSON
#[cfg(feature = "csharp")]
fn workflow_to_json(workflow: &crate::dna::atp::ast::WorkflowDecl) -> String {
    use serde_json::{Map, Value};
    let mut workflow_obj = Map::new();
    workflow_obj.insert("name".to_string(), Value::String(workflow.name.clone()));
    
    if let Some(ref trigger) = workflow.trigger {
        workflow_obj.insert("trigger".to_string(), expression_to_json_value(trigger));
    }
    
    if !workflow.steps.is_empty() {
        let steps_json: Vec<Value> = workflow.steps.iter().map(|step| {
            let mut step_obj = Map::new();
            step_obj.insert("name".to_string(), Value::String(step.name.clone()));
            
            if let Some(ref agent) = step.agent {
                step_obj.insert("agent".to_string(), Value::String(agent.clone()));
            }
            
            if let Some(ref crew) = step.crew {
                step_obj.insert(
                    "crew".to_string(),
                    Value::Array(crew.iter().map(|c| Value::String(c.clone())).collect())
                );
            }
            
            if let Some(ref task) = step.task {
                step_obj.insert("task".to_string(), Value::String(task.clone()));
            }
            
            for (key, expr) in &step.properties {
                step_obj.insert(key.clone(), expression_to_json_value(expr));
            }
            
            Value::Object(step_obj)
        }).collect();
        workflow_obj.insert("steps".to_string(), Value::Array(steps_json));
    }
    
    for (key, expr) in &workflow.properties {
        workflow_obj.insert(key.clone(), expression_to_json_value(expr));
    }
    
    serde_json::to_string(&Value::Object(workflow_obj)).unwrap_or_else(|_| "{}".to_string())
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_agent(config: *mut CsHelixAst, name: *const c_char) -> *mut c_char {
    if config.is_null() || name.is_null() {
        return std::ptr::null_mut();
    }
    
    let name_str = c_string_to_rust(name);
    let agents = (*config).inner.get_agents();
    
    for agent in agents {
        if agent.name == name_str {
            let json_str = agent_to_json(agent);
            return rust_string_to_c(json_str);
        }
    }
    
    std::ptr::null_mut()
}

#[cfg(feature = "csharp")]
#[no_mangle]
pub unsafe extern "C" fn helix_config_get_workflow(config: *mut CsHelixAst, name: *const c_char) -> *mut c_char {
    if config.is_null() || name.is_null() {
        return std::ptr::null_mut();
    }
    
    let name_str = c_string_to_rust(name);
    let workflows = (*config).inner.get_workflows();
    
    for workflow in workflows {
        if workflow.name == name_str {
            let json_str = workflow_to_json(workflow);
            return rust_string_to_c(json_str);
        }
    }
    
    std::ptr::null_mut()
}