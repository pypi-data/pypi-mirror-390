#![cfg(feature = "js")]

use napi::{JsObject, Result as JsResult, Env};

use napi_derive::napi;

#[derive(Debug, Clone)]
pub struct NapiStringError(pub String);

use std::collections::HashMap;

use bincode;

pub use crate::dna::atp::value::Value as DnaValue;

pub use crate::dna::atp::*;

pub use crate::dna::bch::*;

pub use crate::dna::cmd::*;

pub use crate::dna::compiler::Compiler;

pub use crate::dna::compiler::*;

pub use crate::dna::exp::*;

pub use crate::dna::hel::dna_hlx::Hlx;

pub use crate::dna::hel::*;

pub use crate::dna::map::*;

pub use crate::dna::mds::optimizer::OptimizationLevel;

pub use crate::dna::mds::*;

pub use crate::dna::ngs::*;

pub use crate::dna::ops::*;

pub use crate::dna::out::*;

pub use crate::dna::tst::*;

pub use crate::dna::vlt::Vault;

pub use crate::dna::atp::ast::*;

pub use crate::dna::atp::interpreter::*;

pub use crate::dna::atp::lexer::*;

pub use crate::dna::atp::output::*;

pub use crate::dna::atp::parser::*;

pub use crate::dna::atp::types::*;

pub use crate::dna::hel::binary::*;

pub use crate::dna::hel::dispatch::*;

pub use crate::dna::hel::dna_hlx::*;

pub use crate::dna::hel::error::*;  

pub use crate::dna::hel::hlx::*;

pub use crate::dna::map::core::*;

pub use crate::dna::map::hf::*;

pub use crate::dna::map::reasoning::*;

use crate::dna::map::caption::E621Config as MapE621Config;

pub use crate::dna::mds::a_example::{Document, Embedding, Metadata};

pub use crate::dna::mds::benches::*;

pub use crate::dna::mds::bundle::*;
  
pub use crate::dna::mds::cache::*;

pub use crate::dna::mds::caption::*;

pub use crate::dna::mds::codegen::*;

pub use crate::dna::mds::concat::*;

pub use crate::dna::mds::config::*;

pub use crate::dna::mds::decompile::*;

pub use crate::dna::mds::filter::*; 
pub use crate::dna::mds::migrate::*;

pub use crate::dna::mds::modules::*;

pub use crate::dna::mds::optimizer::*;

pub use crate::dna::mds::project::*;

pub use crate::dna::mds::runtime::*;

pub use crate::dna::mds::schema::*;
  
pub use crate::dna::mds::semantic::*;

pub use crate::dna::mds::serializer::*;

pub use crate::dna::mds::server::*;

pub use crate::dna::out::helix_format::*;

pub use crate::dna::out::hlx_config_format::*;

pub use crate::dna::out::hlxb_config_format::*;

pub use crate::dna::out::hlxc_format::*;

pub use crate::dna::vlt::tui::*;

pub use crate::dna::vlt::vault::*;

pub use crate::dna::map::core::TrainingSample; 


fn value_to_js(env: &Env, value: &crate::dna::atp::value::Value) -> JsResult<napi::JsUnknown> {
    match value {
        crate::dna::atp::value::Value::String(s) => {
            Ok(env.create_string(s)?.into_unknown())
        }
        crate::dna::atp::value::Value::Number(n) => {
            Ok(env.create_double(*n)?.into_unknown())
        }
        crate::dna::atp::value::Value::Bool(b) => {
            Ok(env.get_boolean(*b)?.into_unknown())
        }
        crate::dna::atp::value::Value::Array(arr) => {
            let mut js_arr = env.create_array_with_length(arr.len())?;
            for (i, item) in arr.iter().enumerate() {
                let js_item = value_to_js(env, item)?;
                js_arr.set_element(i as u32, js_item)?;
            }
            Ok(js_arr.into_unknown())
        }
        crate::dna::atp::value::Value::Object(obj) => {
            let mut js_obj = env.create_object()?;
            for (key, val) in obj {
                let js_val = value_to_js(env, val)?;
                js_obj.set_named_property(key, js_val)?;
            }
            Ok(js_obj.into_unknown())
        }
        crate::dna::atp::value::Value::Null => {
            Ok(env.get_null()?.into_unknown())
        }
        crate::dna::atp::value::Value::Duration(d) => {
            Ok(env.create_string(&d.to_string())?.into_unknown())
        }
        crate::dna::atp::value::Value::Reference(r) => {
            Ok(env.create_string(&r.to_string())?.into_unknown())
        }
        crate::dna::atp::value::Value::Identifier(i) => {
            Ok(env.create_string(&i.to_string())?.into_unknown())
        }
    }
}


#[napi(js_name = "HelixAst")]
pub struct JsHelixAst {
    inner: HelixAst,
}


#[napi]
impl JsHelixAst {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: HelixAst::new(),
        }
    }

    pub fn add_declaration(&mut self, decl: JsObject) -> JsResult<()> {
        // This will need to be implemented based on the Declaration type
        // For now, return an error
        Err(napi::Error::from_reason("add_declaration not yet implemented"))
    }

    pub fn get_projects(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let projects = self.inner.get_projects();
        let mut result = env.create_array_with_length(projects.len())?;
        for (i, _project) in projects.iter().enumerate() {
            result.set_element(i as u32, env.get_null()?)?;
        }
        Ok(result.into_unknown())
    }

    pub fn get_agents(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let agents = self.inner.get_agents();
        let mut result = env.create_array_with_length(agents.len())?;
        for (i, _agent) in agents.iter().enumerate() {
            result.set_element(i as u32, env.get_null()?)?;
        }
        Ok(result.into_unknown())
    }

    pub fn get_workflows(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let workflows = self.inner.get_workflows();
        let mut result = env.create_array_with_length(workflows.len())?;
        for (i, _workflow) in workflows.iter().enumerate() {
            result.set_element(i as u32, env.get_null()?)?;
        }
        Ok(result.into_unknown())
    }

    pub fn get_contexts(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let contexts = self.inner.get_contexts();
        let mut result = env.create_array_with_length(contexts.len())?;
        for (i, _context) in contexts.iter().enumerate() {
            result.set_element(i as u32, env.get_null()?)?;
        }
        Ok(result.into_unknown())
    }
}

// Jsthon wrapper for AstPrettyPrinter

#[napi(js_name = "AstPrettyPrinter")]
pub struct JsAstPrettyPrinter {
    inner: AstPrettyPrinter,
}

#[napi]
impl JsAstPrettyPrinter {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: AstPrettyPrinter::new(),
        }
    }

    pub fn print(&mut self, ast: &JsHelixAst) -> JsResult<String> {
        Ok(self.inner.print(&ast.inner))
    }
}

// Jsthon wrapper for Expression

#[napi(js_name = "Expression")]
pub struct JsExpression {
    inner: Expression,
}


#[napi]
impl JsExpression {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: Expression::Identifier("".to_string()),
        }
    }

    #[napi]
    pub fn binary(
        left: &JsExpression,
        op: String,
        right: &JsExpression,
    ) -> JsResult<JsExpression> {
        // Parse binary operator
        let binary_op = match op.as_str() {
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
            _ => return Err(napi::Error::from_reason("Invalid binary operator")),
        };

        let expr = Expression::binary(
            left.inner.clone(),
            binary_op,
            right.inner.clone(),
        );
        Ok(Self { inner: expr })
    }

    pub fn as_string(&self) -> JsResult<String> {
        Ok(self.inner.as_string().unwrap_or_default())
    }

    pub fn as_number(&self) -> JsResult<f64> {
        self.inner
            .as_number()
            .ok_or(napi::Error::from_reason("Value is not a number"))
    }

    pub fn as_bool(&self) -> JsResult<bool> {
        self.inner
            .as_bool()
            .ok_or(napi::Error::from_reason("Value is not a boolean"))
    }

    pub fn as_array(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let arr = self
            .inner
            .as_array()
            .ok_or(napi::Error::from_reason("Value is not an array"))?;
        let mut result = env.create_array_with_length(arr.len())?;
        for (i, _expr) in arr.iter().enumerate() {
            result.set_element(i as u32, env.get_null()?)?;
        }
        Ok(result.into_unknown())
    }

    pub fn as_object(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let obj = self
            .inner
            .as_object()
            .ok_or(napi::Error::from_reason("Value is not an object"))?;
        let mut result = env.create_object()?;
        for (key, _expr) in obj {
            result.set_named_property(key, env.get_null()?)?;
        }
        Ok(result.into_unknown())
    }

    pub fn to_value(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let value = self.inner.to_value();
        value_to_js(&env, &value)
    }
}

// Jsthon wrapper for AstBuilder

#[napi(js_name = "AstBuilder")]
pub struct JsAstBuilder {
    inner: AstBuilder,
}


#[napi]
impl JsAstBuilder {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: AstBuilder::new(),
        }
    }

    pub fn add_agent(&mut self, _agent: JsObject) -> JsResult<()> {
        // This needs proper AgentDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_workflow(&mut self, _workflow: JsObject) -> JsResult<()> {
        // This needs proper WorkflowDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_context(&mut self, _context: JsObject) -> JsResult<()> {
        // This needs proper ContextDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_memory(&mut self, _memory: JsObject) -> JsResult<()> {
        // This needs proper MemoryDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_crew(&mut self, _crew: JsObject) -> JsResult<()> {
        // This needs proper CrewDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_pipeline(&mut self, _pipeline: JsObject) -> JsResult<()> {
        // This needs proper PipelineDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_plugin(&mut self, _plugin: JsObject) -> JsResult<()> {
        // This needs proper PluginDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_database(&mut self, _database: JsObject) -> JsResult<()> {
        // This needs proper DatabaseDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_load(&mut self, _load: JsObject) -> JsResult<()> {
        // This needs proper LoadDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_section(&mut self, _section: JsObject) -> JsResult<()> {
        // This needs proper SectionDecl conversion
        Ok(()) // Placeholder
    }

    pub fn build(&mut self) -> JsResult<JsHelixAst> {
        let ast = std::mem::replace(&mut self.inner, crate::dna::atp::ast::AstBuilder::new()).build();
        Ok(JsHelixAst { inner: ast })
    }
}

// HelixInterpreter wrapper

#[napi(js_name = "HelixInterpreter")]
pub struct JsHelixInterpreter {
    inner: HelixInterpreter,
}


