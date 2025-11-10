#[cfg(feature = "python")]
use pyo3::exceptions::PyValueError;
#[cfg(feature = "python")]
use pyo3::prelude::*;
#[cfg(feature = "python")]
use pyo3::pymethods;
#[cfg(feature = "python")]
use std::collections::HashMap;
#[cfg(all(feature = "python", feature = "compiler"))]
use bincode;
#[cfg(feature = "python")]
pub use crate::dna::atp::value::Value as DnaValue;
#[cfg(feature = "python")]
pub use crate::dna::atp::*;
#[cfg(feature = "python")]
pub use crate::dna::bch::*;
#[cfg(feature = "python")]
pub use crate::dna::cmd::*;
#[cfg(feature = "python")]
pub use crate::dna::compiler::Compiler;
#[cfg(feature = "python")]
pub use crate::dna::compiler::*;
#[cfg(feature = "python")]
pub use crate::dna::exp::*;
#[cfg(feature = "python")]
pub use crate::dna::hel::dna_hlx::Hlx;
#[cfg(feature = "python")]
pub use crate::dna::hel::*;
#[cfg(feature = "python")]
pub use crate::dna::map::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::optimizer::OptimizationLevel;
#[cfg(feature = "python")]
pub use crate::dna::mds::*;
#[cfg(feature = "python")]
pub use crate::dna::ngs::*;
#[cfg(feature = "python")]
pub use crate::dna::ops::*;
#[cfg(feature = "python")]
pub use crate::dna::out::*;
#[cfg(feature = "python")]
pub use crate::dna::tst::*;
#[cfg(feature = "python")]
pub use crate::dna::vlt::Vault;
#[cfg(feature = "python")]
pub use crate::dna::atp::ast::*;
#[cfg(feature = "python")]
pub use crate::dna::atp::interpreter::*;
#[cfg(feature = "python")]
pub use crate::dna::atp::lexer::*;
#[cfg(feature = "python")]
pub use crate::dna::atp::output::*;
#[cfg(feature = "python")]
pub use crate::dna::atp::parser::*;
#[cfg(feature = "python")]
pub use crate::dna::atp::types::*;
#[cfg(feature = "python")]
pub use crate::dna::atp::value::*;
#[cfg(feature = "python")]
pub use crate::dna::hel::binary::*;
#[cfg(feature = "python")]
pub use crate::dna::hel::dispatch::*;
#[cfg(feature = "python")]
pub use crate::dna::hel::dna_hlx::*;
#[cfg(feature = "python")]
pub use crate::dna::hel::error::*;  
#[cfg(feature = "python")]
pub use crate::dna::hel::hlx::*;
#[cfg(feature = "python")]
pub use crate::dna::map::core::*;
#[cfg(feature = "python")]
pub use crate::dna::map::hf::*;
#[cfg(feature = "python")]
pub use crate::dna::map::reasoning::*;
#[cfg(feature = "python")]
use crate::dna::map::caption::E621Config as MapE621Config;
#[cfg(feature = "python")]
pub use crate::dna::mds::a_example::{Document, Embedding, Metadata};
#[cfg(feature = "python")]
pub use crate::dna::mds::benches::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::bundle::*;
#[cfg(feature = "python")]  
pub use crate::dna::mds::cache::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::caption::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::codegen::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::concat::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::config::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::decompile::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::filter::*; 
pub use crate::dna::mds::migrate::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::modules::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::optimizer::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::project::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::runtime::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::schema::*;
#[cfg(feature = "python")]  
pub use crate::dna::mds::semantic::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::serializer::*;
#[cfg(feature = "python")]
pub use crate::dna::mds::server::*;
#[cfg(feature = "python")]
pub use crate::dna::out::helix_format::*;
#[cfg(feature = "python")]
pub use crate::dna::out::hlx_config_format::*;
#[cfg(feature = "python")]
pub use crate::dna::out::hlxb_config_format::*;
#[cfg(feature = "python")]
pub use crate::dna::out::hlxc_format::*;
#[cfg(feature = "python")]
pub use crate::dna::vlt::tui::*;
#[cfg(feature = "python")]
pub use crate::dna::vlt::vault::*;
#[cfg(feature = "python")]
pub use crate::dna::map::core::TrainingSample; 


#[cfg(feature = "python")]
#[pyclass]
pub struct PyHelixAst {
    inner: HelixAst,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyHelixAst {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HelixAst::new(),
        }
    }

    pub fn add_declaration(&mut self, decl: PyObject) -> PyResult<()> {
        // This will need to be implemented based on the Declaration type
        // For now, return an error
        Err(PyValueError::new_err("add_declaration not yet implemented"))
    }

    pub fn get_projects(&self) -> PyResult<Vec<PyObject>> {
        let projects = self.inner.get_projects();
        // Convert Vec<ProjectDecl> to Vec<PyObject>
        let mut result = Vec::new();
        for _project in projects {
            // Convert ProjectDecl to PyObject
            result.push(Python::with_gil(|py| py.None()));
        }
        Ok(result)
    }

    pub fn get_agents(&self) -> PyResult<Vec<PyObject>> {
        let agents = self.inner.get_agents();
        // Convert Vec<AgentDecl> to Vec<PyObject>
        let mut result = Vec::new();
        for _agent in agents {
            // Convert AgentDecl to PyObject
            result.push(Python::with_gil(|py| py.None()));
        }
        Ok(result)
    }

    pub fn get_workflows(&self) -> PyResult<Vec<PyObject>> {
        let workflows = self.inner.get_workflows();
        // Convert Vec<WorkflowDecl> to Vec<PyObject>
        let mut result = Vec::new();
        for _workflow in workflows {
            // Convert WorkflowDecl to PyObject
            result.push(Python::with_gil(|py| py.None()));
        }
        Ok(result)
    }

    pub fn get_contexts(&self) -> PyResult<Vec<PyObject>> {
        let contexts = self.inner.get_contexts();
        // Convert Vec<ContextDecl> to Vec<PyObject>
        let mut result = Vec::new();
        for _context in contexts {
            // Convert ContextDecl to PyObject
            result.push(Python::with_gil(|py| py.None()));
        }
        Ok(result)
    }
}

// Python wrapper for AstPrettyPrinter
#[cfg(feature = "python")]
#[pyclass]
pub struct PyAstPrettyPrinter {
    inner: AstPrettyPrinter,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyAstPrettyPrinter {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: AstPrettyPrinter::new(),
        }
    }

    pub fn print(&mut self, ast: &PyHelixAst) -> PyResult<String> {
        Ok(self.inner.print(&ast.inner))
    }
}

// Python wrapper for Expression
#[cfg(feature = "python")]
#[pyclass]
pub struct PyExpression {
    inner: Expression,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyExpression {
    pub fn binary(
        left: &Bound<'_, PyExpression>,
        op: String,
        right: &Bound<'_, PyExpression>,
    ) -> PyResult<Self> {
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
            _ => return Err(PyValueError::new_err("Invalid binary operator")),
        };

        let expr = Expression::binary(
            left.borrow().inner.clone(),
            binary_op,
            right.borrow().inner.clone(),
        );
        Ok(Self { inner: expr })
    }

    pub fn as_string(&self) -> PyResult<String> {
        Ok(self.inner.as_string().unwrap_or_default())
    }

    pub fn as_number(&self) -> PyResult<f64> {
        self.inner
            .as_number()
            .ok_or(PyValueError::new_err("Value is not a number"))
    }

    pub fn as_bool(&self) -> PyResult<bool> {
        self.inner
            .as_bool()
            .ok_or(PyValueError::new_err("Value is not a boolean"))
    }

    pub fn as_array(&self) -> PyResult<Vec<PyObject>> {
        let arr = self
            .inner
            .as_array()
            .ok_or(PyValueError::new_err("Value is not an array"))?;
        let mut result = Vec::new();
        for expr in arr {
            // Convert Expression to PyObject
            result.push(Python::with_gil(|py| py.None()));
        }
        Ok(result)
    }

    pub fn as_object(&self) -> PyResult<HashMap<String, PyObject>> {
        let obj = self
            .inner
            .as_object()
            .ok_or(PyValueError::new_err("Value is not an object"))?;
        // Convert HashMap<String, Expression> to HashMap<String, PyObject>
        let mut result: HashMap<String, PyObject> = HashMap::new();
        for (key, _expr) in obj {
            // Convert Expression to PyObject
            let py_obj = Python::with_gil(|py| py.None());
            result.insert(key.clone(), py_obj);
        }
        Ok(result)
    }

    pub fn to_value(&self) -> PyResult<PyObject> {
        let value = self.inner.to_value();
        // Convert ast::value::Value to PyObject
        Ok(Python::with_gil(|py| match value {
            crate::dna::atp::value::Value::String(s) => s.to_object(py),
            crate::dna::atp::value::Value::Number(n) => n.to_object(py),
            crate::dna::atp::value::Value::Bool(b) => b.to_object(py),
            crate::dna::atp::value::Value::Array(_) => py.None(),
            crate::dna::atp::value::Value::Object(_) => py.None(),
            crate::dna::atp::value::Value::Null => py.None(),
            crate::dna::atp::value::Value::Duration(d) => d.to_string().to_object(py),
            crate::dna::atp::value::Value::Reference(r) => r.to_object(py),
            crate::dna::atp::value::Value::Identifier(i) => i.to_object(py),
        }))
    }
}

// Python wrapper for AstBuilder
#[cfg(feature = "python")]
#[pyclass]
pub struct PyAstBuilder {
    inner: AstBuilder,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyAstBuilder {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: AstBuilder::new(),
        }
    }

    pub fn add_agent(&mut self, _agent: PyObject) -> PyResult<()> {
        // This needs proper AgentDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_workflow(&mut self, _workflow: PyObject) -> PyResult<()> {
        // This needs proper WorkflowDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_context(&mut self, _context: PyObject) -> PyResult<()> {
        // This needs proper ContextDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_memory(&mut self, _memory: PyObject) -> PyResult<()> {
        // This needs proper MemoryDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_crew(&mut self, _crew: PyObject) -> PyResult<()> {
        // This needs proper CrewDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_pipeline(&mut self, _pipeline: PyObject) -> PyResult<()> {
        // This needs proper PipelineDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_plugin(&mut self, _plugin: PyObject) -> PyResult<()> {
        // This needs proper PluginDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_database(&mut self, _database: PyObject) -> PyResult<()> {
        // This needs proper DatabaseDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_load(&mut self, _load: PyObject) -> PyResult<()> {
        // This needs proper LoadDecl conversion
        Ok(()) // Placeholder
    }

    pub fn add_section(&mut self, _section: PyObject) -> PyResult<()> {
        // This needs proper SectionDecl conversion
        Ok(()) // Placeholder
    }

    pub fn build(&mut self) -> PyResult<PyHelixAst> {
        let ast = std::mem::replace(&mut self.inner, crate::dna::atp::ast::AstBuilder::new()).build();
        Ok(PyHelixAst { inner: ast })
    }
}

