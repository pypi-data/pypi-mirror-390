pub mod dna {
    pub mod atp;
    pub mod bch;
    pub mod cmd;
    pub mod exp;
    pub mod hel;
    pub mod map;
    pub mod mds;
    pub mod ngs;
    pub mod ops;
    pub mod out;
    pub mod tst;
    pub mod compiler;
    pub mod vlt;
}
pub use dna::atp::*;
pub use dna::bch::*;
pub use dna::cmd::*;
pub use dna::exp::*;
pub use dna::hel::*;
pub use dna::map::*;
pub use dna::mds::*;
pub use dna::ngs::*;
pub use dna::ops::*;
pub use dna::out::*;
pub use dna::tst::*;
pub use dna::compiler::*;
pub use dna::compiler::Compiler;
pub use dna::mds::optimizer::OptimizationLevel;
pub use dna::hel::dna_hlx::Hlx;
pub use dna::atp::value::Value as DnaValue;
pub use dna::vlt::Vault;
pub use dna::atp::ast::*;
pub use dna::atp::interpreter::*;
pub use dna::atp::lexer::*;
pub use dna::atp::output::*;
pub use dna::atp::parser::*;
pub use dna::atp::types::*;
pub use dna::atp::value::*;
pub use dna::hel::binary::*;
pub use dna::hel::dispatch::*;
pub use dna::hel::dna_hlx::*;
pub use dna::hel::error::*;
pub use dna::hel::hlx::*;
pub use dna::map::core::*;
pub use dna::map::hf::*;
pub use dna::map::reasoning::*;
pub use dna::mds::a_example::{Document, Embedding, Metadata};
pub use dna::mds::benches::*;
pub use dna::mds::bundle::*;
pub use dna::mds::cache::*;
pub use dna::mds::caption::*;
pub use dna::mds::codegen::*;
pub use dna::mds::concat::*;
pub use dna::mds::config::*;
pub use dna::mds::decompile::*;
pub use dna::mds::filter::*;
pub use dna::mds::migrate::*;
pub use dna::mds::modules::*;
pub use dna::mds::optimizer::*;
pub use dna::mds::project::*;
pub use dna::mds::runtime::*;
pub use dna::mds::schema::*;
pub use dna::mds::semantic::*;
pub use dna::mds::serializer::*;
pub use dna::mds::server::*;
pub use dna::mds::watch::*;
pub use dna::out::helix_format::*;
pub use dna::out::hlx_config_format::*;
pub use dna::out::hlxb_config_format::*;
pub use dna::out::hlxc_format::*;
pub use dna::vlt::tui::*;
pub use dna::vlt::vault::*;
pub use dna::atp::types::{
    HelixConfig, ProjectConfig, AgentConfig, WorkflowConfig, MemoryConfig, ContextConfig,
    CrewConfig, PipelineConfig, RetryConfig, TriggerConfig, StepConfig, Value,
    load_default_config, DataFormat, TrainingFormat, GenericJSONDataset, TrainingDataset,
    TrainingSample, AlgorithmFormat,
};
pub use dna::out::hlxb_config_format::{
    HlxbWriter, HlxbReader, HlxbHeader, HLXB_MAGIC, HLXB_VERSION,
};
pub use dna::atp::ast::{
    HelixAst, Declaration, Expression, Statement, AgentDecl, WorkflowDecl, MemoryDecl,
    ContextDecl, CrewDecl, PipelineDecl,
};
pub use dna::atp::lexer::{Token, SourceLocation};
pub use dna::atp::parser::{Parser, ParseError};
pub use dna::mds::semantic::{SemanticAnalyzer, SemanticError};
pub use dna::mds::codegen::{CodeGenerator, HelixIR};
pub use dna::atp::types::HelixLoader;
pub use dna::mds::server::{HelixServer, ServerConfig};

// Python bindings handle their own imports directly
pub async fn xlh(hlx: &Hlx, operator: &str, params: &str) -> std::result::Result<crate::dna::atp::value::Value, crate::dna::hel::error::HlxError> {
    hlx.execute_operator(operator, params).await
}

pub fn parse(source: &str) -> std::result::Result<HelixAst, ParseError> {
    use crate::dna::atp::lexer::tokenize;
    let tokens = tokenize(source)
        .map_err(|e| ParseError {
            message: format!("Lexer error: {}", e),
            location: None,
            token_index: 0,
            expected: None,
            found: String::new(),
            context: String::new(),
        })?;
    crate::dna::atp::parser::parse(tokens)
}

pub fn validate(ast: &HelixAst) -> std::result::Result<(), String> {
    use crate::dna::mds::semantic::SemanticAnalyzer;
    use crate::dna::mds::semantic::SemanticError;
    let mut analyzer = SemanticAnalyzer::new();
    let result: std::result::Result<(), Vec<SemanticError>> = analyzer.analyze(ast);
    result.map_err(|errors| {
        errors.iter()
            .map(|e| format!("{:?}", e))
            .collect::<Vec<_>>()
            .join("\n")
    })
}

pub fn ast_to_config(ast: HelixAst) -> std::result::Result<HelixConfig, String> {
    crate::dna::mds::config::ast_to_config(ast)
}

pub fn pretty_print(ast: &HelixAst) -> String {
    crate::dna::mds::pretty_print::pretty_print(ast)
}

#[cfg(test)]
mod tests;
#[cfg(test)]
mod bch;
#[cfg(test)]
#[path = "dna/tst/integration_tests.rs"]
mod integration_tests;