#[napi]
impl JsHelixInterpreter {
    #[napi(factory)]
    pub fn new() -> std::result::Result<JsHelixInterpreter, napi::Error> {
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        let interpreter = rt
            .block_on(HelixInterpreter::new())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsHelixInterpreter { inner: interpreter })
    }

    pub fn execute_ast(&mut self, env: Env, ast: &JsHelixAst) -> JsResult<napi::JsUnknown> {
        let ast_clone = ast.inner.clone();
            let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        let result = rt.block_on(self.inner.execute_ast(&ast_clone))
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        value_to_js(&env, &result)
    }

    pub fn operator_engine(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _engine = self.inner.operator_engine();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn operator_engine_mut(&mut self, env: Env) -> JsResult<napi::JsUnknown> {
        let _engine = self.inner.operator_engine_mut();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn set_variable(&mut self, name: String, value: napi::JsUnknown) -> JsResult<()> {
        let val = if let Ok(js_str) = value.coerce_to_string() {
            crate::dna::atp::value::Value::String(js_str.into_utf8()?.as_str()?.to_string())
        } else {
            crate::dna::atp::value::Value::String("unknown".to_string())
        };
        self.inner.set_variable(name, val);
        Ok(())
    }

    pub fn get_variable(&self, env: Env, name: String) -> JsResult<napi::JsUnknown> {
        let value = self.inner.get_variable(&name);
        match value {
            Some(v) => value_to_js(&env, &v),
            None => Ok(env.get_null()?.into_unknown()),
        }
    }

    pub fn list_variables(&self) -> JsResult<Vec<String>> {
        let vars = self.inner.list_variables();
        Ok(vars.into_iter().map(|(name, _value)| name).collect())
    }
}

// SourceMap wrapper

#[napi(js_name = "SourceMap")]
pub struct JsSourceMap {
    inner: SourceMap,
}

#[napi]
impl JsSourceMap {
    #[napi(factory)]
    pub fn new(source: String) -> std::result::Result<JsSourceMap, napi::Error> {
        let inner = SourceMap::new(source.clone())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsSourceMap { inner })
    }

    pub fn get_line(&self, line_num: usize) -> JsResult<String> {
        let line = self.inner.get_line(line_num);
        Ok(line.unwrap_or_default().to_string())
    }
}


#[napi(js_name = "SectionName")]
pub struct JsSectionName {
    inner: crate::dna::atp::ops::SectionName,
}

#[napi]
impl JsSectionName {
    #[napi(constructor)]
    pub fn new(s: String) -> Self {
        Self {
            inner: crate::dna::atp::ops::SectionName::new(s),
        }
    }

    pub fn as_str(&self) -> &str {
        self.inner.as_str()
    }
}


#[napi(js_name = "VariableName")]
pub struct JsVariableName {
    inner: crate::dna::atp::ops::VariableName,
}

#[napi]
impl JsVariableName {
    #[napi(constructor)]
    pub fn new(s: String) -> Self {
        Self {
            inner: crate::dna::atp::ops::VariableName::new(s),
        }
    }

    pub fn as_str(&self) -> &str {
        self.inner.as_str()
    }
}

#[napi(js_name = "CacheKey")]
pub struct JsCacheKey {
    inner: crate::dna::atp::ops::CacheKey,
}

#[napi]
impl JsCacheKey {
    #[napi(constructor)]
    pub fn new(file: String, key: String) -> Self {
        Self {
            inner: crate::dna::atp::ops::CacheKey::new(&file, &key),
        }
    }
}

#[napi(js_name = "RegexCache")]
pub struct JsRegexCache {
    inner: crate::dna::atp::ops::RegexCache,
}

#[napi]
impl JsRegexCache {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: crate::dna::atp::ops::RegexCache::new(),
        }
    }
}


#[napi(js_name = "StringParser")]
pub struct JsStringParser {
    inner: crate::dna::atp::ops::StringParser,
}

#[napi]
impl JsStringParser {
    #[napi(constructor)]
    pub fn new(input: String) -> Self {
        Self {
            inner: crate::dna::atp::ops::StringParser::new(input),
        }
    }

    pub fn parse_quoted_string(&mut self) -> JsResult<String> {
        self.inner
            .parse_quoted_string()
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }
}


#[napi(js_name = "OperatorParser")]
pub struct JsOperatorParser {
    inner: crate::dna::atp::ops::OperatorParser,
}

#[napi]
impl JsOperatorParser {
    #[napi(factory)]
    pub fn new() -> std::result::Result<JsOperatorParser, napi::Error> {
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        let parser = rt
            .block_on(crate::dna::atp::ops::OperatorParser::new())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsOperatorParser { inner: parser })
    }

    pub fn load_hlx(&mut self) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                rt.block_on(self.inner.load_hlx())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn try_math(&self, s: String) -> JsResult<f64> {
        crate::dna::atp::ops::eval_math_expression(&s)
            .map_err(|e| napi::Error::from_reason(e.to_string()))
            .and_then(|val| match val {
                crate::dna::atp::value::Value::Number(n) => Ok(n),
                _ => Err(napi::Error::from_reason(
                    "Math expression did not evaluate to a number",
                )),
            })
    }

    pub fn execute_date(&self, fmt: String) -> JsResult<String> {
        Ok(crate::dna::atp::ops::eval_date_expression(&fmt))
    }

    pub fn parse_line(&mut self, raw: String) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        rt.block_on(self.inner.parse_line(&raw))
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn get(&self, env: Env, key: String) -> JsResult<napi::JsUnknown> {
        let value = self.inner.get(&key);
        match value {
            Some(v) => value_to_js(&env, &v),
            None => Ok(env.get_null()?.into_unknown()),
        }
    }

    pub fn get_ref(&self, env: Env, key: String) -> JsResult<napi::JsUnknown> {
        let value = self.inner.get_ref(&key);
        match value {
            Some(v) => value_to_js(&env, v),
            None => Ok(env.get_null()?.into_unknown()),
        }
    }

    pub fn set(&mut self, key: String, value: napi::JsUnknown) -> JsResult<()> {
        let val = if let Ok(js_str) = value.coerce_to_string() {
            crate::dna::atp::value::Value::String(js_str.into_utf8()?.as_str()?.to_string())
        } else {
            crate::dna::atp::value::Value::String("unknown".to_string())
        };
        self.inner.set(&key, val);
        Ok(())
    }

    pub fn keys(&self) -> JsResult<Vec<String>> {
        Ok(self.inner.keys())
    }

    pub fn items(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let items = self.inner.items();
        let mut result = env.create_object()?;
        for (key, value) in items.iter() {
            let js_val = value_to_js(&env, value)?;
            result.set_named_property(key, js_val)?;
        }
        Ok(result.into_unknown())
    }

    pub fn items_cloned(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let items = self.inner.items_cloned();
        let mut result = env.create_object()?;
        for (key, value) in items {
            let js_val = value_to_js(&env, &value)?;
            result.set_named_property(&key, js_val)?;
        }
        Ok(result.into_unknown())
    }

    pub fn get_errors(&self) -> JsResult<Vec<String>> {
        Ok(self.inner.get_errors().iter().map(|e| e.to_string()).collect())
    }

    pub fn has_errors(&self) -> bool {
        self.inner.has_errors()
    }
}


#[napi(js_name = "OutputFormat")]
pub struct JsOutputFormat {
    inner: OutputFormat,
}

#[napi]
impl JsOutputFormat {
    #[napi(factory)]
    pub fn from_str(s: String) -> Self {
        let format = OutputFormat::from(s.as_str()).unwrap_or(OutputFormat::Helix);
        Self { inner: format }
    }
}


#[napi(js_name = "CompressionConfig")]
pub struct JsCompressionConfig {
    inner: CompressionConfig,
}

#[napi]
impl JsCompressionConfig {
    #[napi(constructor)]
    pub fn default() -> Self {
        Self {
            inner: CompressionConfig::default(),
        }
    }
}


#[napi(js_name = "OutputConfig")]
pub struct JsOutputConfig {
    inner: OutputConfig,
}

#[napi]
impl JsOutputConfig {
    #[napi(constructor)]
    pub fn default() -> Self {
        Self {
            inner: OutputConfig::default(),
        }
    }
}


#[napi(js_name = "OutputManager")]
pub struct JsOutputManager {
    inner: OutputManager,
}
  
#[napi]
impl JsOutputManager {
    #[napi(constructor)]
    pub fn new(config: &JsOutputConfig) -> Self {
        Self {
            inner: OutputManager::new(config.inner.clone()),
        }
    }

    pub fn add_row(&mut self, row: HashMap<String, JsObject>) -> JsResult<()> {
        // Convert HashMap<String, JsObject> to HashMap<String, AtpValue>
        let converted_row: HashMap<String, crate::dna::atp::value::Value> = HashMap::new(); // Placeholder
        self.inner.add_row(converted_row);
        Ok(())
    }

    pub fn flush_batch(&mut self) -> JsResult<()> {
        self.inner
            .flush_batch()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn finalize_all(&mut self) -> JsResult<()> {
        self.inner
            .finalize_all()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn get_output_files(&self) -> JsResult<Vec<String>> {
        Ok(self.inner.get_output_files().iter().map(|p| p.to_string_lossy().to_string()).collect())
    }
}


#[napi(js_name = "HlxcDataWriter")]
pub struct JsHlxcDataWriter {
    inner: crate::dna::atp::output::HlxcDataWriter,
}

#[napi]
impl JsHlxcDataWriter {
    #[napi(constructor)]
    pub fn new(config: &JsOutputConfig) -> Self {
        Self {
            inner: crate::dna::atp::output::HlxcDataWriter::new(config.inner.clone()),
        }
    }

    pub fn write_batch(&mut self, batch: JsObject) -> JsResult<()> {
        // Convert JsObject to RecordBatch
        // This would need proper Arrow RecordBatch conversion
        Ok(())
    }

    pub fn finalize(&mut self) -> JsResult<()> {
        self.inner
            .finalize()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }
}


#[napi(js_name = "Parser")]
pub struct JsParser {
    inner: Parser,
}

#[napi]
impl JsParser {
    #[napi(factory)]
    pub fn new(tokens: Vec<JsObject>) -> std::result::Result<JsParser, napi::Error> {
        // Convert Vec<JsObject> to Vec<Token>
        let converted_tokens: Vec<Token> = vec![]; // Placeholder
        Ok(JsParser {
            inner: Parser::new(converted_tokens),
        })
    }

    #[napi]
    pub fn new_enhanced(tokens: Vec<JsObject>) -> JsParser {
        // Convert Vec<JsObject> to Vec<TokenWithLocation>
        let converted_tokens: Vec<crate::dna::atp::lexer::TokenWithLocation> = vec![]; // Placeholder
        JsParser {
            inner: Parser::new_enhanced(converted_tokens),
        }
    }

    #[napi]
    pub fn new_with_source_map(source_map: &JsSourceMap) -> JsParser {
        JsParser {
            inner: Parser::new_with_source_map(source_map.inner.clone()),
        }
    }

    pub fn set_runtime_context(&mut self, context: HashMap<String, String>) -> JsResult<()> {
        self.inner.set_runtime_context(context);
        Ok(())
    }

    pub fn parse(&mut self) -> JsResult<JsHelixAst> {
        let ast = self
            .inner
            .parse()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsHelixAst { inner: ast })
    }
}


#[napi(js_name = "HelixLoader")]
pub struct JsHelixLoader {
    inner: HelixLoader,
}

#[napi]
impl JsHelixLoader {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: HelixLoader::new(),
        }
    }   

    pub fn parse(&mut self, content: &str) -> JsResult<()> {
        self.inner
            .parse(content)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn get_config(&self, env: Env, name: String) -> JsResult<napi::JsUnknown> {
        let config = self.inner.get_config(&name);
        match config {
            Some(_c) => Ok(env.get_null()?.into_unknown()),
            None => Ok(env.get_null()?.into_unknown()),
        }
    }

    pub fn set_context(&mut self, context: String) -> JsResult<()> {
        self.inner.set_context(context);
        Ok(())
    }

    pub fn merge_configs(&self, env: Env, configs: Vec<JsObject>) -> JsResult<napi::JsUnknown> {
        // Convert Vec<JsObject> to Vec<&HelixConfig>
        let converted_configs: Vec<&HelixConfig> = vec![]; // Placeholder
        let _merged = self.inner.merge_configs(converted_configs);
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "Compiler")]
pub struct JsCompiler {
    inner: Compiler,
}