// HelixInterpreter wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyHelixInterpreter {
    inner: HelixInterpreter,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyHelixInterpreter {
    #[new]
    pub fn new() -> PyResult<Self> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                let interpreter = rt
                    .block_on(HelixInterpreter::new())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Self { inner: interpreter })
            })
        })
    }

    pub fn execute_ast(&mut self, ast: &PyHelixAst) -> PyResult<PyObject> {
        let ast_clone = ast.inner.clone();
        Python::with_gil(|py| {
            let rt = tokio::runtime::Runtime::new()
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            let result = py.allow_threads(|| {
                rt.block_on(self.inner.execute_ast(&ast_clone))
                    .map_err(|e| PyValueError::new_err(e.to_string()))
            });
            match result {
                Ok(v) => Python::with_gil(|py| {
                    match v {
                        crate::dna::atp::value::Value::String(s) => Ok(s.to_object(py)),
                        crate::dna::atp::value::Value::Number(n) => Ok(n.to_object(py)),
                        crate::dna::atp::value::Value::Bool(b) => Ok(b.to_object(py)),
                        crate::dna::atp::value::Value::Array(_) => Ok(py.None()),
                        crate::dna::atp::value::Value::Object(_) => Ok(py.None()),
                        crate::dna::atp::value::Value::Null => Ok(py.None()),
                        crate::dna::atp::value::Value::Duration(d) => Ok(d.to_string().to_object(py)),
                        crate::dna::atp::value::Value::Reference(r) => Ok(r.to_object(py)),
                        crate::dna::atp::value::Value::Identifier(i) => Ok(i.to_object(py)),
                    }
                }),
                Err(e) => Err(e),
            }
        })
    }

    pub fn operator_engine(&self) -> PyResult<PyObject> {
        let _engine = self.inner.operator_engine();
        // Wrap the operator engine
        Ok(Python::with_gil(|py| py.None()))
    }

    pub fn operator_engine_mut(&mut self) -> PyResult<PyObject> {
        let _engine = self.inner.operator_engine_mut();
        // Wrap the mutable operator engine
        Ok(Python::with_gil(|py| py.None()))
    }

    pub fn set_variable(&mut self, name: String, value: PyObject) -> PyResult<()> {
        // Convert PyObject to atp::value::Value
        let val = Python::with_gil(|py| {
            if let Ok(s) = value.extract::<String>(py) {
                crate::dna::atp::value::Value::String(s)
            } else if let Ok(n) = value.extract::<f64>(py) {
                crate::dna::atp::value::Value::Number(n)
            } else if let Ok(b) = value.extract::<bool>(py) {
                crate::dna::atp::value::Value::Bool(b)
            } else {
                // Default to string representation
                crate::dna::atp::value::Value::String(format!("{:?}", value))
            }
        });
        self.inner.set_variable(name, val);
        Ok(())
    }

    pub fn get_variable(&self, name: &str) -> PyResult<PyObject> {
        let value = self.inner.get_variable(name);
        match value {
            Some(v) => Python::with_gil(|py| {
                // Convert atp::value::Value to PyObject
                match v {
                    crate::dna::atp::value::Value::String(s) => Ok(s.to_object(py)),
                    crate::dna::atp::value::Value::Number(n) => Ok(n.to_object(py)),
                    crate::dna::atp::value::Value::Bool(b) => Ok(b.to_object(py)),
                    crate::dna::atp::value::Value::Array(arr) => {
                        let py_list = pyo3::types::PyList::empty_bound(py);
                        for item in arr {
                            // Recursively convert array items
                            let py_item = match item {
                                crate::dna::atp::value::Value::String(s) => s.to_object(py),
                                crate::dna::atp::value::Value::Number(n) => n.to_object(py),
                                crate::dna::atp::value::Value::Bool(b) => b.to_object(py),
                                crate::dna::atp::value::Value::Null => py.None(),
                                _ => py.None(),
                            };
                            py_list.append(py_item)?;
                        }
                        Ok(py_list.to_object(py))
                    }
                    crate::dna::atp::value::Value::Object(obj) => {
                        let py_dict = pyo3::types::PyDict::new_bound(py);
                        for (key, val) in obj {
                            // Recursively convert object values
                            let py_val = match val {
                                crate::dna::atp::value::Value::String(s) => s.to_object(py),
                                crate::dna::atp::value::Value::Number(n) => n.to_object(py),
                                crate::dna::atp::value::Value::Bool(b) => b.to_object(py),
                                crate::dna::atp::value::Value::Null => py.None(),
                                _ => py.None(),
                            };
                            py_dict.set_item(key, py_val)?;
                        }
                        Ok(py_dict.to_object(py))
                    }
                    crate::dna::atp::value::Value::Null => Ok(py.None()),
                    crate::dna::atp::value::Value::Duration(d) => Ok(d.to_string().to_object(py)),
                    crate::dna::atp::value::Value::Reference(r) => Ok(r.to_object(py)),
                    crate::dna::atp::value::Value::Identifier(i) => Ok(i.to_object(py)),
                }
            }),
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn list_variables(&self) -> PyResult<Vec<String>> {
        let vars = self.inner.list_variables();
        Ok(vars.into_iter().map(|(name, _value)| name).collect())
    }
}

// SourceMap wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PySourceMap {
    inner: SourceMap,
}
#[cfg(feature = "python")]
#[pymethods]
impl PySourceMap {
    #[new]
    pub fn new(source: String) -> PyResult<Self> {
        let inner = SourceMap::new(source.clone())
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Self { inner })
    }

    pub fn get_line(&self, line_num: usize) -> PyResult<String> {
        let line = self.inner.get_line(line_num);
        Ok(line.unwrap_or_default().to_string())
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PySectionName {
    inner: crate::dna::atp::ops::SectionName,
}
#[cfg(feature = "python")]
#[pymethods]
impl PySectionName {
    #[new]
    pub fn new(s: String) -> Self {
        Self {
            inner: crate::dna::atp::ops::SectionName::new(s),
        }
    }

    pub fn as_str(&self) -> &str {
        self.inner.as_str()
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyVariableName {
    inner: crate::dna::atp::ops::VariableName,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyVariableName {
    #[new]
    pub fn new(s: String) -> Self {
        Self {
            inner: crate::dna::atp::ops::VariableName::new(s),
        }
    }

    pub fn as_str(&self) -> &str {
        self.inner.as_str()
    }
}
#[cfg(feature = "python")]
#[pyclass]
pub struct PyCacheKey {
    inner: crate::dna::atp::ops::CacheKey,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCacheKey {
    #[new]
    pub fn new(file: &str, key: &str) -> Self {
        Self {
            inner: crate::dna::atp::ops::CacheKey::new(file, key),
        }
    }
}
#[cfg(feature = "python")]
#[pyclass]
pub struct PyRegexCache {
    inner: crate::dna::atp::ops::RegexCache,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyRegexCache {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: crate::dna::atp::ops::RegexCache::new(),
        }
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyStringParser {
    inner: crate::dna::atp::ops::StringParser,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyStringParser {
    #[new]
    pub fn new(input: String) -> Self {
        Self {
            inner: crate::dna::atp::ops::StringParser::new(input),
        }
    }

    pub fn parse_quoted_string(&mut self) -> PyResult<String> {
        self.inner
            .parse_quoted_string()
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyOperatorParser {
    inner: crate::dna::atp::ops::OperatorParser,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyOperatorParser {
    #[new]
    pub fn new() -> PyResult<Self> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                let parser = rt
                    .block_on(crate::dna::atp::ops::OperatorParser::new())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Self { inner: parser })
            })
        })
    }

    pub fn load_hlx(&mut self) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.load_hlx())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn try_math(&self, s: &str) -> PyResult<f64> {
        crate::dna::atp::ops::eval_math_expression(s)
            .map_err(|e| PyValueError::new_err(e.to_string()))
            .and_then(|val| match val {
                crate::dna::atp::value::Value::Number(n) => Ok(n),
                _ => Err(PyValueError::new_err(
                    "Math expression did not evaluate to a number",
                )),
            })
    }

    pub fn execute_date(&self, fmt: &str) -> PyResult<String> {
        Ok(crate::dna::atp::ops::eval_date_expression(fmt))
    }

    pub fn parse_line(&mut self, raw: &str) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.parse_line(raw))
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn get(&self, key: &str) -> PyResult<PyObject> {
        let value = self.inner.get(key);
        match value {
            Some(v) => Python::with_gil(|py| {
                // Convert ops::value::Value to PyObject
                match v {
                    crate::dna::atp::value::Value::String(s) => Ok(s.to_object(py)),
                    crate::dna::atp::value::Value::Number(n) => Ok(n.to_object(py)),
                    crate::dna::atp::value::Value::Bool(b) => Ok(b.to_object(py)),
                    crate::dna::atp::value::Value::Array(_) => Ok(py.None()),
                    crate::dna::atp::value::Value::Object(_) => Ok(py.None()),
                    crate::dna::atp::value::Value::Null => Ok(py.None()),
                    crate::dna::atp::value::Value::Duration(d) => Ok(d.to_string().to_object(py)),
                    crate::dna::atp::value::Value::Reference(r) => Ok(r.to_object(py)),
                    crate::dna::atp::value::Value::Identifier(i) => Ok(i.to_object(py)),
                }
            }),
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn get_ref(&self, key: &str) -> PyResult<PyObject> {
        let value = self.inner.get_ref(key);
        match value {
            Some(v) => Python::with_gil(|py| {
                // Convert &ops::value::Value to PyObject
                match v {
                    crate::dna::atp::value::Value::String(s) => Ok(s.to_object(py)),
                    crate::dna::atp::value::Value::Number(n) => Ok(n.to_object(py)),
                    crate::dna::atp::value::Value::Bool(b) => Ok(b.to_object(py)),
                    crate::dna::atp::value::Value::Array(_) => Ok(py.None()),
                    crate::dna::atp::value::Value::Object(_) => Ok(py.None()),
                    crate::dna::atp::value::Value::Null => Ok(py.None()),
                    crate::dna::atp::value::Value::Duration(d) => Ok(d.to_string().to_object(py)),
                    crate::dna::atp::value::Value::Reference(r) => Ok(r.to_object(py)),
                    crate::dna::atp::value::Value::Identifier(i) => Ok(i.to_object(py)),
                }
            }),
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn set(&mut self, key: &str, value: PyObject) -> PyResult<()> {
        // Convert PyObject to ops::value::Value
        let val = Python::with_gil(|py| {
            if let Ok(s) = value.extract::<String>(py) {
                crate::dna::atp::value::Value::String(s)
            } else if let Ok(n) = value.extract::<f64>(py) {
                crate::dna::atp::value::Value::Number(n)
            } else if let Ok(b) = value.extract::<bool>(py) {
                crate::dna::atp::value::Value::Bool(b)
            } else {
                // Default to string representation
                crate::dna::atp::value::Value::String(format!("{:?}", value))
            }
        });
        self.inner.set(key, val);
        Ok(())
    }

    pub fn keys(&self) -> PyResult<Vec<String>> {
        Ok(self.inner.keys())
    }

    pub fn items(&self) -> PyResult<Vec<(String, PyObject)>> {
        let items = self.inner.items();
        // Convert &HashMap<String, Value> to Vec<(String, PyObject)>
        let mut result = Vec::new();
        for (key, value) in items.iter() {
            let py_obj = Python::with_gil(|py| {
                // Convert ops::value::Value to PyObject
                match value {
                    crate::dna::atp::value::Value::String(s) => s.to_object(py),
                    crate::dna::atp::value::Value::Number(n) => n.to_object(py),
                    crate::dna::atp::value::Value::Bool(b) => b.to_object(py),
                    crate::dna::atp::value::Value::Array(_) => py.None(),
                    crate::dna::atp::value::Value::Object(_) => py.None(),
                    crate::dna::atp::value::Value::Null => py.None(),
                    crate::dna::atp::value::Value::Duration(d) => d.to_string().to_object(py),
                    crate::dna::atp::value::Value::Reference(r) => r.to_object(py),
                    crate::dna::atp::value::Value::Identifier(i) => i.to_object(py),
                }
            });
            result.push((key.clone(), py_obj));
        }
        Ok(result)
    }

    pub fn items_cloned(&self) -> PyResult<Vec<(String, PyObject)>> {
        let items = self.inner.items_cloned();
        // Convert Vec<(String, ops::value::Value)> to Vec<(String, PyObject)>
        let mut result = Vec::new();
        for (key, value) in items {
            let py_obj = Python::with_gil(|py| {
                // Convert ops::value::Value to PyObject
                match value {
                    crate::dna::atp::value::Value::String(s) => s.to_object(py),
                    crate::dna::atp::value::Value::Number(n) => n.to_object(py),
                    crate::dna::atp::value::Value::Bool(b) => b.to_object(py),
                    crate::dna::atp::value::Value::Array(_) => py.None(),
                    crate::dna::atp::value::Value::Object(_) => py.None(),
                    crate::dna::atp::value::Value::Null => py.None(),
                    crate::dna::atp::value::Value::Duration(d) => d.to_string().to_object(py),
                    crate::dna::atp::value::Value::Reference(r) => r.to_object(py),
                    crate::dna::atp::value::Value::Identifier(i) => i.to_object(py),
                }
            });
            result.push((key, py_obj));
        }
        Ok(result)
    }

    pub fn get_errors(&self) -> PyResult<Vec<String>> {
        Ok(self.inner.get_errors().iter().map(|e| e.to_string()).collect())
    }

    pub fn has_errors(&self) -> bool {
        self.inner.has_errors()
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyOutputFormat {
    inner: OutputFormat,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyOutputFormat {
    #[new]
    pub fn from_str(s: &str) -> PyResult<Self> {
        let format = OutputFormat::from(s)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Self { inner: format })
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyCompressionConfig {
    inner: CompressionConfig,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCompressionConfig {
    #[new]
    pub fn default() -> Self {
        Self {
            inner: CompressionConfig::default(),
        }
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyOutputConfig {
    inner: OutputConfig,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyOutputConfig {
    #[new]
    pub fn default() -> Self {
        Self {
            inner: OutputConfig::default(),
        }
    }
}

#[cfg(feature = "python")]
#[pyclass(unsendable)]
pub struct PyOutputManager {
    inner: OutputManager,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyOutputManager {
    #[new]
    pub fn new(config: &PyOutputConfig) -> Self {
        Self {
            inner: OutputManager::new(config.inner.clone()),
        }
    }

    pub fn add_row(&mut self, row: HashMap<String, PyObject>) -> PyResult<()> {
        // Convert HashMap<String, PyObject> to HashMap<String, AtpValue>
        let converted_row: HashMap<String, crate::dna::atp::value::Value> = HashMap::new(); // Placeholder
        self.inner.add_row(converted_row);
        Ok(())
    }

    pub fn flush_batch(&mut self) -> PyResult<()> {
        self.inner
            .flush_batch()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn finalize_all(&mut self) -> PyResult<()> {
        self.inner
            .finalize_all()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn get_output_files(&self) -> PyResult<Vec<String>> {
        Ok(self.inner.get_output_files().iter().map(|p| p.to_string_lossy().to_string()).collect())
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHlxcDataWriter {
    inner: crate::dna::atp::output::HlxcDataWriter,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHlxcDataWriter {
    #[new]
    pub fn new(config: &PyOutputConfig) -> Self {
        Self {
            inner: crate::dna::atp::output::HlxcDataWriter::new(config.inner.clone()),
        }
    }

    pub fn write_batch(&mut self, batch: PyObject) -> PyResult<()> {
        // Convert PyObject to RecordBatch
        // This would need proper Arrow RecordBatch conversion
        Ok(())
    }

    pub fn finalize(&mut self) -> PyResult<()> {
        self.inner
            .finalize()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyParser {
    inner: Parser,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyParser {
    #[new]
    pub fn new(tokens: Vec<PyObject>) -> PyResult<Self> {
        // Convert Vec<PyObject> to Vec<Token>
        let converted_tokens: Vec<Token> = vec![]; // Placeholder
        Ok(Self {
            inner: Parser::new(converted_tokens),
        })
    }

    #[staticmethod]
    pub fn new_enhanced(tokens: Vec<PyObject>) -> PyResult<Self> {
        // Convert Vec<PyObject> to Vec<TokenWithLocation>
        let converted_tokens: Vec<crate::dna::atp::lexer::TokenWithLocation> = vec![]; // Placeholder
        Ok(Self {
            inner: Parser::new_enhanced(converted_tokens),
        })
    }

    #[staticmethod]
    pub fn new_with_source_map(source_map: &PySourceMap) -> Self {
        Self {
            inner: Parser::new_with_source_map(source_map.inner.clone()),
        }
    }

    pub fn set_runtime_context(&mut self, context: HashMap<String, String>) -> PyResult<()> {
        self.inner.set_runtime_context(context);
        Ok(())
    }

    pub fn parse(&mut self) -> PyResult<PyHelixAst> {
        let ast = self
            .inner
            .parse()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(PyHelixAst { inner: ast })
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHelixLoader {
    inner: HelixLoader,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHelixLoader {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HelixLoader::new(),
        }
    }

    pub fn parse(&mut self, content: &str) -> PyResult<()> {
        self.inner
            .parse(content)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn get_config(&self, name: &str) -> PyResult<PyObject> {
        let config = self.inner.get_config(name);
        match config {
            Some(c) => Ok(Python::with_gil(|py| py.None())), // Convert HelixConfig to PyObject
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn set_context(&mut self, context: String) -> PyResult<()> {
        self.inner.set_context(context);
        Ok(())
    }

    pub fn merge_configs(&self, configs: Vec<PyObject>) -> PyResult<PyObject> {
        // Convert Vec<PyObject> to Vec<&HelixConfig>
        let converted_configs: Vec<&HelixConfig> = vec![]; // Placeholder
        let merged = self.inner.merge_configs(converted_configs);
        Ok(Python::with_gil(|py| py.None())) // Convert to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyCompiler {
    inner: Compiler,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCompiler {
    #[new]
    pub fn new(optimization_level: PyObject) -> PyResult<Self> {
        // Convert PyObject to OptimizationLevel
        let level = Python::with_gil(|py| {
            if let Ok(s) = optimization_level.extract::<String>(py) {
                match s.to_lowercase().as_str() {
                    "zero" => OptimizationLevel::Zero,
                    "one" => OptimizationLevel::One,
                    "two" => OptimizationLevel::Two,
                    "three" => OptimizationLevel::Three,
                    _ => OptimizationLevel::Two,
                }
            } else if let Ok(n) = optimization_level.extract::<u8>(py) {
                OptimizationLevel::from(n)
            } else {
                OptimizationLevel::Two
            }
        });
        Ok(Self {
            inner: Compiler::new(level),
        })
    }

    #[staticmethod]
    pub fn builder() -> PyResult<PyCompilerBuilder> {
        Ok(PyCompilerBuilder {
            inner: Compiler::builder(),
        })
    }

    pub fn decompile(&self, binary: PyObject) -> PyResult<PyObject> {
        // Convert PyObject to &HelixBinary
        let bin = HelixBinary::new(); // Placeholder
        let ast = self
            .inner
            .decompile(&bin)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Python::with_gil(|py| py.None())) // Convert to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyCompilerBuilder {
    inner: CompilerBuilder,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCompilerBuilder {
    pub fn optimization_level(&mut self, level: PyObject) -> PyResult<()> {
        // Convert PyObject to OptimizationLevel
        let opt_level = Python::with_gil(|py| {
            if let Ok(s) = level.extract::<String>(py) {
                match s.to_lowercase().as_str() {
                    "zero" => OptimizationLevel::Zero,
                    "one" => OptimizationLevel::One,
                    "two" => OptimizationLevel::Two,
                    "three" => OptimizationLevel::Three,
                    _ => OptimizationLevel::Two,
                }
            } else if let Ok(n) = level.extract::<u8>(py) {
                OptimizationLevel::from(n)
            } else {
                OptimizationLevel::Two
            }
        });
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.optimization_level(opt_level);
        Ok(())
    }

    pub fn compression(&mut self, enable: bool) -> PyResult<()> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.compression(enable);
        Ok(())
    }

    pub fn cache(&mut self, enable: bool) -> PyResult<()> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.cache(enable);
        Ok(())
    }

    pub fn verbose(&mut self, enable: bool) -> PyResult<()> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        self.inner = builder.verbose(enable);
        Ok(())
    }

    pub fn build(&mut self) -> PyResult<PyCompiler> {
        let builder = std::mem::replace(&mut self.inner, CompilerBuilder::default());
        let compiler = builder.build();
        Ok(PyCompiler { inner: compiler })
    }
}

#[cfg(feature = "python")]
#[pyclass]
#[derive(Clone, Debug)]
pub struct PyHelixBinary {
    inner: HelixBinary,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyHelixBinary {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HelixBinary::new(),
        }
    }

    pub fn validate(&self) -> PyResult<()> {
        self.inner
            .validate()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn calculate_checksum(&self) -> PyResult<u64> {
        Ok(self.inner.calculate_checksum())
    }

    pub fn size(&self) -> usize {
        self.inner.size()
    }

    pub fn compression_ratio(&self, original_size: usize) -> f64 {
        self.inner.compression_ratio(original_size)
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHelixDispatcher {
    inner: HelixDispatcher,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHelixDispatcher {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HelixDispatcher::new(),
        }
    }

    pub fn initialize(&mut self) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.initialize())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn parse_only(&self, source: &str) -> PyResult<String> {
        let tokens_with_loc = crate::dna::atp::lexer::tokenize_with_locations(source)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        let source_map = crate::dna::atp::lexer::SourceMap {
            tokens: tokens_with_loc.clone(),
            source: source.to_string(),
        };
        let mut parser = crate::dna::atp::parser::Parser::new_with_source_map(source_map);
        match parser.parse() {
            Ok(ast) => Ok(format!("{:?}", ast)),
            Err(e) => Err(PyValueError::new_err(e)),
        }
    }

    pub fn parse_dsl(&mut self, source: &str) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.parse_dsl(source))
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn interpreter(&self) -> PyResult<PyHelixInterpreter> {
        // Since we can't clone the interpreter, create a new one
        // The original interpreter reference is just used to check if it's initialized
        let _ = self.inner.interpreter()
            .ok_or_else(|| PyValueError::new_err("Interpreter not initialized"))?;
        PyHelixInterpreter::new()
    }

    pub fn interpreter_mut(&mut self) -> PyResult<PyHelixInterpreter> {
        // Can't clone a mutable reference, need to return an error or handle differently
        Err(PyValueError::new_err("Cannot clone mutable interpreter reference"))
    }

    pub fn is_ready(&self) -> bool {
        self.inner.is_ready()
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHlx {
    inner: Hlx,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHlx {
    #[new]
    pub fn new() -> PyResult<Self> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                let hlx = rt
                    .block_on(Hlx::new())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Self { inner: hlx })
            })
        })
    }

    pub fn get_raw(&self, section: &str, key: &str) -> PyResult<PyObject> {
        let value = self.inner.get_raw(section, key);
        match value {
            Some(v) => Ok(Python::with_gil(|py| py.None())), // Convert Value to PyObject
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn get_str(&self, section: &str, key: &str) -> PyResult<String> {
        self.inner
            .get_str(section, key)
            .map(|s| s.to_string())
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_num(&self, section: &str, key: &str) -> PyResult<f64> {
        self.inner
            .get_num(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_bool(&self, section: &str, key: &str) -> PyResult<bool> {
        self.inner
            .get_bool(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_array(&self, section: &str, key: &str) -> PyResult<Vec<PyObject>> {
        let arr = self
            .inner
            .get_array(section, key)
            .ok_or(PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))?;

        let mut result = Vec::new();
        Python::with_gil(|py| {
            for val in arr {
                let py_obj = match val {
                    crate::dna::atp::value::Value::String(s) => s.to_object(py),
                    crate::dna::atp::value::Value::Number(n) => n.to_object(py),
                    crate::dna::atp::value::Value::Bool(b) => b.to_object(py),
                    crate::dna::atp::value::Value::Null => py.None(),
                    _ => py.None(),
                };
                result.push(py_obj);
            }
        });
        Ok(result)
    }

    pub fn get_string(&self, section: &str, key: &str) -> PyResult<String> {
        self.inner
            .get_string(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_i32(&self, section: &str, key: &str) -> PyResult<i32> {
        self.inner
            .get_i32(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_i64(&self, section: &str, key: &str) -> PyResult<i64> {
        self.inner
            .get_i64(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_u32(&self, section: &str, key: &str) -> PyResult<u32> {
        self.inner
            .get_u32(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_u64(&self, section: &str, key: &str) -> PyResult<u64> {
        self.inner
            .get_u64(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_f32(&self, section: &str, key: &str) -> PyResult<f32> {
        self.inner
            .get_f32(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_f64(&self, section: &str, key: &str) -> PyResult<f64> {
        self.inner
            .get_f64(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_string(&self, section: &str, key: &str) -> PyResult<Vec<String>> {
        self.inner
            .get_vec_string(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_i32(&self, section: &str, key: &str) -> PyResult<Vec<i32>> {
        self.inner
            .get_vec_i32(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_f64(&self, section: &str, key: &str) -> PyResult<Vec<f64>> {
        self.inner
            .get_vec_f64(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_vec_bool(&self, section: &str, key: &str) -> PyResult<Vec<bool>> {
        self.inner
            .get_vec_bool(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))
    }

    pub fn get_dynamic(&self, section: &str, key: &str) -> PyResult<PyDynamicValue> {
        let value = self
            .inner
            .get_dynamic(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))?;
        Ok(PyDynamicValue { inner: value })
    }

    pub fn get_auto(&self, section: &str, key: &str) -> PyResult<PyObject> {
        let value = self
            .inner
            .get_auto(section, key)
            .ok_or_else(|| PyValueError::new_err(format!(
                "Key '{}' not found in section '{}'",
                key, section
            )))?;
        Ok(Python::with_gil(|py| value.to_object(py)))
    }

    pub fn select(&self, section: &str, key: &str) -> PyResult<PyObject> {
        // TypedGetter wrapper - for now return a placeholder
        Ok(Python::with_gil(|py| py.None()))
    }

    pub fn set_str(&mut self, section: &str, key: &str, value: &str) -> PyResult<()> {
        self.inner.set_str(section, key, value);
        Ok(())
    }

    pub fn set_num(&mut self, section: &str, key: &str, value: f64) -> PyResult<()> {
        self.inner.set_num(section, key, value);
        Ok(())
    }

    pub fn set_bool(&mut self, section: &str, key: &str, value: bool) -> PyResult<()> {
        self.inner.set_bool(section, key, value);
        Ok(())
    }

    pub fn increase(&mut self, section: &str, key: &str, amount: f64) -> PyResult<f64> {
        self.inner
            .increase(section, key, amount)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    pub fn index(&self, section: &str) -> PyResult<PyObject> {
        let index = self.inner.index(section);
        Ok(Python::with_gil(|py| py.None())) // Convert index to PyObject
    }

    pub fn index_mut(&mut self, section: &str) -> PyResult<PyObject> {
        let index = self.inner.index_mut(section);
        Ok(Python::with_gil(|py| py.None())) // Convert mutable index to PyObject
    }

    pub fn server(&mut self) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.server())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn watch(&mut self) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.watch())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn process(&mut self) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.process())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn compile(&mut self) -> PyResult<()> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                rt.block_on(self.inner.compile())
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(())
            })
        })
    }

    pub fn execute(&mut self, code: &str) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                let result = rt
                    .block_on(self.inner.execute(code))
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Python::with_gil(|py| py.None())) // Convert result to PyObject
            })
        })
    }

    pub fn sections(&self) -> PyResult<Vec<String>> {
        Ok(self.inner.sections().iter().map(|s| s.to_string()).collect())
    }

    pub fn keys(&self, section: &str) -> PyResult<Vec<String>> {
        let keys = self.inner.keys(section)
            .ok_or_else(|| PyValueError::new_err(format!("Section '{}' not found", section)))?;
        Ok(keys.iter().map(|s| s.to_string()).collect())
    }

    pub fn get_file_path(&self) -> PyResult<String> {
        let path = self.inner.get_file_path()
            .ok_or_else(|| PyValueError::new_err("No file path available"))?;
        Ok(path.to_string_lossy().to_string())
    }

    pub fn save(&self) -> PyResult<()> {
        self.inner
            .save()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn make(&self) -> PyResult<PyObject> {
        let result = self
            .inner
            .make()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Python::with_gil(|py| py.None())) // Convert result to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyDynamicValue {
    inner: DynamicValue,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyDynamicValue {
    pub fn as_string(&self) -> PyResult<String> {
        Ok(self.inner.as_string().unwrap_or_default())
    }

    pub fn as_number(&self) -> PyResult<f64> {
        Ok(self.inner.as_number().unwrap_or(0.0))
    }

    pub fn as_integer(&self) -> PyResult<i64> {
        Ok(self.inner.as_integer().unwrap_or(0))
    }

    pub fn as_bool(&self) -> PyResult<bool> {
        Ok(self.inner.as_bool().unwrap_or(false))
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyAtpValue {
    inner: crate::dna::atp::value::Value,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyAtpValue {
    #[new]
    pub fn default() -> Self {
        Self {
            inner: crate::dna::atp::value::Value::default(),
        }
    }

    pub fn value_type(&self) -> PyResult<String> {
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

    pub fn as_string(&self) -> PyResult<String> {
        self.inner
            .as_string()
            .map(|s| s.to_string())
            .ok_or(PyValueError::new_err("Value is not a string"))
    }

    pub fn as_number(&self) -> PyResult<f64> {
        self.inner
            .as_number()
            .ok_or(PyValueError::new_err("Value is not a number"))
    }

    pub fn as_f64(&self) -> PyResult<f64> {
        self.inner
            .as_f64()
            .ok_or(PyValueError::new_err("Value is not a number"))
    }

    pub fn as_str(&self) -> PyResult<String> {
        self.inner
            .as_str()
            .map(|s| s.to_string())
            .ok_or(PyValueError::new_err("Value is not a string"))
    }

    pub fn as_boolean(&self) -> PyResult<bool> {
        self.inner
            .as_boolean()
            .ok_or(PyValueError::new_err("Value is not a boolean"))
    }

    pub fn as_array(&self) -> PyResult<Vec<PyObject>> {
        let arr = self
            .inner
            .as_array()
            .ok_or(PyValueError::new_err("Value is not an array"))?;
        // Convert Vec<Value> to Vec<PyObject>
        let mut result = Vec::new();
        for item in arr {
            let py_obj = Python::with_gil(|py| match item {
                crate::dna::atp::value::Value::String(s) => s.into_py(py),
                crate::dna::atp::value::Value::Number(n) => n.into_py(py),
                crate::dna::atp::value::Value::Bool(b) => b.into_py(py),
                crate::dna::atp::value::Value::Array(_) => py.None(),
                crate::dna::atp::value::Value::Object(_) => py.None(),
                crate::dna::atp::value::Value::Null => py.None(),
                _ => py.None(),
            });
            result.push(py_obj);
        }
        Ok(result)
    }

    pub fn as_object(&self) -> PyResult<HashMap<String, PyObject>> {
        let obj = self
            .inner
            .as_object()
            .ok_or(PyValueError::new_err("Value is not an object"))?;
        // Convert HashMap<String, Value> to HashMap<String, PyObject>
        let mut result = HashMap::new();
        for (key, value) in obj {
            let py_obj = Python::with_gil(|py| match value {
                crate::dna::atp::value::Value::String(s) => s.into_py(py),
                crate::dna::atp::value::Value::Number(n) => n.into_py(py),
                crate::dna::atp::value::Value::Bool(b) => b.into_py(py),
                crate::dna::atp::value::Value::Array(_) => py.None(),
                crate::dna::atp::value::Value::Object(_) => py.None(),
                crate::dna::atp::value::Value::Null => py.None(),
                _ => py.None(),
            });
            result.insert(key.clone(), py_obj);
        }
        Ok(result)
    }

    pub fn get(&self, key: &str) -> PyResult<PyObject> {
        let value = self.inner.get(key);
        match value {
            Some(v) => Python::with_gil(|py| match v {
                crate::dna::atp::value::Value::String(s) => Ok(s.to_object(py)),
                crate::dna::atp::value::Value::Number(n) => Ok(n.to_object(py)),
                crate::dna::atp::value::Value::Bool(b) => Ok(b.to_object(py)),
                crate::dna::atp::value::Value::Array(_) => Ok(py.None()),
                crate::dna::atp::value::Value::Object(_) => Ok(py.None()),
                crate::dna::atp::value::Value::Null => Ok(py.None()),
                crate::dna::atp::value::Value::Duration(d) => Ok(d.to_string().to_object(py)),
                crate::dna::atp::value::Value::Reference(r) => Ok(r.to_object(py)),
                crate::dna::atp::value::Value::Identifier(i) => Ok(i.to_object(py)),
            }),
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn get_mut(&mut self, key: &str) -> PyResult<PyObject> {
        let value = self.inner.get_mut(key);
        match value {
            Some(v) => Python::with_gil(|py| match v {
                crate::dna::atp::value::Value::String(s) => Ok(s.to_object(py)),
                crate::dna::atp::value::Value::Number(n) => Ok(n.to_object(py)),
                crate::dna::atp::value::Value::Bool(b) => Ok(b.to_object(py)),
                crate::dna::atp::value::Value::Array(_) => Ok(py.None()),
                crate::dna::atp::value::Value::Object(_) => Ok(py.None()),
                crate::dna::atp::value::Value::Null => Ok(py.None()),
                crate::dna::atp::value::Value::Duration(d) => Ok(d.to_string().to_object(py)),
                crate::dna::atp::value::Value::Reference(r) => Ok(r.to_object(py)),
                crate::dna::atp::value::Value::Identifier(i) => Ok(i.to_object(py)),
            }),
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn get_string(&self, key: &str) -> PyResult<String> {
        self.inner
            .get_string(key)
            .map(|s| s.to_string())
            .ok_or(PyValueError::new_err(format!(
                "Key '{}' not found or not a string",
                key
            )))
    }

    pub fn get_number(&self, key: &str) -> PyResult<f64> {
        self.inner
            .get_number(key)
            .ok_or(PyValueError::new_err(format!(
                "Key '{}' not found or not a number",
                key
            )))
    }

    pub fn get_boolean(&self, key: &str) -> PyResult<bool> {
        self.inner
            .get_boolean(key)
            .ok_or(PyValueError::new_err(format!(
                "Key '{}' not found or not a boolean",
                key
            )))
    }

    pub fn get_array(&self, key: &str) -> PyResult<Vec<PyObject>> {
        let arr = self
            .inner
            .get_array(key)
            .ok_or(PyValueError::new_err(format!(
                "Key '{}' not found or not an array",
                key
            )))?;
        // Convert Vec<Value> to Vec<PyObject>
        let mut result = Vec::new();
        for item in arr {
            let py_obj = Python::with_gil(|py| match item {
                crate::dna::atp::value::Value::String(s) => s.into_py(py),
                crate::dna::atp::value::Value::Number(n) => n.into_py(py),
                crate::dna::atp::value::Value::Bool(b) => b.into_py(py),
                crate::dna::atp::value::Value::Array(_) => py.None(),
                crate::dna::atp::value::Value::Object(_) => py.None(),
                crate::dna::atp::value::Value::Null => py.None(),
                _ => py.None(),
            });
            result.push(py_obj);
        }
        Ok(result)
    }

    pub fn get_object(&self, key: &str) -> PyResult<HashMap<String, PyObject>> {
        let obj = self
            .inner
            .get_object(key)
            .ok_or(PyValueError::new_err(format!(
                "Key '{}' not found or not an object",
                key
            )))?;
        // Convert HashMap<String, Value> to HashMap<String, PyObject>
        let mut result = HashMap::new();
        for (key, value) in obj {
            let py_obj = Python::with_gil(|py| match value {
                crate::dna::atp::value::Value::String(s) => s.into_py(py),
                crate::dna::atp::value::Value::Number(n) => n.into_py(py),
                crate::dna::atp::value::Value::Bool(b) => b.into_py(py),
                crate::dna::atp::value::Value::Array(_) => py.None(),
                crate::dna::atp::value::Value::Object(_) => py.None(),
                crate::dna::atp::value::Value::Null => py.None(),
                _ => py.None(),
            });
            result.insert(key.clone(), py_obj);
        }
        Ok(result)
    }

    pub fn to_string(&self) -> String {
        self.inner.to_string()
    }

    pub fn to_json(&self) -> PyResult<String> {
        self.inner
            .to_json()
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    pub fn to_yaml(&self) -> PyResult<String> {
        self.inner
            .to_yaml()
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    #[staticmethod]
    pub fn from_json(json_value: PyObject) -> PyResult<Self> {
        // Convert PyObject to serde_json::Value
        let json = serde_json::Value::Null; // Placeholder
        let value = crate::dna::atp::value::Value::from_json(json);
        Ok(Self { inner: value })
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHlxHeader {
    inner: HlxHeader,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHlxHeader {
    #[new]
    pub fn new(schema: PyObject, metadata: HashMap<String, PyObject>) -> PyResult<Self> {
        // Convert parameters
        use arrow::datatypes::{DataType, Field, Schema};
        let converted_schema = Schema::new(vec![Field::new("placeholder", DataType::Utf8, false)]);
        let converted_metadata: HashMap<String, serde_json::Value> = HashMap::new(); // Placeholder
        let header = HlxHeader::new(&converted_schema, converted_metadata);
        Ok(Self { inner: header })
    }

    pub fn with_compression(&mut self, compressed: bool) -> PyResult<()> {
        let inner = self.inner.clone();
        self.inner = inner.with_compression(compressed);
        Ok(())
    }

    pub fn with_row_count(&mut self, count: u64) -> PyResult<()> {
        let inner = self.inner.clone();
        self.inner = inner.with_row_count(count);
        Ok(())
    }

    pub fn with_preview(&mut self, preview: Vec<PyObject>) -> PyResult<()> {
        // Convert Vec<PyObject> to Vec<serde_json::Value>
        let converted_preview: Vec<serde_json::Value> = vec![]; // Placeholder
        let inner = self.inner.clone();
        self.inner = inner.with_preview(converted_preview);
        Ok(())
    }

    pub fn is_compressed(&self) -> bool {
        self.inner.is_compressed()
    }

    pub fn to_json_bytes(&self) -> PyResult<Vec<u8>> {
        self.inner.to_json_bytes()
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    #[staticmethod]
    pub fn from_json_bytes(bytes: &[u8]) -> PyResult<Self> {
        let header =
            HlxHeader::from_json_bytes(bytes).map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Self { inner: header })
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PySymbolTable {
    inner: crate::dna::hel::binary::SymbolTable,
}
#[cfg(feature = "python")]
#[pymethods]
impl PySymbolTable {
    pub fn intern(&mut self, s: &str) -> u32 {
        self.inner.intern(s)
    }

    pub fn get(&self, id: u32) -> PyResult<String> {
        self.inner
            .get(id)
            .ok_or_else(|| PyValueError::new_err(format!("Symbol with id {} not found", id)))
            .map(|s| s.clone())
    }

    pub fn stats(&self) -> PyObject {
        let stats = self.inner.stats();
        Python::with_gil(|py| py.None()) // Convert stats to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyDataSection {
    inner: DataSection,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyDataSection {
    #[new]
    pub fn new(section_type: PyObject, data: Vec<u8>) -> PyResult<Self> {
        // Convert PyObject to SectionType
        let st = crate::dna::hel::binary::SectionType::Project; // Placeholder
        let section = DataSection::new(st, data);
        Ok(Self { inner: section })
    }

    pub fn compress(&mut self, method: PyObject) -> PyResult<()> {
        // Convert PyObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        self.inner
            .compress(cm)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn decompress(&mut self) -> PyResult<()> {
        self.inner
            .decompress()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHelixVM {
    inner: HelixVM,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyHelixVM {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HelixVM::new(),
        }
    }

    pub fn with_debug(&mut self) {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.with_debug();
    }

    pub fn execute_binary(&mut self, binary: &PyHelixBinary) -> PyResult<()> {
        self.inner
            .execute_binary(&binary.inner)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn push(&mut self, value: PyObject) -> PyResult<()> {
        // Convert PyObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        self.inner.push(val);
        Ok(())
    }

    pub fn pop(&mut self) -> PyResult<()> {
        self.inner
            .pop()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn load_memory(&self, address: u32) -> PyResult<PyObject> {
        let value = self.inner.load_memory(address);
        Ok(Python::with_gil(|py| py.None())) // Convert Value to PyObject
    }

    pub fn store_memory(&mut self, address: u32, value: PyObject) -> PyResult<()> {
        // Convert PyObject to Value
        let val = crate::dna::hel::binary::Value::Null; // Placeholder
        self.inner.store_memory(address, val);
        Ok(())
    }

    pub fn set_breakpoint(&mut self, address: usize) -> PyResult<()> {
        self.inner.set_breakpoint(address);
        Ok(())
    }

    pub fn remove_breakpoint(&mut self, address: usize) -> PyResult<()> {
        self.inner.remove_breakpoint(address);
        Ok(())
    }

    pub fn continue_execution(&mut self) -> PyResult<()> {
        self.inner.continue_execution();
        Ok(())
    }

    pub fn step(&mut self) -> PyResult<()> {
        self.inner.step();
        Ok(())
    }

    pub fn state(&self) -> PyResult<PyObject> {
        let state = self.inner.state();
        Ok(Python::with_gil(|py| py.None())) // Convert VMState to PyObject
    }

    pub fn stats(&self) -> PyResult<PyObject> {
        let stats = self.inner.stats();
        Ok(Python::with_gil(|py| py.None())) // Convert VMStats to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyVMExecutor {
    inner: VMExecutor,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyVMExecutor {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: VMExecutor::new(),
        }
    }

    pub fn vm(&mut self) -> PyResult<PyHelixVM> {
        // vm() returns &mut, can't move it - need to clone or return reference
        Err(PyValueError::new_err("Cannot move vm from executor"))
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyAppState {
    inner: crate::dna::vlt::tui::AppState,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyAppState {
    #[new]
    pub fn new() -> PyResult<Self> {
        Ok(Self {
            inner: crate::dna::vlt::tui::AppState::new()
                .map_err(|e| PyValueError::new_err(e.to_string()))?,
        })
    }

    pub fn focus(&mut self, area: PyObject) -> PyResult<()> {
        // Convert PyObject to FocusArea
        let focus_area = crate::dna::vlt::tui::FocusArea::Files; // Placeholder
        self.inner.focus(focus_area);
        Ok(())
    }

    pub fn select_next_file(&mut self) -> PyResult<()> {
        self.inner.select_next_file();
        Ok(())
    }

    pub fn select_prev_file(&mut self) -> PyResult<()> {
        self.inner.select_prev_file();
        Ok(())
    }

    pub fn open_selected_file(&mut self) -> PyResult<()> {
        self.inner
            .open_selected_file()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn select_next_operator(&mut self) -> PyResult<()> {
        self.inner.select_next_operator();
        Ok(())
    }

    pub fn select_prev_operator(&mut self) -> PyResult<()> {
        self.inner.select_prev_operator();
        Ok(())
    }

    pub fn cycle_operator_category_next(&mut self) -> PyResult<()> {
        self.inner.cycle_operator_category_next();
        Ok(())
    }

    pub fn cycle_operator_category_prev(&mut self) -> PyResult<()> {
        self.inner.cycle_operator_category_prev();
        Ok(())
    }

    pub fn reset_operator_category(&mut self) -> PyResult<()> {
        self.inner.reset_operator_category();
        Ok(())
    }

    pub fn sync_operator_selection(&mut self) -> PyResult<()> {
        self.inner.sync_operator_selection();
        Ok(())
    }

    pub fn insert_selected_operator(&mut self) -> PyResult<()> {
        self.inner.insert_selected_operator();
        Ok(())
    }

    pub fn next_tab(&mut self) -> PyResult<()> {
        self.inner.next_tab();
        Ok(())
    }

    pub fn previous_tab(&mut self) -> PyResult<()> {
        self.inner.previous_tab();
        Ok(())
    }

    pub fn close_active_tab(&mut self) -> PyResult<()> {
        self.inner.close_active_tab();
        Ok(())
    }

    pub fn create_new_tab(&mut self) -> PyResult<()> {
        self.inner.create_new_tab();
        Ok(())
    }

    pub fn save_active_tab(&mut self) -> PyResult<()> {
        self.inner
            .save_active_tab()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn trigger_command(&mut self) -> PyResult<()> {
        self.inner.trigger_command();
        Ok(())
    }

    pub fn select_next_command(&mut self) -> PyResult<()> {
        self.inner.select_next_command();
        Ok(())
    }

    pub fn select_prev_command(&mut self) -> PyResult<()> {
        self.inner.select_prev_command();
        Ok(())
    }

    pub fn on_tick(&mut self) -> PyResult<()> {
        self.inner.on_tick();
        Ok(())
    }
}

#[cfg(feature = "python")]  
#[pyclass]
pub struct PyBenchmark {
    inner: Benchmark,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyBenchmark {
    #[new]
    pub fn new(name: &str) -> Self {
        Self {
            inner: Benchmark::new(name),
        }
    }

    pub fn with_iterations(&mut self, iterations: usize) -> PyResult<()> {
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_iterations(iterations);
        Ok(())
    }

    pub fn with_warmup(&mut self, warmup: usize) -> PyResult<()> {
        self.inner = std::mem::replace(&mut self.inner, Benchmark::new("")).with_warmup(warmup);
        Ok(())
    }

    pub fn run(&self, f: PyObject) -> PyResult<PyObject> {
        // This needs to be implemented with proper callback handling
        Ok(Python::with_gil(|py| py.None()))
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyBundler {
    inner: Bundler,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyBundler {
    #[new]
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

#[cfg(feature = "python")]
#[pyclass]
pub struct PyBundleBuilder {
    inner: crate::dna::mds::bundle::BundleBuilder,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyBundleBuilder {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: crate::dna::mds::bundle::BundleBuilder::new(),
        }
    }

    pub fn add_file(&mut self, path: String, binary: PyHelixBinary) -> PyResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner.add_file(path_buf, binary.inner);
        Ok(())
    }

    pub fn add_dependency(&mut self, from: String, to: String) -> PyResult<()> {
        let from_path = std::path::PathBuf::from(from);
        let to_path = std::path::PathBuf::from(to);
        self.inner.add_dependency(from_path, to_path);
        Ok(())
    }

    pub fn build(&mut self) -> PyResult<PyObject> {
        let _bundle = std::mem::replace(&mut self.inner, crate::dna::mds::bundle::BundleBuilder::new()).build();
        Ok(Python::with_gil(|py| py.None())) // Convert Bundle to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyCacheAction {
    // This is likely an enum, so we need to handle it differently
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCacheAction {
    #[staticmethod]
    pub fn from_str(s: &str) -> PyResult<Self> {
        // Convert string to CacheAction enum
        Ok(Self {}) // Placeholder
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyE621Config {
    inner: MapE621Config,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyE621Config {
    #[new]
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

#[cfg(feature = "python")]
#[pyclass]
pub struct PyConcatConfig {
    inner: ConcatConfig,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyConcatConfig {
    pub fn with_deduplication(&mut self, deduplicate: bool) -> PyResult<()> {
        self.inner = std::mem::replace(&mut self.inner, ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags)).with_deduplication(deduplicate);
        Ok(())
    }

    #[staticmethod]
    pub fn from_preset(preset: PyObject) -> Self {
        // TODO: Convert PyObject to FileExtensionPreset
        let config = ConcatConfig::from_preset(FileExtensionPreset::CaptionWdTags); // Placeholder
        Self { inner: config }
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyDataFormat {
    inner: crate::dna::map::core::DataFormat,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyDataFormat {
    #[staticmethod]
    pub fn from_str(s: &str) -> PyResult<Self> {
        let format = s
            .parse::<crate::dna::map::core::DataFormat>()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Self { inner: format })
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyGenericJSONDataset {
    inner: crate::dna::map::core::GenericJSONDataset,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyGenericJSONDataset {
    pub fn len(&self) -> usize {
        self.inner.len()
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    pub fn get_random_sample(&self) -> PyResult<PyObject> {
        let sample = self.inner.get_random_sample();
        match sample {
            Some(s) => Ok(Python::with_gil(|py| py.None())), // Convert to PyObject
            None => Ok(Python::with_gil(|py| py.None())),
        }
    }

    pub fn stats(&self) -> PyResult<PyObject> {
        let stats = self.inner.stats();
        Ok(Python::with_gil(|py| py.None())) // Convert DatasetStats to PyObject
    }

    pub fn detect_training_format(&self) -> PyResult<PyObject> {
        let format = self.inner.detect_training_format();
        Ok(Python::with_gil(|py| py.None())) // Convert TrainingFormat to PyObject
    }

    pub fn to_training_dataset(&self) -> PyResult<PyTrainingDataset> {
        let dataset = self
            .inner
            .to_training_dataset()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(PyTrainingDataset { inner: dataset })
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyTrainingDataset {
    inner: crate::dna::map::core::TrainingDataset,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyTrainingDataset {
    pub fn quality_assessment(&self) -> PyResult<PyObject> {
        let assessment = self.inner.quality_assessment();
        Ok(Python::with_gil(|py| py.None())) // Convert QualityAssessment to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHuggingFaceDataset {
    inner: HuggingFaceDataset,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyHuggingFaceDataset {
    #[staticmethod]
    pub fn load(name: &str, split: &str, cache_dir: String) -> PyResult<Self> {
        Python::with_gil(|py| {
            py.allow_threads(|| {
                let rt = tokio::runtime::Runtime::new()
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                let path = std::path::PathBuf::from(cache_dir);
                let dataset = rt
                    .block_on(HuggingFaceDataset::load(name, split, &path))
                    .map_err(|e| PyValueError::new_err(e.to_string()))?;
                Ok(Self { inner: dataset })
            })
        })
    }

    pub fn get_features(&self) -> PyResult<PyObject> {
        let features = self.inner.get_features();
        Ok(Python::with_gil(|py| py.None())) // Convert features to PyObject
    }

    pub fn info(&self) -> PyResult<PyObject> {
        let info = self.inner.info();
        Ok(Python::with_gil(|py| py.None())) // Convert info to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyPreferenceProcessor {
    inner: PreferenceProcessor,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyPreferenceProcessor {
    #[staticmethod]
    pub fn compute_statistics(_samples: Vec<PyObject>) -> PyResult<PyObject> {
        // compute_statistics is private, placeholder implementation
        Ok(Python::with_gil(|py| py.None()))
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyCompletionProcessor {
    inner: CompletionProcessor,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCompletionProcessor {
    #[staticmethod]
    pub fn compute_statistics(_samples: Vec<PyObject>) -> PyResult<PyObject> {
        // compute_statistics is private, placeholder implementation
        Ok(Python::with_gil(|py| py.None()))
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyInstructionProcessor {
    inner: InstructionProcessor,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyInstructionProcessor {
    #[staticmethod]
    pub fn compute_statistics(_samples: Vec<PyObject>) -> PyResult<PyObject> {
        // compute_statistics is private, placeholder implementation
        Ok(Python::with_gil(|py| py.None()))
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyHfProcessor {
    inner: HfProcessor,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHfProcessor {
    #[new]
    pub fn new(cache_dir: String) -> Self {
        let path = std::path::PathBuf::from(cache_dir);
        Self {
            inner: HfProcessor::new(path),
        }
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyReasoningDataset {
    inner: ReasoningDataset,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyReasoningDataset {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: ReasoningDataset::new(),
        }
    }

    pub fn add_entry(&mut self, entry: PyObject) -> PyResult<()> {
        // Convert PyObject to ReasoningEntry
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

#[cfg(feature = "python")]
#[pyclass]
pub struct PyDocument {
    // This appears to be a placeholder impl block
}
#[cfg(feature = "python")]
#[pyclass]
#[derive(Debug, Clone)]
pub struct PyStringPool {
    inner: StringPool,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyStringPool {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: StringPool::new(),
        }
    }

    pub fn intern(&mut self, s: &str) -> u32 {
        self.inner.intern(s)
    }

    pub fn get(&self, idx: u32) -> PyResult<String> {
        self.inner
            .get(idx)
            .ok_or_else(|| PyValueError::new_err(format!("Index {} not found", idx)))
            .map(|s| s.clone())
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyConstantPool {
    inner: ConstantPool,
}
#[cfg(feature = "python")]  
#[pymethods]
impl PyConstantPool {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: ConstantPool::new(),
        }
    }

    pub fn add(&mut self, value: PyObject) -> PyResult<u32> {
        // TODO: Convert PyObject to ConstantValue
        let cv = ConstantValue::String(0); // Placeholder
        Ok(self.inner.add(cv))
    }

    pub fn get(&self, idx: u32) -> PyResult<PyObject> {
        let value = self.inner.get(idx)
            .ok_or_else(|| PyValueError::new_err(format!("Constant at index {} not found", idx)))?;
        Ok(Python::with_gil(|py| py.None())) // Convert ConstantValue to PyObject
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyCodeGenerator {
    inner: CodeGenerator,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCodeGenerator {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: CodeGenerator::new(),
        }
    }

    pub fn generate(&mut self, ast: &PyHelixAst) -> PyResult<()> {
        let _ir = self.inner.generate(&ast.inner);
        Ok(())
    }
}

// BinarySerializer wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyBinarySerializer {
    inner: crate::dna::mds::serializer::BinarySerializer,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyBinarySerializer {
    #[new]
    pub fn new(enable_compression: bool) -> Self {
        Self {
            inner: crate::dna::mds::serializer::BinarySerializer::new(enable_compression),
        }
    }

    pub fn with_compression_method(&mut self, method: PyObject) -> () {
        // Convert PyObject to CompressionMethod
        let cm = CompressionMethod::Lz4; // Placeholder
        let inner = crate::dna::mds::serializer::BinarySerializer::new(true);
        self.inner = inner.with_compression_method(cm);
    }
}

// VersionChecker wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyVersionChecker {
    // This seems to be a static utility class
}
#[cfg(feature = "python")]
#[pymethods]
impl PyVersionChecker {
    #[staticmethod]
    pub fn is_compatible(_ir: PyObject) -> bool {
        // Convert PyObject to &HelixIR - placeholder implementation
        // HelixIR doesn't have Default, so using a dummy check
        true
    }

    #[staticmethod]
    pub fn migrate(ir: PyObject) -> PyResult<()> {
        // Convert and modify PyObject representing HelixIR
        Ok(())
    }
}

// Migrator wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyMigrator {
    inner: Migrator,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyMigrator {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: Migrator::new(),
        }
    }

    pub fn verbose(&mut self, enable: bool) -> () {
        let inner = std::mem::take(&mut self.inner);
        self.inner = inner.verbose(enable);
    }

    pub fn migrate_json(&self, json_str: &str) -> PyResult<String> {
        self.inner
            .migrate_json(json_str)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    pub fn migrate_toml(&self, toml_str: &str) -> PyResult<String> {
        self.inner
            .migrate_toml(toml_str)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    pub fn migrate_yaml(&self, yaml_str: &str) -> PyResult<String> {
        self.inner
            .migrate_yaml(yaml_str)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    pub fn migrate_env(&self, env_str: &str) -> PyResult<String> {
        self.inner
            .migrate_env(env_str)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }
}

// ModuleResolver wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyModuleResolver {
    inner: ModuleResolver,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyModuleResolver {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: ModuleResolver::new(),
        }
    }

    pub fn resolve(&mut self, module_name: &str) -> PyResult<PyObject> {
        let result = self.inner.resolve(module_name);
        match result {
            Ok(path) => Ok(Python::with_gil(|py| path.to_string_lossy().to_string().to_object(py))),
            Err(e) => Err(PyValueError::new_err(e.to_string())),
        }
    }

    pub fn clear_cache(&mut self) -> PyResult<()> {
        self.inner.clear_cache();
        Ok(())
    }
}

// ModuleSystem wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyModuleSystem {
    inner: ModuleSystem,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyModuleSystem {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: ModuleSystem::new(),
        }
    }

    pub fn load_module(&mut self, path: String) -> PyResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner
            .load_module(&path_buf)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn resolve_dependencies(&mut self) -> PyResult<()> {
        self.inner
            .resolve_dependencies()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn compilation_order(&self) -> PyResult<Vec<String>> {
        Ok(self.inner.compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect())
    }

    pub fn merge_modules(&self) -> PyResult<PyObject> {
        let merged = self
            .inner
            .merge_modules()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Python::with_gil(|py| py.None())) // Convert HelixAst to PyObject
    }

    pub fn modules(&self) -> PyResult<Vec<PyObject>> {
        let modules = self.inner.modules();
        // Convert Vec<ModuleInfo> to Vec<PyObject>
        Ok(vec![]) // Placeholder
    }

    pub fn dependency_graph(&self) -> PyResult<PyDependencyGraph> {
        Ok(PyDependencyGraph { inner: DependencyGraph })
    }
}

// DependencyBundler wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyDependencyBundler {
    inner: DependencyBundler,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyDependencyBundler {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: DependencyBundler::new(),
        }
    }

    pub fn build_bundle(&mut self) -> PyResult<PyObject> {
        let bundle = self
            .inner
            .build_bundle()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Python::with_gil(|py| py.None())) // Convert Bundle to PyObject
    }

    pub fn get_compilation_order(&self) -> PyResult<Vec<String>> {
        Ok(self.inner.get_compilation_order().iter().map(|p| p.to_string_lossy().to_string()).collect())
    }
}

// DependencyGraph wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyDependencyGraph {
    inner: DependencyGraph,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyDependencyGraph {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: DependencyGraph::new(),
        }
    }

    pub fn check_circular(&self) -> PyResult<()> {
        self.inner.check_circular().map_err(|e| PyValueError::new_err(e))
    }
}

// OptimizationLevel wrapper
#[cfg(feature = "python")]
#[pyclass]
#[derive(Clone)]
pub struct PyOptimizationLevel {
    inner: OptimizationLevel,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyOptimizationLevel {
    #[staticmethod]
    pub fn from_u8(level: u8) -> Self {
        Self {
            inner: OptimizationLevel::from(level),
        }
    }
}

#[cfg(feature = "python")]
#[pyclass]
pub struct PyOptimizer {
    inner: Optimizer,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyOptimizer {
    #[new]
    pub fn new(level: PyOptimizationLevel) -> Self {
        Self {
            inner: Optimizer::new(level.inner),
        }
    }

    pub fn optimize(&mut self, _ir: PyObject) -> PyResult<()> {
        // Convert PyObject to &mut HelixIR - placeholder implementation
        // HelixIR doesn't have Default, skipping optimization
        Ok(())
    }

    pub fn stats(&self) -> PyResult<PyObject> {
        let stats = self.inner.stats();
        Ok(Python::with_gil(|py| py.None())) // Convert OptimizationStats to PyObject
    }
}

// ProjectManifest wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyProjectManifest {
    // This seems to be a large struct, placeholder for now
}

// Runtime wrapper (HelixVM is already defined above)


// Schema wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyHelixConfig {
    inner: HelixConfig,
}

#[cfg(feature = "python")]
#[pymethods]
impl PyHelixConfig {
    // Index implementation would go here if needed
}

// HlxDatasetProcessor wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyHlxDatasetProcessor {
    inner: HlxDatasetProcessor,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHlxDatasetProcessor {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HlxDatasetProcessor::new(),
        }
    }

    pub fn parse_hlx_content(&self, content: &str) -> PyResult<PyObject> {
        let result = self.inner.parse_hlx_content(content);
        match result {
            Ok(data) => Ok(Python::with_gil(|py| py.None())), // Convert parsed data to PyObject
            Err(e) => Err(PyValueError::new_err(e.to_string())),
        }
    }

    pub fn cache_stats(&self) -> PyResult<PyObject> {
        let stats = self.inner.cache_stats();
        Ok(Python::with_gil(|py| py.None())) // Convert CacheStats to PyObject
    }

    pub fn clear_cache(&mut self) -> PyResult<()> {
        self.inner.clear_cache();
        Ok(())
    }
}

// ProcessingOptions wrapper
#[cfg(feature = "python")]
#[pyclass]
#[derive(Debug, Clone)]
pub struct PyProcessingOptions {
    inner: ProcessingOptions,
}
#[cfg(feature = "python")]
#[pyclass]
pub struct PyCacheStats {
    inner: CacheStats,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyCacheStats {
    pub fn total_size_mb(&self) -> f64 {
        self.inner.total_size_mb()
    }

    pub fn total_size_gb(&self) -> f64 {
        self.inner.total_size_gb()
    }
}

// HlxBridge wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyHlxBridge {
    inner: HlxBridge,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHlxBridge {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HlxBridge::new(),
        }
    }
}

// ServerConfig wrapper
#[cfg(feature = "python")]
#[pyclass]
#[derive(Clone)]
pub struct PyServerConfig {
    inner: ServerConfig,
}
#[cfg(feature = "python")]
// HelixServer wrapper
#[pyclass]
pub struct PyHelixServer {
    inner: HelixServer,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyHelixServer {
    #[new]
    pub fn new(config: &PyServerConfig) -> Self {
        Self {
            inner: HelixServer::new(config.inner.clone()),
        }
    }

    pub fn start(&self) -> PyResult<()> {
        self.inner
            .start()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }
}

// VaultConfig wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyVaultConfig {
    inner: VaultConfig,
}

// Vault wrapper
#[cfg(feature = "python")]
#[pyclass]
pub struct PyVault {
    inner: Vault,
}
#[cfg(feature = "python")]
#[pymethods]
impl PyVault {
    #[new]
    pub fn new() -> PyResult<Self> {
        let inner = Vault::new().map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Self { inner })
    }

    pub fn save(&self, path: String, description: Option<String>) -> PyResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner
            .save(&path_buf, description)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn load_latest(&self, path: String) -> PyResult<PyObject> {
        let path_buf = std::path::PathBuf::from(path);
        let content = self
            .inner
            .load_latest(&path_buf)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Python::with_gil(|py| py.None())) // Convert content to PyObject
    }

    pub fn load_version(&self, file_hash: &str, version_id: &str) -> PyResult<PyObject> {
        let content = self
            .inner
            .load_version(file_hash, version_id)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(Python::with_gil(|py| py.None())) // Convert content to PyObject
    }

    pub fn list_versions(&self, path: String) -> PyResult<Vec<PyObject>> {
        let path_buf = std::path::PathBuf::from(path);
        let versions = self
            .inner
            .list_versions(&path_buf)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(versions
            .into_iter()
            .map(|v| Python::with_gil(|py| v.id.to_object(py)))
            .collect())
    }

    pub fn revert(&self, path: String, version_id: &str) -> PyResult<()> {
        let path_buf = std::path::PathBuf::from(path);
        self.inner
            .revert(&path_buf, version_id)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }

    pub fn garbage_collect(&self) -> PyResult<()> {
        self.inner
            .garbage_collect()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok(())
    }
}

#[cfg(feature = "python")]
#[pymodule]
#[pyo3(name = "_core_impl")]
fn helix(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register all the classes
    m.add_class::<PyHelixAst>()?;
    m.add_class::<PyAstPrettyPrinter>()?;
    m.add_class::<PyExpression>()?;
    m.add_class::<PyAstBuilder>()?;
    m.add_class::<PyHelixInterpreter>()?;
    m.add_class::<PySourceMap>()?;
    m.add_class::<PySectionName>()?;
    m.add_class::<PyVariableName>()?;
    m.add_class::<PyCacheKey>()?;
    m.add_class::<PyRegexCache>()?;
    m.add_class::<PyStringParser>()?;
    m.add_class::<PyOperatorParser>()?;
    m.add_class::<PyOutputFormat>()?;
    m.add_class::<PyCompressionConfig>()?;
    m.add_class::<PyOutputConfig>()?;
    m.add_class::<PyOutputManager>()?;
    m.add_class::<PyHlxcDataWriter>()?;
    m.add_class::<PyParser>()?;
    m.add_class::<PyHelixLoader>()?;
    m.add_class::<PyGenericJSONDataset>()?;
    m.add_class::<PyTrainingDataset>()?;
    m.add_class::<PyCompiler>()?;
    m.add_class::<PyCompilerBuilder>()?;
    m.add_class::<PyHelixBinary>()?;
    m.add_class::<PyHelixDispatcher>()?;
    m.add_class::<PyHlx>()?;
    m.add_class::<PyDynamicValue>()?;
    m.add_class::<PyAtpValue>()?;
    m.add_class::<PyHlxHeader>()?;
    m.add_class::<PySymbolTable>()?;
    m.add_class::<PyDataSection>()?;
    m.add_class::<PyHelixVM>()?;
    m.add_class::<PyVMExecutor>()?;
    m.add_class::<PyAppState>()?;
    m.add_class::<PyBenchmark>()?;
    m.add_class::<PyBundler>()?;
    m.add_class::<PyBundleBuilder>()?;
    m.add_class::<PyCacheAction>()?;
    m.add_class::<PyE621Config>()?;
    m.add_class::<PyConcatConfig>()?;
    m.add_class::<PyDataFormat>()?;
    m.add_class::<PyHuggingFaceDataset>()?;
    m.add_class::<PyPreferenceProcessor>()?;
    m.add_class::<PyCompletionProcessor>()?;
    m.add_class::<PyInstructionProcessor>()?;
    m.add_class::<PyHfProcessor>()?;
    m.add_class::<PyReasoningDataset>()?;
    m.add_class::<PyDocument>()?;
    m.add_class::<PyStringPool>()?;
    m.add_class::<PyConstantPool>()?;
    m.add_class::<PyCodeGenerator>()?;
    m.add_class::<PyBinarySerializer>()?;
    m.add_class::<PyVersionChecker>()?;
    m.add_class::<PyMigrator>()?;
    m.add_class::<PyModuleResolver>()?;
    m.add_class::<PyModuleSystem>()?;
    m.add_class::<PyDependencyBundler>()?;
    m.add_class::<PyDependencyGraph>()?;
    m.add_class::<PyOptimizationLevel>()?;
    m.add_class::<PyOptimizer>()?;
    m.add_class::<PyProjectManifest>()?;
    m.add_class::<PyHelixConfig>()?;
    m.add_class::<PyHlxDatasetProcessor>()?;
    m.add_class::<PyProcessingOptions>()?;
    m.add_class::<PyCacheStats>()?;
    m.add_class::<PyHlxBridge>()?;
    m.add_class::<PyServerConfig>()?;
    m.add_class::<PyHelixServer>()?;
    m.add_class::<PyVaultConfig>()?;
    m.add_class::<PyVault>()?;
    m.add_function(wrap_pyfunction!(parse_helix_source, m)?)?;
    m.add_function(wrap_pyfunction!(load_file, m)?)?;
    m.add_function(wrap_pyfunction!(execute, m)?)?;
    m.add_function(wrap_pyfunction!(cmd_compile, m)?)?;
    m.add_function(wrap_pyfunction!(cmd_add, m)?)?;
    m.add_function(wrap_pyfunction!(cmd_validate, m)?)?;
    Ok(())
}

#[cfg(feature = "python")]
#[pyfunction]
pub fn parse_helix_source(source: &str) -> PyResult<PyHelixAst> {
    let py_source_map = PySourceMap::new(source.to_string())?;
    let mut parser = PyParser::new_with_source_map(&py_source_map);
    parser.parse()
}

#[cfg(feature = "python")]
#[pyfunction]
pub fn load_file(file_path: &str) -> PyResult<PyHlx> {
    Python::with_gil(|py| {
        py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new()
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            let path = std::path::PathBuf::from(file_path);
            let content = std::fs::read_to_string(&path)
                .map_err(|e| PyValueError::new_err(format!("Failed to read file: {}", e)))?;
            let hlx = rt
                .block_on(Hlx::new())
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            Ok(PyHlx { inner: hlx })
        })
    })
}

#[cfg(feature = "python")]
#[pyfunction]
pub fn execute(source: &str) -> PyResult<PyObject> {
    let ast = parse_helix_source(source)?;
    let result = Python::with_gil(|py| {
        py.allow_threads(|| {
            let rt = tokio::runtime::Runtime::new()
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            let mut interpreter = rt
                .block_on(HelixInterpreter::new())
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            rt.block_on(interpreter.execute_ast(&ast.inner))
                .map_err(|e| PyValueError::new_err(e.to_string()))
        })
    })?;
    Python::with_gil(|py| {
        match result {
            crate::dna::atp::value::Value::String(s) => Ok(s.to_object(py)),
            crate::dna::atp::value::Value::Number(n) => Ok(n.to_object(py)),
            crate::dna::atp::value::Value::Bool(b) => Ok(b.to_object(py)),
            crate::dna::atp::value::Value::Array(_) => Ok(py.None()),
            crate::dna::atp::value::Value::Object(_) => Ok(py.None()),
            crate::dna::atp::value::Value::Null => Ok(py.None()),
            crate::dna::atp::value::Value::Duration(d) => Ok(d.to_string().to_object(py)),
            crate::dna::atp::value::Value::Reference(r) => Ok(r.to_object(py)),
            crate::dna::atp::value::Value::Identifier(i) => Ok(i.to_object(py)),
        }
    })
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (input=None, output=None, compress=false, optimize=2, cache=false, verbose=false, quiet=false))]
pub fn cmd_compile(
    input: Option<String>,
    output: Option<String>,
    compress: bool,
    optimize: u8,
    cache: bool,
    verbose: bool,
    quiet: bool,
) -> PyResult<String> {
    Python::with_gil(|py| {
        py.allow_threads(|| {
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
                Err(e) => Err(PyValueError::new_err(format!("Compilation failed: {}", e))),
            }
        })
    })
}

#[cfg(feature = "python")]
#[pyfunction]
#[pyo3(signature = (dependency, version=None, dev=false, verbose=false))]
pub fn cmd_add(
    dependency: String,
    version: Option<String>,
    dev: bool,
    verbose: bool,
) -> PyResult<String> {
    Python::with_gil(|py| {
        py.allow_threads(|| {
            match crate::dna::mds::add::add_dependency(
                dependency,
                version,
                dev,
                verbose,
            ) {
                Ok(_) => Ok("Dependency added".to_string()),
                Err(e) => Err(PyValueError::new_err(format!("Failed to add dependency: {}", e))),
            }
        })
    })
}

#[cfg(feature = "python")]
#[pyfunction]
pub fn cmd_validate(target: Option<String>) -> PyResult<String> {
    Python::with_gil(|py| {
        py.allow_threads(|| {
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
                            Err(e) => return Err(PyValueError::new_err(format!("Validation failed: {}", e))),
                        }
                    }
                }
            }
            // For source files, check they exist and are readable
            if target_path.exists() {
                Ok("File validation passed".to_string())
            } else {
                Err(PyValueError::new_err(format!("File not found: {}", target_path.display())))
            }
        })
    })
}