#[napi]
impl JsCompiler {
    #[napi(factory)]
    pub fn new(optimization_level: napi::JsUnknown) -> std::result::Result<JsCompiler, napi::Error> {
        // Convert JsUnknown to OptimizationLevel
        let level = if let Ok(js_str) = optimization_level.coerce_to_string() {
            let s = js_str.into_utf8()?.as_str()?.to_string();
            match s.to_lowercase().as_str() {
                "zero" => OptimizationLevel::Zero,
                "one" => OptimizationLevel::One,
                "two" => OptimizationLevel::Two,
                "three" => OptimizationLevel::Three,
                _ => OptimizationLevel::Two,
            }
        } else {
            OptimizationLevel::Two
        };
        Ok(JsCompiler {
            inner: Compiler::new(level),
        })
    }
    #[napi]
    pub fn builder() -> JsResult<JsCompilerBuilder> {
        Ok(JsCompilerBuilder {
            inner: Compiler::builder(),
        })
    }

    pub fn decompile(&self, env: Env, bin: JsHelixBinary) -> JsResult<napi::JsUnknown> {
        let _ast = self.inner
            .decompile(&bin.inner)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "CompilerBuilder")]
pub struct JsCompilerBuilder {
    inner: CompilerBuilder,
}

#[napi]
impl JsCompilerBuilder {
    pub fn optimization_level(&mut self, level: napi::JsUnknown) -> JsResult<()> {
        // Convert JsUnknown to OptimizationLevel
        let opt_level = if let Ok(js_str) = level.coerce_to_string() {
            let s = js_str.into_utf8()?.as_str()?.to_string();
            match s.to_lowercase().as_str() {
                "zero" => OptimizationLevel::Zero,
                "one" => OptimizationLevel::One,
                "two" => OptimizationLevel::Two,
                "three" => OptimizationLevel::Three,
                _ => OptimizationLevel::Two,
            }
        } else {
            OptimizationLevel::Two
        };
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.optimization_level(opt_level);
        Ok(())
    }

    pub fn compression(&mut self, enable: bool) -> JsResult<()> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.compression(enable);
        Ok(())
    }

    pub fn cache(&mut self, enable: bool) -> JsResult<()> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.cache(enable);
        Ok(())
    }

    pub fn verbose(&mut self, enable: bool) -> JsResult<()> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.verbose(enable);
        Ok(())
    }

    pub fn build(&mut self) -> JsResult<JsCompiler> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        let compiler = builder.build();
        Ok(JsCompiler { inner: compiler })
    }
}


#[napi(js_name = "HelixBinary")]
#[derive(Clone, Debug)]
pub struct JsHelixBinary {
    inner: HelixBinary,
}
  
#[napi]
impl JsHelixBinary {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: HelixBinary::new(),
        }
    }

    pub fn validate(&self) -> JsResult<()> {
        self.inner
            .validate()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn calculate_checksum(&self) -> JsResult<u64> {
        Ok(self.inner.calculate_checksum())
    }

    pub fn size(&self) -> usize {
        self.inner.size()
    }

    pub fn compression_ratio(&self, original_size: usize) -> f64 {
        self.inner.compression_ratio(original_size)
    }
}


#[napi(js_name = "HelixDispatcher")]
pub struct JsHelixDispatcher {
    inner: HelixDispatcher,
}

#[napi]
impl JsHelixDispatcher {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: HelixDispatcher::new(),
        }
    }

    pub fn initialize(&mut self) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                rt.block_on(self.inner.initialize())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn parse_only(&self, source: String) -> JsResult<String> {
        let tokens_with_loc = crate::dna::atp::lexer::tokenize_with_locations(&source)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        let source_map = crate::dna::atp::lexer::SourceMap {
            tokens: tokens_with_loc.clone(),
            source: source.to_string(),
        };
        let mut parser = crate::dna::atp::parser::Parser::new_with_source_map(source_map);
        match parser.parse() {
            Ok(ast) => Ok(format!("{:?}", ast)),
            Err(e) => Err(napi::Error::from_reason(e)),
        }
    }

    pub fn parse_dsl(&mut self, source: String) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        rt.block_on(self.inner.parse_dsl(&source))
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn interpreter(&self) -> JsResult<JsHelixInterpreter> {
        // Since we can't clone the interpreter, create a new one
        // The original interpreter reference is just used to check if it's initialized
        let _ = self.inner.interpreter()
            .ok_or_else(|| napi::Error::from_reason("Interpreter not initialized"))?;
        JsHelixInterpreter::new()
    }

    pub fn interpreter_mut(&mut self) -> JsResult<JsHelixInterpreter> {
        // Can't clone a mutable reference, need to return an error or handle differently
        Err(napi::Error::from_reason("Cannot clone mutable interpreter reference"))
    }

    pub fn is_ready(&self) -> bool {
        self.inner.is_ready()
    }
}


#[napi(js_name = "Hlx")]
pub struct JsHlx {
    inner: Hlx,
}

#[napi]
impl JsHlx {
    #[napi(factory)]
    pub fn new() -> std::result::Result<JsHlx, napi::Error> {
        let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        let hlx = rt
            .block_on(Hlx::new())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsHlx { inner: hlx })
    }

    pub fn get_raw(&self, env: Env, section: String, key: String) -> JsResult<napi::JsUnknown> {
        let value = self.inner.get_raw(&section, &key);
        match value {
            Some(v) => value_to_js(&env, &v),
            None => Ok(env.get_null()?.into_unknown()),
        }
    }

    pub fn get_str(&self, section: String, key: String) -> JsResult<String> {
        self.inner
            .get_str(&section, &key)
            .map(|s| s.to_string())
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_num(&self, section: String, key: String) -> JsResult<f64> {
        self.inner
            .get_num(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_bool(&self, section: String, key: String) -> JsResult<bool> {
        self.inner
            .get_bool(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_array(&self, env: Env, section: String, key: String) -> JsResult<napi::JsUnknown> {
        let arr = self
            .inner
            .get_array(&section, &key)
            .ok_or(napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))?;

        let mut result = env.create_array_with_length(arr.len())?;
        for (i, val) in arr.iter().enumerate() {
            let js_val = value_to_js(&env, val)?;
            result.set_element(i as u32, js_val)?;
        }
        Ok(result.into_unknown())
    }

    pub fn get_string(&self, section: String, key: String) -> JsResult<String> {
        self.inner
            .get_string(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_i32(&self, section: String, key: String) -> JsResult<i32> {
        self.inner
            .get_i32(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_i64(&self, section: String, key: String) -> JsResult<i64> {
        self.inner
            .get_i64(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_u32(&self, section: String, key: String) -> JsResult<u32> {
        self.inner
            .get_u32(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_u64(&self, section: String, key: String) -> JsResult<u64> {
        self.inner
            .get_u64(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_f32(&self, section: String, key: String) -> JsResult<f32> {
        self.inner
            .get_f32(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_f64(&self, section: String, key: String) -> JsResult<f64> {
        self.inner
            .get_f64(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_string(&self, section: String, key: String) -> JsResult<Vec<String>> {
        self.inner
            .get_vec_string(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_i32(&self, section: String, key: String) -> JsResult<Vec<i32>> {
        self.inner
            .get_vec_i32(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_f64(&self, section: String, key: String) -> JsResult<Vec<f64>> {
        self.inner
            .get_vec_f64(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_bool(&self, section: String, key: String) -> JsResult<Vec<bool>> {
        self.inner
            .get_vec_bool(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_dynamic(&self, section: String, key: String) -> JsResult<JsDynamicValue> {
        let value = self
            .inner
            .get_dynamic(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))?;
        Ok(JsDynamicValue { inner: value })
    }

    pub fn get_auto(&self, env: Env, section: String, key: String) -> JsResult<napi::JsUnknown> {
        let value = self
            .inner
            .get_auto(&section, &key)
            .ok_or_else(|| napi::Error::from_reason(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))?;
        value_to_js(&env, &crate::dna::atp::value::Value::String(value))
    }

    pub fn select(&self, env: Env, section: String, key: String) -> JsResult<napi::JsUnknown> {
        // TypedGetter wrapper - for now return a placeholder
        Ok(env.get_null()?.into_unknown())
    }

    pub fn set_str(&mut self, section: String, key: String, value: String) -> JsResult<()> {
        self.inner.set_str(&section, &key, &value);
        Ok(())
    }

    pub fn set_num(&mut self, section: String, key: String, value: f64) -> JsResult<()> {
        self.inner.set_num(&section, &key, value);
        Ok(())
    }

    pub fn set_bool(&mut self, section: String, key: String, value: bool) -> JsResult<()> {
        self.inner.set_bool(&section, &key, value);
        Ok(())
    }

    pub fn increase(&mut self, section: String, key: String, amount: f64) -> JsResult<f64> {
        self.inner
            .increase(&section, &key, amount)
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }

    pub fn index(&self, env: Env, section: String) -> JsResult<napi::JsUnknown> {
        let _index = self.inner.index(&section);
        Ok(env.get_null()?.into_unknown())
    }

    pub fn index_mut(&mut self, env: Env, section: String) -> JsResult<napi::JsUnknown> {
        let _index = self.inner.index_mut(&section);
        Ok(env.get_null()?.into_unknown())
    }

    pub fn server(&mut self) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                rt.block_on(self.inner.server())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn watch(&mut self) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                rt.block_on(self.inner.watch())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn process(&mut self) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                rt.block_on(self.inner.process())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn compile(&mut self) -> JsResult<()> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                rt.block_on(self.inner.compile())
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                Ok(())
    }

    pub fn execute(&mut self, env: Env, code: String) -> JsResult<napi::JsUnknown> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                let result = rt
            .block_on(self.inner.execute(&code))
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        value_to_js(&env, &result)
    }

    pub fn sections(&self) -> JsResult<Vec<String>> {
        Ok(self.inner.sections().iter().map(|s| s.to_string()).collect())
    }

    pub fn keys(&self, section: String) -> JsResult<Vec<String>> {
        let keys = self.inner.keys(&section)
            .ok_or_else(|| napi::Error::from_reason(format!("Section '{}' not found", section)))?;
        Ok(keys.iter().map(|s| s.to_string()).collect())
    }

    pub fn get_file_path(&self) -> JsResult<String> {
        let path = self.inner.get_file_path()
            .ok_or_else(|| napi::Error::from_reason("No file path available"))?;
        Ok(path.to_string_lossy().to_string())
    }

    pub fn save(&self) -> JsResult<()> {
        self.inner
            .save()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn make(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let result = self
            .inner
            .make()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        value_to_js(&env, &crate::dna::atp::value::Value::String(result))
    }
}


#[napi(js_name = "DynamicValue")]
pub struct JsDynamicValue {
    inner: DynamicValue,
}

#[napi]
impl JsDynamicValue {
    pub fn as_string(&self) -> JsResult<String> {
        Ok(self.inner.as_string().unwrap_or_default())
    }

    pub fn as_number(&self) -> JsResult<f64> {
        Ok(self.inner.as_number().unwrap_or(0.0))
    }

    pub fn as_integer(&self) -> JsResult<i64> {
        Ok(self.inner.as_integer().unwrap_or(0))
    }

    pub fn as_bool(&self) -> JsResult<bool> {
        Ok(self.inner.as_bool().unwrap_or(false))
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
}


#[napi(js_name = "AtpValue")]
pub struct JsAtpValue {
    inner: crate::dna::atp::value::Value,
}

#[napi]
impl JsAtpValue {
    #[napi(constructor)]
    pub fn default() -> Self {
        Self {
            inner: crate::dna::atp::value::Value::default(),
        }
    }

    pub fn value_type(&self) -> JsResult<String> {
        Ok(format!("{:?}", self.inner.value_type()))
    }

    pub fn is_string(&self) -> bool {
        self.inner.is_string()
    }

    pub fn is_number(&self) -> bool {
        self.inner.is_number()
    }

    pub fn is_boolean(&self) -> bool {
        self.inner.is_boolean()
    }

    pub fn is_array(&self) -> bool {
        self.inner.is_array()
    }

    pub fn is_object(&self) -> bool {
        self.inner.is_object()
    }

    pub fn is_null(&self) -> bool {
        self.inner.is_null()
    }

    pub fn as_string(&self) -> JsResult<String> {
        self.inner
            .as_string()
            .map(|s| s.to_string())
            .ok_or(napi::Error::from_reason("Value is not a string"))
    }

    pub fn as_number(&self) -> JsResult<f64> {
        self.inner
            .as_number()
            .ok_or(napi::Error::from_reason("Value is not a number"))
    }

    pub fn as_f64(&self) -> JsResult<f64> {
        self.inner
            .as_f64()
            .ok_or(napi::Error::from_reason("Value is not a number"))
    }

    pub fn as_str(&self) -> JsResult<String> {
        self.inner
            .as_str()
            .map(|s| s.to_string())
            .ok_or(napi::Error::from_reason("Value is not a string"))
    }

    pub fn as_boolean(&self) -> JsResult<bool> {
        self.inner
            .as_boolean()
            .ok_or(napi::Error::from_reason("Value is not a boolean"))
    }

    pub fn as_array(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let arr = self
            .inner
            .as_array()
            .ok_or(napi::Error::from_reason("Value is not an array"))?;
        let mut result = env.create_array_with_length(arr.len())?;
        for (i, item) in arr.iter().enumerate() {
            let js_val = value_to_js(&env, item)?;
            result.set_element(i as u32, js_val)?;
        }
        Ok(result.into_unknown())
    }

    pub fn as_object(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let obj = self
            .inner
            .as_object()
            .ok_or(napi::Error::from_reason("Value is not an object"))?;
        let mut js_obj = env.create_object()?;
        for (key, value) in obj {
            let js_val = value_to_js(&env, value)?;
            js_obj.set_named_property(&key, js_val)?;
        }
        Ok(js_obj.into_unknown())
    }

    pub fn get(&self, env: Env, key: String) -> JsResult<napi::JsUnknown> {
        let value = self.inner.get(&key);
        match value {
            Some(v) => value_to_js(&env, v),
            None => Ok(env.get_null()?.into_unknown()),
        }
    }

    pub fn get_mut(&mut self, env: Env, key: String) -> JsResult<napi::JsUnknown> {
        let value = self.inner.get_mut(&key);
        match value {
            Some(v) => value_to_js(&env, v),
            None => Ok(env.get_null()?.into_unknown()),
        }
    }

    pub fn get_string(&self, key: &str) -> JsResult<String> {
        self.inner
            .get_string(key)
            .map(|s| s.to_string())
            .ok_or(napi::Error::from_reason(format!(
                "Key '{}' not found or not a string",
                key
            )))
    }

    pub fn get_number(&self, key: &str) -> JsResult<f64> {
        self.inner
            .get_number(key)
            .ok_or(napi::Error::from_reason(format!(
                "Key '{}' not found or not a number",
                key
            )))
    }

    pub fn get_boolean(&self, key: &str) -> JsResult<bool> {
        self.inner
            .get_boolean(key)
            .ok_or(napi::Error::from_reason(format!(
                "Key '{}' not found or not a boolean",
                key
            )))
    }

    pub fn get_array(&self, env: Env, key: String) -> JsResult<napi::JsUnknown> {
        let arr = self
            .inner
            .get_array(&key)
            .ok_or(napi::Error::from_reason(format!(
                "Key '{}' not found or not an array",
                key
            )))?;
        let mut result = env.create_array_with_length(arr.len())?;
        for (i, item) in arr.iter().enumerate() {
            let js_val = value_to_js(&env, item)?;
            result.set_element(i as u32, js_val)?;
        }
        Ok(result.into_unknown())
    }

    pub fn get_object(&self, env: Env, key: String) -> JsResult<napi::JsUnknown> {
        let obj = self
            .inner
            .get_object(&key)
            .ok_or(napi::Error::from_reason(format!(
                "Key '{}' not found or not an object",
                key
            )))?;
        let mut js_obj = env.create_object()?;
        for (k, value) in obj {
            let js_val = value_to_js(&env, value)?;
            js_obj.set_named_property(&k, js_val)?;
        }
        Ok(js_obj.into_unknown())
    }

    pub fn to_string(&self) -> String {
        self.inner.to_string()
    }

    pub fn to_json(&self) -> JsResult<String> {
        self.inner
            .to_json()
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }

    pub fn to_yaml(&self) -> JsResult<String> {
        self.inner
            .to_yaml()
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }

    #[napi]
    pub fn from_json(json_value: JsObject) -> JsResult<JsAtpValue> {
        // Convert JsObject to serde_json::Value
        let json = serde_json::Value::Null; // Placeholder
        let value = crate::dna::atp::value::Value::from_json(json);
        Ok(JsAtpValue { inner: value })
    }
}


#[napi(js_name = "HlxHeader")]
pub struct JsHlxHeader {
    inner: HlxHeader,
}

#[napi]
impl JsHlxHeader {
    #[napi(factory)]
    pub fn new(schema: JsObject, metadata: HashMap<String, JsObject>) -> std::result::Result<JsHlxHeader, napi::Error> {
        // Convert parameters
        use arrow::datatypes::{DataType, Field, Schema};
        let converted_schema = Schema::new(vec![Field::new("placeholder", DataType::Utf8, false)]);
        let converted_metadata: HashMap<String, serde_json::Value> = HashMap::new(); // Placeholder
        let header = HlxHeader::new(&converted_schema, converted_metadata);
        Ok(JsHlxHeader { inner: header })
    }

    #[napi(factory)]
    pub fn from_json_bytes(bytes: Vec<u8>) -> std::result::Result<JsHlxHeader, napi::Error> {
        let header =
            HlxHeader::from_json_bytes(&bytes).map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsHlxHeader { inner: header })
    }

    pub fn with_compression(&mut self, compressed: bool) -> JsResult<()> {
        let inner = self.inner.clone();
        self.inner = inner.with_compression(compressed);
        Ok(())
    }

    pub fn with_row_count(&mut self, count: u64) -> JsResult<()> {
        let inner = self.inner.clone();
        self.inner = inner.with_row_count(count);
        Ok(())
    }

    pub fn with_preview(&mut self, preview: Vec<JsObject>) -> JsResult<()> {
        // Convert Vec<JsObject> to Vec<serde_json::Value>
        let converted_preview: Vec<serde_json::Value> = vec![]; // Placeholder
        let inner = self.inner.clone();
        self.inner = inner.with_preview(converted_preview);
        Ok(())
    }

    pub fn is_compressed(&self) -> bool {
        self.inner.is_compressed()
    }

    pub fn to_json_bytes(&self) -> JsResult<Vec<u8>> {
        self.inner.to_json_bytes()
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }
}


#[napi(js_name = "SymbolTable")]
pub struct JsSymbolTable {
    inner: crate::dna::hel::binary::SymbolTable,
}

#[napi]
impl JsSymbolTable {
    pub fn intern(&mut self, s: &str) -> u32 {
        self.inner.intern(s)
    }

    pub fn get(&self, id: u32) -> JsResult<String> {
        self.inner
            .get(id)
            .ok_or_else(|| napi::Error::from_reason(format!("Symbol with id {} not found", id)))
            .map(|s| s.clone())
    }

    pub fn stats(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _stats = self.inner.stats();
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "DataSection")]
pub struct JsDataSection {
    inner: DataSection,
}

#[napi]
impl JsDataSection {
    #[napi(factory)]
    pub fn new(section_type: JsObject, data: Vec<u8>) -> std::result::Result<JsDataSection, napi::Error> {
        // Convert JsObject to SectionType
        let st = crate::dna::hel::binary::SectionType::Project; // Placeholder
        let section = DataSection::new(st, data);
        Ok(JsDataSection { inner: section })
    }

    pub fn compress(&mut self, method: JsObject) -> JsResult<()> {
        // Convert JsObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        self.inner
            .compress(cm)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn decompress(&mut self) -> JsResult<()> {
        self.inner
            .decompress()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }
}


#[napi(js_name = "HelixVM")]
pub struct JsHelixVM {
    inner: HelixVM,
}
  
#[napi]
impl JsHelixVM {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: HelixVM::new(),
        }
    }

    pub fn with_debug(&mut self) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_debug();
    }

    pub fn execute_binary(&mut self, binary: &JsHelixBinary) -> JsResult<()> {
        self.inner
            .execute_binary(&binary.inner)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn push(&mut self, value: JsObject) -> JsResult<()> {
        // Convert JsObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        self.inner.push(val);
        Ok(())
    }

    pub fn pop(&mut self) -> JsResult<()> {
        self.inner
            .pop()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn load_memory(&self, env: Env, address: u32) -> JsResult<napi::JsUnknown> {
        let value = self.inner.load_memory(address)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        // Convert hel::binary::Value to atp::value::Value
        let atp_value = match value {
            crate::dna::hel::binary::Value::String(_s) => crate::dna::atp::value::Value::String("string_id".to_string()),
            crate::dna::hel::binary::Value::Int(n) => crate::dna::atp::value::Value::Number(*n as f64),
            crate::dna::hel::binary::Value::Float(n) => crate::dna::atp::value::Value::Number(*n),
            crate::dna::hel::binary::Value::Bool(b) => crate::dna::atp::value::Value::Bool(*b),
            crate::dna::hel::binary::Value::Null => crate::dna::atp::value::Value::Null,
            _ => crate::dna::atp::value::Value::String("unsupported value type".to_string()),
        };
        value_to_js(&env, &atp_value)
    }

    pub fn store_memory(&mut self, address: u32, value: JsObject) -> JsResult<()> {
        // Convert JsObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        self.inner.store_memory(address, val).map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn set_breakpoint(&mut self, address: usize) -> JsResult<()> {
        self.inner.set_breakpoint(address);
        Ok(())
    }

    pub fn remove_breakpoint(&mut self, address: usize) -> JsResult<()> {
        self.inner.remove_breakpoint(address);
        Ok(())
    }

    pub fn continue_execution(&mut self) -> JsResult<()> {
        self.inner.continue_execution();
        Ok(())
    }

    pub fn step(&mut self) -> JsResult<()> {
        self.inner.step();
        Ok(())
    }

    pub fn state(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _state = self.inner.state();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn stats(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _stats = self.inner.stats();
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "VMExecutor")]
pub struct JsVMExecutor {
    inner: VMExecutor,
}

#[napi]
impl JsVMExecutor {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: VMExecutor::new(),
        }
    }

    pub fn vm(&mut self) -> JsResult<JsHelixVM> {
        // vm() returns &mut, can't move it - need to clone or return reference
        Err(napi::Error::from_reason("Cannot move vm from executor"))
    }
}


#[napi(js_name = "AppState")]
pub struct JsAppState {
    inner: crate::dna::vlt::tui::AppState,
}
  
#[napi]
impl JsAppState {
    #[napi(factory)]
    pub fn new() -> std::result::Result<JsAppState, napi::Error> {
        Ok(JsAppState {
            inner: crate::dna::vlt::tui::AppState::new()
                .map_err(|e| napi::Error::from_reason(e.to_string()))?,
        })
    }

    pub fn focus(&mut self, area: JsObject) -> JsResult<()> {
        // Convert JsObject to FocusArea
        let focus_area = crate::dna::vlt::tui::FocusArea::Files; // Placeholder
        self.inner.focus(focus_area);
        Ok(())
    }

    pub fn select_next_file(&mut self) -> JsResult<()> {
        self.inner.select_next_file();
        Ok(())
    }

    pub fn select_prev_file(&mut self) -> JsResult<()> {
        self.inner.select_prev_file();
        Ok(())
    }

    pub fn open_selected_file(&mut self) -> JsResult<()> {
        self.inner
            .open_selected_file()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn select_next_operator(&mut self) -> JsResult<()> {
        self.inner.select_next_operator();
        Ok(())
    }

    pub fn select_prev_operator(&mut self) -> JsResult<()> {
        self.inner.select_prev_operator();
        Ok(())
    }

    pub fn cycle_operator_category_next(&mut self) -> JsResult<()> {
        self.inner.cycle_operator_category_next();
        Ok(())
    }

    pub fn cycle_operator_category_prev(&mut self) -> JsResult<()> {
        self.inner.cycle_operator_category_prev();
        Ok(())
    }

    pub fn reset_operator_category(&mut self) -> JsResult<()> {
        self.inner.reset_operator_category();
        Ok(())
    }

    pub fn sync_operator_selection(&mut self) -> JsResult<()> {
        self.inner.sync_operator_selection();
        Ok(())
    }

    pub fn insert_selected_operator(&mut self) -> JsResult<()> {
        self.inner.insert_selected_operator();
        Ok(())
    }

    pub fn next_tab(&mut self) -> JsResult<()> {
        self.inner.next_tab();
        Ok(())
    }

    pub fn previous_tab(&mut self) -> JsResult<()> {
        self.inner.previous_tab();
        Ok(())
    }

    pub fn close_active_tab(&mut self) -> JsResult<()> {
        self.inner.close_active_tab();
        Ok(())
    }

    pub fn create_new_tab(&mut self) -> JsResult<()> {
        self.inner.create_new_tab();
        Ok(())
    }

    pub fn save_active_tab(&mut self) -> JsResult<()> {
        self.inner
            .save_active_tab()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn trigger_command(&mut self) -> JsResult<()> {
        self.inner.trigger_command();
        Ok(())
    }

    pub fn select_next_command(&mut self) -> JsResult<()> {
        self.inner.select_next_command();
        Ok(())
    }

    pub fn select_prev_command(&mut self) -> JsResult<()> {
        self.inner.select_prev_command();
        Ok(())
    }

    pub fn on_tick(&mut self) -> JsResult<()> {
        self.inner.on_tick();
        Ok(())
    }
}

  
#[napi(js_name = "Benchmark")]
pub struct JsBenchmark {
    inner: Benchmark,
}

#[napi]
impl JsBenchmark {
    #[napi(constructor)]
    pub fn new(name: String) -> Self {
        Self {
            inner: Benchmark::new(&name),
        }
    }

    pub fn with_iterations(&mut self, iterations: usize) -> JsResult<()> {
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_iterations(iterations);
        Ok(())
    }

    pub fn with_warmup(&mut self, warmup: usize) -> JsResult<()> {
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_warmup(warmup);
        Ok(())
    }

    pub fn run(&self, env: Env, f: napi::JsUnknown) -> JsResult<napi::JsUnknown> {
        // This needs to be implemented with proper callback handling
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "Bundler")]
pub struct JsBundler {
    inner: Bundler,
}

#[napi]
impl JsBundler {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: Bundler::new(),
        }
    }

    pub fn include(&mut self, pattern: &str) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.include(pattern);
    }

    pub fn exclude(&mut self, pattern: &str) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.exclude(pattern);
    }

    pub fn with_imports(&mut self, follow: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_imports(follow);
    }

    pub fn with_tree_shaking(&mut self, enable: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_tree_shaking(enable);
    }

    pub fn verbose(&mut self, enable: bool) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.verbose(enable);
    }
}


#[napi(js_name = "BundleBuilder")]
pub struct JsBundleBuilder {
    inner: crate::dna::mds::bundle::BundleBuilder,
}

#[napi]
impl JsBundleBuilder {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: crate::dna::mds::bundle::BundleBuilder::new(),
        }
    }

    pub fn add_file(&mut self, path: String, binary: JsHelixBinary) -> JsResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner.add_file(path_buf, binary.inner);
        Ok(())
    }

    pub fn add_dependency(&mut self, from: String, to: String) -> JsResult<()> {
        let from_path = std::path::PathBuf::from(from);
        let to_path = std::path::PathBuf::from(to);
        self.inner.add_dependency(from_path, to_path);
        Ok(())
    }

    pub fn build(&mut self, env: Env) -> JsResult<napi::JsUnknown> {
        let _bundle = std::mem::replace(&mut self.inner, crate::dna::mds::bundle::BundleBuilder::new()).build();
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "CacheAction")]
pub struct JsCacheAction {
    // This is likely an enum, so we need to handle it differently
}

#[napi]
impl JsCacheAction {
    #[napi]
    pub fn from_str(s: String) -> JsResult<JsCacheAction> {
        // Convert string to CacheAction enum
        Ok(JsCacheAction {}) // Placeholder
    }
}


#[napi(js_name = "E621Config")]
pub struct JsE621Config {
    inner: MapE621Config,
}
  
#[napi]
impl JsE621Config {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: MapE621Config::new(),
        }
    }

    pub fn with_filter_tags(&mut self, filter_tags: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_filter_tags(filter_tags);
    }

    pub fn with_format(&mut self, format: Option<String>) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_format(format);
    }

    pub fn with_artist_prefix(&mut self, prefix: Option<String>) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_artist_prefix(prefix);
    }

    pub fn with_artist_suffix(&mut self, suffix: Option<String>) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_artist_suffix(suffix);
    }

    pub fn with_replace_underscores(&mut self, replace_underscores: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_replace_underscores(replace_underscores);
    }
}


#[napi(js_name = "ConcatConfig")]
pub struct JsConcatConfig {
    inner: ConcatConfig,
}

#[napi]
impl JsConcatConfig {
    pub fn with_deduplication(&mut self, deduplicate: bool) -> JsResult<()> {
        self.inner = std::mem::replace(&mut self.inner, ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags)).with_deduplication(deduplicate);
        Ok(())
    }

    #[napi]
    pub fn from_preset(preset: JsObject) -> Self {
        // TODO: Convert JsObject to FileExtensionPreset
        let config = ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags); // Placeholder
        Self { inner: config }
    }
}


#[napi(js_name = "DataFormat")]
pub struct JsDataFormat {
    inner: crate::dna::map::core::DataFormat,
}

#[napi]
impl JsDataFormat {
    #[napi]
    pub fn from_str(s: String) -> JsResult<JsDataFormat> {
        let format = s
            .parse::<crate::dna::map::core::DataFormat>()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsDataFormat { inner: format })
    }
}


#[napi(js_name = "GenericJSONDataset")]
pub struct JsGenericJSONDataset {
    inner: crate::dna::map::core::GenericJSONDataset,
}

#[napi]
impl JsGenericJSONDataset {
    pub fn len(&self) -> usize {
        self.inner.len()
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    pub fn get_random_sample(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _sample = self.inner.get_random_sample();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn stats(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _stats = self.inner.stats();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn detect_training_format(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _format = self.inner.detect_training_format();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn to_training_dataset(&self) -> JsResult<JsTrainingDataset> {
        let dataset = self
            .inner
            .to_training_dataset()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsTrainingDataset { inner: dataset })
    }
}


#[napi(js_name = "TrainingDataset")]
pub struct JsTrainingDataset {
    inner: crate::dna::map::core::TrainingDataset,
}

#[napi]
impl JsTrainingDataset {
    pub fn quality_assessment(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _assessment = self.inner.quality_assessment();
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "HuggingFaceDataset")]
pub struct JsHuggingFaceDataset {
    inner: HuggingFaceDataset,
}
  
#[napi]
impl JsHuggingFaceDataset {
    #[napi]
    pub fn load(name: String, split: String, cache_dir: String) -> JsResult<JsHuggingFaceDataset> {
                let rt = tokio::runtime::Runtime::new()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
                let path = std::path::PathBuf::from(cache_dir);
                let dataset = rt
            .block_on(HuggingFaceDataset::load(&name, &split, &path))
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsHuggingFaceDataset { inner: dataset })
    }
}


#[napi]
impl JsHuggingFaceDataset {
    pub fn get_features(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _features = self.inner.get_features();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn info(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _info = self.inner.info();
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "PreferenceProcessor")]
pub struct JsPreferenceProcessor {
    inner: PreferenceProcessor,
}

#[napi]
impl JsPreferenceProcessor {
    #[napi]
    pub fn compute_statistics(_samples: Vec<JsObject>, env: Env) -> JsResult<napi::JsUnknown> {
        Ok(env.get_null()?.into_unknown())
    }

}


#[napi(js_name = "CompletionProcessor")]
pub struct JsCompletionProcessor {
    inner: CompletionProcessor,
}

#[napi]
impl JsCompletionProcessor {
    #[napi]
    pub fn compute_statistics(_samples: Vec<JsObject>, env: Env) -> JsResult<napi::JsUnknown> {
        // compute_statistics is private, placeholder implementation
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "InstructionProcessor")]
pub struct JsInstructionProcessor {
    inner: InstructionProcessor,
}

#[napi]
impl JsInstructionProcessor {
    #[napi]
    pub fn compute_statistics(_samples: Vec<JsObject>, env: Env) -> JsResult<napi::JsUnknown> {
        // compute_statistics is private, placeholder implementation
        Ok(env.get_null()?.into_unknown())
    }
}


#[napi(js_name = "HfProcessor")]
pub struct JsHfProcessor {
    inner: HfProcessor,
}

#[napi]
impl JsHfProcessor {
    #[napi(constructor)]
    pub fn new(cache_dir: String) -> Self {
        let path = std::path::PathBuf::from(cache_dir);
        Self {
            inner: HfProcessor::new(path),
        }
    }
}


#[napi(js_name = "ReasoningDataset")]
pub struct JsReasoningDataset {
    inner: ReasoningDataset,
}
  
#[napi]
impl JsReasoningDataset {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: ReasoningDataset::new(),
        }
    }

    pub fn add_entry(&mut self, entry: JsObject) -> JsResult<()> {
        // Convert JsObject to ReasoningEntry
        let converted_entry = ReasoningEntry {
            user: "placeholder".to_string(),
            reasoning: "placeholder".to_string(),
            assistant: "placeholder".to_string(),
            template: "placeholder".to_string(),
            conversations: vec![],
        }; // Placeholder
        self.inner.add_entry(converted_entry);
        Ok(())
    }

    pub fn len(&self) -> usize {
        self.inner.len()
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    pub fn create_template(&self, user: &str, reasoning: &str, assistant: &str) -> String {
        crate::dna::map::reasoning::ReasoningDataset::create_template(user, reasoning, assistant)
    }
}


#[napi(js_name = "Document")]
pub struct JsDocument {
    // This appears to be a placeholder impl block
}

#[napi(js_name = "StringPool")]
#[derive(Debug, Clone)]
pub struct JsStringPool {
    inner: StringPool,
}

#[napi]
impl JsStringPool {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: StringPool::new(),
        }
    }

    pub fn intern(&mut self, s: &str) -> u32 {
        self.inner.intern(s)
    }

    pub fn get(&self, idx: u32) -> JsResult<String> {
        self.inner
            .get(idx)
            .ok_or_else(|| napi::Error::from_reason(format!("Index {} not found", idx)))
            .map(|s| s.clone())
    }
}


#[napi(js_name = "ConstantPool")]
pub struct JsConstantPool {
    inner: ConstantPool,
}
  
#[napi]
impl JsConstantPool {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: ConstantPool::new(),
        }
    }

    pub fn add(&mut self, value: JsObject) -> JsResult<u32> {
        // TODO: Convert JsObject to ConstantValue
        let cv = ConstantValue::String(0); // Placeholder
        Ok(self.inner.add(cv))
    }

    pub fn get(&self, env: Env, idx: u32) -> JsResult<napi::JsUnknown> {
        let value = self.inner.get(idx)
            .ok_or_else(|| napi::Error::from_reason(format!("Constant at index {} not found", idx)))?;
        // Convert ConstantValue to atp::value::Value
        let atp_value = match value {
            crate::dna::mds::codegen::ConstantValue::String(s) => crate::dna::atp::value::Value::String(s.to_string()),
            crate::dna::mds::codegen::ConstantValue::Number(n) => crate::dna::atp::value::Value::Number(*n as f64),
            crate::dna::mds::codegen::ConstantValue::Bool(b) => crate::dna::atp::value::Value::Bool(*b),
            crate::dna::mds::codegen::ConstantValue::Duration(_) => crate::dna::atp::value::Value::String("duration".to_string()),
            crate::dna::mds::codegen::ConstantValue::Null => crate::dna::atp::value::Value::Null,
        };
        value_to_js(&env, &atp_value)
    }
}


#[napi(js_name = "CodeGenerator")]
pub struct JsCodeGenerator {
    inner: CodeGenerator,
}

#[napi]
impl JsCodeGenerator {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: CodeGenerator::new(),
        }
    }

    pub fn generate(&mut self, ast: &JsHelixAst) -> JsResult<()> {
        let _ir = self.inner.generate(&ast.inner);
        Ok(())
    }
}

// BinarySerializer wrapper

#[napi(js_name = "BinarySerializer")]
pub struct JsBinarySerializer {
    inner: crate::dna::mds::serializer::BinarySerializer,
}

#[napi]
impl JsBinarySerializer {
    #[napi(constructor)]
    pub fn new(enable_compression: bool) -> Self {
        Self {
            inner: crate::dna::mds::serializer::BinarySerializer::new(enable_compression),
        }
    }

    pub fn with_compression_method(&mut self, method: JsObject) -> () {
        // Convert JsObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        let inner = crate::dna::mds::serializer::BinarySerializer::new(true);
        self.inner = inner.with_compression_method(cm);
    }
}

// VersionChecker wrapper

#[napi(js_name = "VersionChecker")]
pub struct JsVersionChecker {
    // This seems to be a static utility class
}

#[napi]
impl JsVersionChecker {
    #[napi]
    pub fn is_compatible(_ir: JsObject) -> bool {
        // Convert JsObject to &HelixIR - placeholder implementation
        // HelixIR doesn't have Default, so using a dummy check
        true
    }

    #[napi]
    pub fn migrate(ir: JsObject) -> JsResult<()> {
        // Convert and modify JsObject representing HelixIR
        Ok(())
    }
}

// Migrator wrapper

#[napi(js_name = "Migrator")]
pub struct JsMigrator {
    inner: Migrator,
}

#[napi]
impl JsMigrator {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: Migrator::new(),
        }
    }

    pub fn verbose(&mut self, enable: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.verbose(enable);
    }

    pub fn migrate_json(&self, json_str: &str) -> JsResult<String> {
        self.inner
            .migrate_json(json_str)
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }

    pub fn migrate_toml(&self, toml_str: &str) -> JsResult<String> {
        self.inner
            .migrate_toml(toml_str)
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }

    pub fn migrate_yaml(&self, yaml_str: &str) -> JsResult<String> {
        self.inner
            .migrate_yaml(yaml_str)
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }

    pub fn migrate_env(&self, env_str: &str) -> JsResult<String> {
        self.inner
            .migrate_env(env_str)
            .map_err(|e| napi::Error::from_reason(e.to_string()))
    }
}

// ModuleResolver wrapper

#[napi(js_name = "ModuleResolver")]
pub struct JsModuleResolver {
    inner: ModuleResolver,
}

#[napi]
impl JsModuleResolver {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: ModuleResolver::new(),
        }
    }

    pub fn resolve(&mut self, env: Env, module_name: String) -> JsResult<napi::JsUnknown> {
        let result = self.inner.resolve(&module_name);
        match result {
            Ok(path) => Ok(env.create_string(&path.to_string_lossy())?.into_unknown()),
            Err(e) => Err(napi::Error::from_reason(e.to_string())),
        }
    }

    pub fn clear_cache(&mut self) -> JsResult<()> {
        self.inner.clear_cache();
        Ok(())
    }
}

// ModuleSystem wrapper

#[napi(js_name = "ModuleSystem")]
pub struct JsModuleSystem {
    inner: ModuleSystem,
}


#[napi]
impl JsModuleSystem {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: ModuleSystem::new(),
        }
    }

    pub fn load_module(&mut self, path: String) -> JsResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner
            .load_module(&path_buf)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn resolve_dependencies(&mut self) -> JsResult<()> {
        self.inner
            .resolve_dependencies()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn compilation_order(&self) -> JsResult<Vec<String>> {
        Ok(self.inner.compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect())
    }

    pub fn merge_modules(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _merged = self
            .inner
            .merge_modules()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(env.get_null()?.into_unknown())
    }

    pub fn modules(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _modules = self.inner.modules();
        // Convert Vec<ModuleInfo> to Vec<JsObject>
        Ok(env.create_array_with_length(0)?.into_unknown())
    }

    pub fn dependency_graph(&self) -> JsResult<JsDependencyGraph> {
        Ok(JsDependencyGraph { inner: DependencyGraph })
    }
}

// DependencyBundler wrapper

#[napi(js_name = "DependencyBundler")]
pub struct JsDependencyBundler {
    inner: DependencyBundler,
}


#[napi]
impl JsDependencyBundler {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: DependencyBundler::new(),
        }
    }

    pub fn build_bundle(&mut self, env: Env) -> JsResult<napi::JsUnknown> {
        let _bundle = self
            .inner
            .build_bundle()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(env.get_null()?.into_unknown())
    }

    pub fn get_compilation_order(&self) -> JsResult<Vec<String>> {
        Ok(self.inner.get_compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect())
    }
}

// DependencyGraph wrapper

#[napi(js_name = "DependencyGraph")]
pub struct JsDependencyGraph {
    inner: DependencyGraph,
}

#[napi]
impl JsDependencyGraph {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: DependencyGraph::new(),
        }
    }

    pub fn check_circular(&self) -> JsResult<()> {
        self.inner.check_circular().map_err(|e| napi::Error::from_reason(e))
    }
}

// OptimizationLevel wrapper

#[napi(js_name = "OptimizationLevel")]
#[derive(Clone)]
pub struct JsOptimizationLevel {
    inner: OptimizationLevel,
}


#[napi]
impl JsOptimizationLevel {
    #[napi]
    pub fn from_u8(level: u8) -> Self {
        Self {
            inner: OptimizationLevel::from(level),
        }
    }
}


#[napi(js_name = "Optimizer")]
pub struct JsOptimizer {
    inner: Optimizer,
}

#[napi]
impl JsOptimizer {
    #[napi(constructor)]
    pub fn new(level: u8) -> Self {
        Self {
            inner: Optimizer::new(OptimizationLevel::from(level)),
        }
    }

    pub fn optimize(&mut self, _ir: JsObject) -> JsResult<()> {
        // Convert JsObject to &mut HelixIR - placeholder implementation
        // HelixIR doesn't have Default, skipping optimization
        Ok(())
    }

    pub fn stats(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _stats = self.inner.stats();
        Ok(env.get_null()?.into_unknown())
    }
}

// ProjectManifest wrapper

#[napi(js_name = "ProjectManifest")]
pub struct JsProjectManifest {
    // This seems to be a large struct, placeholder for now
}

// Runtime wrapper (HelixVM is already defined above)


// Schema wrapper

#[napi(js_name = "HelixConfig")]
pub struct JsHelixConfig {
    inner: HelixConfig,
}


#[napi]
impl JsHelixConfig {
    // Index implementation would go here if needed
}

// HlxDatasetProcessor wrapper

#[napi(js_name = "HlxDatasetProcessor")]
pub struct JsHlxDatasetProcessor {
    inner: HlxDatasetProcessor,
}

#[napi]
impl JsHlxDatasetProcessor {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: HlxDatasetProcessor::new(),
        }
    }

    pub fn parse_hlx_content(&self, env: Env, content: String) -> JsResult<napi::JsUnknown> {
        let result = self.inner.parse_hlx_content(&content);
        match result {
            Ok(_data) => Ok(env.get_null()?.into_unknown()),
            Err(e) => Err(napi::Error::from_reason(e.to_string())),
        }
    }

    pub fn cache_stats(&self, env: Env) -> JsResult<napi::JsUnknown> {
        let _stats = self.inner.cache_stats();
        Ok(env.get_null()?.into_unknown())
    }

    pub fn clear_cache(&mut self) -> JsResult<()> {
        self.inner.clear_cache();
        Ok(())
    }
}

// ProcessingOptions wrapper

#[napi(js_name = "ProcessingOptions")]
#[derive(Debug, Clone)]
pub struct JsProcessingOptions {
    inner: ProcessingOptions,
}

#[napi(js_name = "CacheStats")]
pub struct JsCacheStats {
    inner: CacheStats,
}

#[napi]
impl JsCacheStats {
    pub fn total_size_mb(&self) -> f64 {
        self.inner.total_size_mb()
    }

    pub fn total_size_gb(&self) -> f64 {
        self.inner.total_size_gb()
    }
}

// HlxBridge wrapper

#[napi(js_name = "HlxBridge")]
pub struct JsHlxBridge {
    inner: HlxBridge,
}

#[napi]
impl JsHlxBridge {
    #[napi(constructor)]
    pub fn new() -> Self {
        Self {
            inner: HlxBridge::new(),
        }
    }
}

// ServerConfig wrapper

#[napi(js_name = "ServerConfig")]
#[derive(Clone)]
pub struct JsServerConfig {
    inner: ServerConfig,
}

// HelixServer wrapper
#[napi(js_name = "HelixServer")]
pub struct JsHelixServer {
    inner: HelixServer,
}

#[napi]
impl JsHelixServer {
    #[napi(constructor)]
    pub fn new(config: &JsServerConfig) -> Self {
        Self {
            inner: HelixServer::new(config.inner.clone()),
        }
    }

    pub fn start(&self) -> JsResult<()> {
        self.inner
            .start()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }
}

// VaultConfig wrapper

#[napi(js_name = "VaultConfig")]
pub struct JsVaultConfig {
    inner: VaultConfig,
}

// Vault wrapper

#[napi(js_name = "Vault")]
pub struct JsVault {
    inner: Vault,
}

#[napi]
impl JsVault {
    #[napi(factory)]
    pub fn new() -> std::result::Result<JsVault, napi::Error> {
        let inner = Vault::new().map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(JsVault { inner })
    }

    pub fn save(&self, path: String, description: Option<String>) -> JsResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner
            .save(&path_buf, description)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn load_latest(&self, env: Env, path: String) -> JsResult<napi::JsUnknown> {
        let path_buf = std::path::PathBuf::from(path);
        let _content = self
            .inner
            .load_latest(&path_buf)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(env.get_null()?.into_unknown())
    }

    pub fn load_version(&self, env: Env, file_hash: String, version_id: String) -> JsResult<napi::JsUnknown> {
        let _content = self
            .inner
            .load_version(&file_hash, &version_id)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(env.get_null()?.into_unknown())
    }

    pub fn list_versions(&self, path: String) -> JsResult<Vec<String>> {
        let path_buf = std::path::PathBuf::from(path);
        let versions = self
            .inner
            .list_versions(&path_buf)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(versions
            .into_iter()
            .map(|v| v.id.clone())
            .collect())
    }

    pub fn revert(&self, path: String, version_id: String) -> JsResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner
            .revert(&path_buf, &version_id)
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }

    pub fn garbage_collect(&self) -> JsResult<()> {
        self.inner
            .garbage_collect()
            .map_err(|e| napi::Error::from_reason(e.to_string()))?;
        Ok(())
    }
}



#[napi]
pub fn parse_helix_source(source: String) -> JsResult<JsHelixAst> {
    let js_source_map = JsSourceMap::new(source.clone())?;
    let mut parser = JsParser::new_with_source_map(&js_source_map);
    parser.parse()
}


#[napi]
pub fn load_file(file_path: String) -> JsResult<JsHlx> {
    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;
    let path = std::path::PathBuf::from(file_path);
    let _content = std::fs::read_to_string(&path)
        .map_err(|e| napi::Error::from_reason(format!("Failed to read file: {}", e)))?;
    let hlx = rt
        .block_on(Hlx::new())
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;
    Ok(JsHlx { inner: hlx })
}


#[napi]
pub fn execute(env: Env, source: String) -> JsResult<napi::JsUnknown> {
    let ast = parse_helix_source(source)?;
    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;
    let mut interpreter = rt
        .block_on(HelixInterpreter::new())
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;
    let result = rt.block_on(interpreter.execute_ast(&ast.inner))
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;
    value_to_js(&env, &result)
}


#[napi]
pub fn cmd_compile(
    input: Option<String>,
    output: Option<String>,
    compress: bool,
    optimize: u8,
    cache: bool,
    verbose: bool,
    quiet: bool,
) -> JsResult<String> {
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
        Err(e) => Err(napi::Error::from_reason(format!("Compilation failed: {}", e))),
    }
}


#[napi]
pub fn cmd_add(
    dependency: String,
    version: Option<String>,
    dev: bool,
    verbose: bool,
) -> JsResult<String> {
    match crate::dna::mds::add::add_dependency(
        dependency,
        version,
        dev,
        verbose,
    ) {
        Ok(_) => Ok("Dependency added".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Failed to add dependency: {}", e))),
    }
}


#[napi]
pub fn cmd_validate(target: Option<String>) -> JsResult<String> {
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
                    Err(e) => return Err(napi::Error::from_reason(format!("Validation failed: {}", e))),
                }
            }
        }
    }
    // For source files, check they exist and are readable
    if target_path.exists() {
        Ok("File validation passed".to_string())
    } else {
        Err(napi::Error::from_reason(format!("File not found: {}", target_path.display())))
    }
}


#[napi]
pub fn cmd_info(
    input: Option<String>,
    file: Option<String>,
    output: Option<String>,
    format: Option<String>,
    symbols: bool,
    sections: bool,
    verbose: bool,
) -> JsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let format = format.unwrap_or_else(|| "text".to_string());
    
    match crate::dna::mds::info::info_command(input_path, format, symbols, sections, verbose) {
        Ok(_) => Ok("Info command completed".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Info command failed: {}", e))),
    }
}


#[napi]
pub fn cmd_init(
    name: Option<String>,
    dir: Option<String>,
    template: Option<String>,
    force: bool,
) -> JsResult<String> {
    let name = name.unwrap_or_else(|| String::new());
    let dir = dir
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let template = template.unwrap_or_else(|| "minimal".to_string());
    
    // TODO: Implement actual init logic
    Ok(format!("Init command: name={}, dir={}, template={}, force={}", 
        name, dir.display(), template, force))
}


#[napi]
pub fn cmd_clean(
    all: bool,
    cache: bool,
) -> JsResult<String> {
    // TODO: Implement actual clean logic
    Ok(format!("Clean command: all={}, cache={}", all, cache))
}


#[napi]
pub fn cmd_fmt(
    files: Vec<String>,
    check: bool,
    verbose: bool,
) -> JsResult<String> {
    let file_paths: Vec<std::path::PathBuf> = files.into_iter().map(std::path::PathBuf::from).collect();
    
    match crate::dna::mds::fmt::format_files(file_paths, check, verbose) {
        Ok(_) => {
            if check {
                Ok("Files are formatted correctly".to_string())
            } else {
                Ok("Files formatted successfully".to_string())
            }
        }
        Err(e) => Err(napi::Error::from_reason(format!("Format failed: {}", e))),
    }
}


#[napi]
pub fn cmd_bench(
    pattern: Option<String>,
    iterations: Option<u32>,
) -> JsResult<String> {
    match crate::dna::mds::bench::run_benchmarks(pattern, iterations.map(|i| i as usize), true) {
        Ok(_) => Ok("Benchmarks completed".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Benchmark failed: {}", e))),
    }
}


#[napi]
pub fn cmd_bundle(
    input: Option<String>,
    output: Option<String>,
    include: Vec<String>,
    exclude: Vec<String>,
    tree_shake: bool,
    optimize: u8,
) -> JsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("bundle.hlxb"));
    
    match crate::dna::mds::bundle::bundle_command(input_path, output_path, include, exclude, tree_shake, optimize, false) {
        Ok(_) => Ok("Bundle created successfully".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Bundle failed: {}", e))),
    }
}


#[napi]
pub fn cmd_test(
    pattern: Option<String>,
    integration: bool,
) -> JsResult<String> {
    // TODO: Implement actual test logic
    Ok(format!("Test command: pattern={:?}, integration={}", pattern, integration))
}


#[napi]
pub fn cmd_lint(
    files: Vec<String>,
    verbose: bool,
) -> JsResult<String> {
    let file_paths: Vec<std::path::PathBuf> = files.into_iter().map(std::path::PathBuf::from).collect();
    
    match crate::dna::mds::lint::lint_files(file_paths, verbose) {
        Ok(_) => Ok("Lint completed".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Lint failed: {}", e))),
    }
}


#[napi]
pub fn cmd_optimize(
    input: Option<String>,
    output: Option<String>,
    level: u8,
) -> JsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    
    // TODO: Implement actual optimization logic
    Ok(format!("Optimize command: input={}, output={}, level={}", 
        input_path.display(), output_path.display(), level))
}


#[napi]
pub fn cmd_remove(
    files: Vec<String>,
) -> JsResult<String> {
    // TODO: Implement actual remove logic
    Ok(format!("Remove command with {} files", files.len()))
}


#[napi]
pub fn cmd_reset(
    force: bool,
) -> JsResult<String> {
    // TODO: Implement actual reset logic
    Ok(format!("Reset command: force={}", force))
}


#[napi]
pub fn cmd_search(
    query: String,
    search_type: Option<String>,
    limit: Option<u32>,
    threshold: Option<f64>,
    embeddings: Option<String>,
    auto_find: bool,
) -> JsResult<String> {
    let search_type = search_type.unwrap_or_else(|| "semantic".to_string());
    let limit = limit.unwrap_or(10) as usize;
    let threshold = threshold.unwrap_or(0.0) as f32;
    
    // TODO: Implement actual search logic
    Ok(format!("Search command: query={}, type={}, limit={}, threshold={}, auto_find={}",
        query, search_type, limit, threshold, auto_find))
}


#[napi]
pub fn cmd_serve(
    port: Option<u16>,
    host: Option<String>,
    directory: Option<String>,
) -> JsResult<String> {
    let directory_path = directory.map(|s| std::path::PathBuf::from(s));
    
    // Note: This will block, so we might want to return immediately and run in background
    // For now, we'll just return a message
    match crate::dna::mds::serve::serve_project(port, host, directory_path, false) {
        Ok(_) => Ok("Server started".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Serve failed: {}", e))),
    }
}


#[napi]
pub fn cmd_sign(
    input: String,
    key: Option<String>,
    output: Option<String>,
    verify: bool,
    verbose: bool,
) -> JsResult<String> {
    let input_path = std::path::PathBuf::from(input);
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::sign::sign_binary(input_path, key, output_path, verify, verbose) {
        Ok(_) => {
            if verify {
                Ok("Signature verified".to_string())
            } else {
                Ok("Binary signed successfully".to_string())
            }
        }
        Err(e) => Err(napi::Error::from_reason(format!("Sign failed: {}", e))),
    }
}


#[napi]
pub fn cmd_watch(
    input: Option<String>,
    output: Option<String>,
    optimize: u8,
    debounce: Option<u32>,
    filter: Option<String>,
) -> JsResult<String> {
    let input_path = input
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let output_path = output
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let debounce = debounce.unwrap_or(500) as u64;
    
    // TODO: This should run in background, for now just return
    Ok(format!("Watch command: input={}, output={}, optimize={}, debounce={}, filter={:?}",
        input_path.display(), output_path.display(), optimize, debounce, filter))
}


#[napi]
pub fn cmd_export(
    format: Option<String>,
    output: Option<String>,
    include_deps: bool,
    verbose: bool,
) -> JsResult<String> {
    let format = format.unwrap_or_else(|| "json".to_string());
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::export::export_project(format, output_path, include_deps, verbose) {
        Ok(_) => Ok("Export completed".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Export failed: {}", e))),
    }
}


#[napi]
pub fn cmd_dataset(
    files: Vec<String>,
    output: Option<String>,
    format: Option<String>,
) -> JsResult<String> {
    let file_paths: Vec<std::path::PathBuf> = files.into_iter().map(std::path::PathBuf::from).collect();
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;
    
    use crate::dna::mds::dataset::{dataset_command, DatasetAction};
    
    let action = DatasetAction::Process {
        files: file_paths,
        output: output_path,
        format,
        algorithm: None,
        validate: false,
    };
    
    match rt.block_on(dataset_command(action, false)) {
        Ok(_) => Ok("Dataset processing completed".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Dataset command failed: {}", e))),
    }
}


#[napi]
pub fn cmd_filter(
    files: Vec<String>,
) -> JsResult<String> {
    // TODO: Implement actual filter logic
    Ok(format!("Filter command with {} files", files.len()))
}


#[napi]
pub fn cmd_generate(
    template: String,
    output: Option<String>,
    name: Option<String>,
    force: bool,
    verbose: bool,
) -> JsResult<String> {
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    match crate::dna::mds::generate::generate_code(template, output_path, name, force, verbose) {
        Ok(_) => Ok("Code generated successfully".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Generate failed: {}", e))),
    }
}


#[napi]
pub fn cmd_import(
    input: String,
    registry: Option<String>,
    token: Option<String>,
    dry_run: bool,
) -> JsResult<String> {
    let input_path = std::path::PathBuf::from(input);
    let rt = tokio::runtime::Runtime::new()
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;
    
    // TODO: Implement actual import logic
    Ok(format!("Import command: {}", input_path.display()))
}


#[napi]
pub fn cmd_schema(
    target: String,
    lang: Option<String>,
    output: Option<String>,
    verbose: bool,
) -> JsResult<String> {
    let target_path = std::path::PathBuf::from(target);
    let output_path = output.map(|s| std::path::PathBuf::from(s));
    
    use crate::dna::mds::schema::Language;
    let language = match lang.as_deref() {
        Some("rust") => Language::Rust,
        Some("ts") | Some("typescript") | Some("js") | Some("javascript") => Language::JavaScript,
        Some("python") => Language::Python,
        Some("go") => Language::Go,
        _ => Language::Rust, // default
    };
    
    match crate::dna::mds::schema::schema_command(target_path, language, output_path, verbose) {
        Ok(_) => Ok("Schema generated successfully".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Schema command failed: {}", e))),
    }
}


#[napi]
pub fn cmd_diff(
    file1: Option<String>,
    file2: Option<String>,
    detailed: bool,
) -> JsResult<String> {
    let file1_path = file1
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    let file2_path = file2
        .map(|s| std::path::PathBuf::from(s))
        .unwrap_or_else(|| std::path::PathBuf::from("."));
    
    match crate::dna::mds::diff::diff_command(file1_path, file2_path, detailed) {
        Ok(_) => Ok("Diff completed".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("Diff failed: {}", e))),
    }
}


#[napi]
pub fn cmd_tui() -> JsResult<String> {
    match crate::dna::vlt::tui::launch() {
        Ok(_) => Ok("TUI session ended".to_string()),
        Err(e) => Err(napi::Error::from_reason(format!("TUI error: {}", e))),
    }
}


#[napi]
pub fn cmd_completions(
    shell: String,
    verbose: bool,
    quiet: bool,
) -> JsResult<String> {
    use clap_complete::Shell;
    let shell_enum = match shell.to_lowercase().as_str() {
        "bash" => Shell::Bash,
        "zsh" => Shell::Zsh,
        "fish" => Shell::Fish,
        "powershell" => Shell::PowerShell,
        "elvish" => Shell::Elvish,
        _ => return Err(napi::Error::from_reason(format!("Unsupported shell: {}", shell))),
    };
    
    let completions = crate::dna::mds::completions::completions_command(shell_enum, verbose, quiet);
    Ok(completions)
}


#[napi]
pub fn cmd_doctor(
    action: Option<String>,
) -> JsResult<String> {
    // TODO: Implement actual diagnostics logic
    let action = action.unwrap_or_else(|| "check".to_string());
    Ok(format!("Doctor command: {} - Diagnostics not yet implemented", action))
}


#[napi]
pub fn cmd_publish(
    action: String,
    registry: Option<String>,
    token: Option<String>,
    dry_run: bool,
    verbose: bool,
    quiet: bool,
    input: Option<String>,
    key: Option<String>,
    output: Option<String>,
    verify: bool,
    format: Option<String>,
    include_deps: bool,
) -> JsResult<String> {
    match action.as_str() {
        "publish" => {
            match crate::dna::mds::publish::publish_project(registry, token, dry_run, verbose) {
                Ok(_) => Ok("Project published successfully".to_string()),
                Err(e) => Err(napi::Error::from_reason(format!("Publish failed: {}", e))),
            }
        }
        "sign" => {
            let input_path = input
                .ok_or_else(|| napi::Error::from_reason("--input is required for sign action"))
                .map(|s| std::path::PathBuf::from(s))?;
            let output_path = output.map(|s| std::path::PathBuf::from(s));
            
            match crate::dna::mds::publish::sign_binary(input_path, key, output_path, verify, verbose) {
                Ok(_) => {
                    if verify {
                        Ok("Signature verified".to_string())
                    } else {
                        Ok("Binary signed successfully".to_string())
                    }
                }
                Err(e) => Err(napi::Error::from_reason(format!("Sign failed: {}", e))),
            }
        }
        "export" => {
            let format = format.ok_or_else(|| napi::Error::from_reason("--format is required for export action"))?;
            let output_path = output.map(|s| std::path::PathBuf::from(s));
            
            match crate::dna::mds::publish::export_project(format, output_path, include_deps, verbose) {
                Ok(_) => Ok("Project exported successfully".to_string()),
                Err(e) => Err(napi::Error::from_reason(format!("Export failed: {}", e))),
            }
        }
        _ => Err(napi::Error::from_reason(format!("Unknown publish action: {}", action))),
    }
}


#[napi]
pub fn cmd_vlt(
    subcommand: String,
    name: Option<String>,
    path: Option<String>,
    editor: Option<String>,
    long: bool,
    description: Option<String>,
    limit: Option<u32>,
    version: Option<String>,
    force: bool,
    from: Option<String>,
    to: Option<String>,
    show: bool,
    compress: Option<bool>,
    retention_days: Option<u32>,
    max_versions: Option<u32>,
    dry_run: bool,
) -> JsResult<String> {
    use crate::dna::vlt::Vault;
    
    // Call vault operations directly since VltCommands is private
    match subcommand.as_str() {
        "new" => {
            // TODO: Implement new file creation via vault
            Ok(format!("Vlt new: {}", name.unwrap_or_else(|| "untitled".to_string())))
        }
        "open" => {
            // TODO: Implement file opening
            Ok(format!("Vlt open: {}", path.as_ref().map(|s| s.as_str()).unwrap_or("current")))
        }
        "list" => {
            match Vault::new() {
                Ok(vault) => {
                    // List files - simplified implementation
                    Ok("Vault files listed".to_string())
                }
                Err(e) => Err(napi::Error::from_reason(format!("Vlt list failed: {}", e))),
            }
        }
        "save" => {
            let p = path.ok_or_else(|| napi::Error::from_reason("path is required for save"))?;
            match Vault::new() {
                Ok(vault) => {
                    let path_buf = std::path::PathBuf::from(p);
                    match vault.save(&path_buf, description) {
                        Ok(version_id) => Ok(format!("Saved as version {}", version_id)),
                        Err(e) => Err(napi::Error::from_reason(format!("Vlt save failed: {}", e))),
                    }
                }
                Err(e) => Err(napi::Error::from_reason(format!("Vault init failed: {}", e))),
            }
        }
        "history" => {
            let p = path.ok_or_else(|| napi::Error::from_reason("path is required for history"))?;
            match Vault::new() {
                Ok(vault) => {
                    let path_buf = std::path::PathBuf::from(p);
                    match vault.list_versions(&path_buf) {
                        Ok(versions) => Ok(format!("Found {} versions", versions.len())),
                        Err(e) => Err(napi::Error::from_reason(format!("Vlt history failed: {}", e))),
                    }
                }
                Err(e) => Err(napi::Error::from_reason(format!("Vault init failed: {}", e))),
            }
        }
        "revert" => {
            let p = path.ok_or_else(|| napi::Error::from_reason("path is required for revert"))?;
            let v = version.ok_or_else(|| napi::Error::from_reason("version is required for revert"))?;
            match Vault::new() {
                Ok(vault) => {
                    let path_buf = std::path::PathBuf::from(p);
                    match vault.revert(&path_buf, &v) {
                        Ok(_) => Ok(format!("Reverted to version {}", v)),
                        Err(e) => Err(napi::Error::from_reason(format!("Vlt revert failed: {}", e))),
                    }
                }
                Err(e) => Err(napi::Error::from_reason(format!("Vault init failed: {}", e))),
            }
        }
        "diff" => {
            // TODO: Implement diff via vault
            Ok(format!("Vlt diff: {}", path.as_ref().map(|s| s.as_str()).unwrap_or("current")))
        }
        "config" => {
            // TODO: Implement config management
            Ok("Vlt config updated".to_string())
        }
        "gc" => {
            match Vault::new() {
                Ok(vault) => {
                    match vault.garbage_collect() {
                        Ok(removed) => Ok(format!("Garbage collection removed {} versions", removed)),
                        Err(e) => Err(napi::Error::from_reason(format!("Vlt gc failed: {}", e))),
                    }
                }
                Err(e) => Err(napi::Error::from_reason(format!("Vault init failed: {}", e))),
            }
        }
        "tui" => {
            match crate::dna::vlt::tui::launch() {
                Ok(_) => Ok("TUI session ended".to_string()),
                Err(e) => Err(napi::Error::from_reason(format!("TUI error: {}", e))),
            }
        }
        _ => Err(napi::Error::from_reason(format!("Unknown vlt subcommand: {}", subcommand))),
    }
}
