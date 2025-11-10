use clap::{Parser, Subcommand};
use std::process;
use helix::dna::cmd;
use anyhow::anyhow;

#[derive(Parser)]
#[command(name = "hlx")]
#[command(version = env!("CARGO_PKG_VERSION"))]
#[command(about = "HELIX Compiler - Configuration without the pain")]
#[command(long_about = None)]
pub struct Cli {
    #[arg(short, long, global = true)]
    verbose: bool,
    #[arg(short, long, global = true)]
    quiet: bool,
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    /// Add new files or entries
    Add(cmd::add::AddArgs),
    /// Benchmark project
    Bench(cmd::bench::BenchArgs),
    /// Bundle project files
    Bundle(cmd::bundle::BundleArgs),
    /// Manage cache
    Cache(cmd::cache::CacheArgs),
    /// Clean project
    Clean(cmd::clean::CleanArgs),
    /// Compile project
    Compile(cmd::compile::CompileArgs),
    /// Shell completions
    Completions(cmd::completions::CompletionsArgs),
    /// Dataset operations
    Dataset(cmd::dataset::DatasetArgs),
    /// Show diff between files or versions
    Diff(cmd::diff::DiffArgs),
    /// Run diagnostics
    Doctor(cmd::doctor::DoctorArgs),
    /// Export data or files
    Export(cmd::export::ExportArgs),
    /// Filter operations
    Filter(cmd::filter::FilterArgs),
    /// Format code
    Fmt(cmd::fmt::FmtArgs),
    /// Generate code or files
    Generate(cmd::generate::GenerateArgs),
    /// Import data or files
    Import(cmd::import::ImportArgs),
    /// Show project or file info
    Info(cmd::info::InfoArgs),
    /// Initialize new project
    Init(cmd::init::InitArgs),
    /// Lint code
    Lint(cmd::lint::LintArgs),
    /// Optimize project or files
    /// 
    Optimize(cmd::optimizer::OptimizeArgs),
    /// Publish project
    Publish(cmd::publish::PublishArgs),
    /// Remove files or entries
    Remove(cmd::rm::RemoveArgs),
    /// Reset project or configuration to default state
    Reset(cmd::reset::ResetArgs),
    /// Schema operations
    Schema(cmd::schema::SchemaArgs),
    /// Search operations
    Search(cmd::search::SearchArgs),
    /// Serve project
    Serve(cmd::serve::ServeArgs),
    /// Sign files or releases
    Sign(cmd::sign::SignArgs),
    /// Test project
    Test(cmd::test::TestArgs),
    /// Validate project or files
    Validate(cmd::validate::ValidateArgs),
    /// Vault - Version control for HLX files
    Vlt(cmd::vlt::VltArgs),
    /// Watch files for changes
    Watch(cmd::watch::WatchArgs),
    /// Workflow operations
    Workflow(cmd::workflow::WorkflowArgs),
    /// Launch the Helix TUI experience
    Tui,
}

#[tokio::main]
async fn main() {
    let cli = Cli::parse();
    let result = match cli.command {
        Some(Commands::Add(args)) => cmd::add::run(args).await,
        Some(Commands::Bench(args)) => cmd::bench::run(args),
        Some(Commands::Bundle(args)) => cmd::bundle::run(args),
        Some(Commands::Cache(args)) => cmd::cache::run(args),
        Some(Commands::Clean(args)) => cmd::clean::run(args).await,
        Some(Commands::Compile(args)) => cmd::compile::run(args),
        Some(Commands::Completions(args)) => cmd::completions::run(args),
        Some(Commands::Dataset(args)) => cmd::dataset::run(args).await,
        Some(Commands::Diff(args)) => cmd::diff::run(args),
        Some(Commands::Doctor(args)) => cmd::doctor::run(args),
        Some(Commands::Export(args)) => cmd::export::run(args),
        Some(Commands::Filter(args)) => cmd::filter::run(args).await,
        Some(Commands::Fmt(args)) => cmd::fmt::run(args),
        Some(Commands::Generate(args)) => cmd::generate::run(args),
        Some(Commands::Import(args)) => cmd::import::run(args).await,
        Some(Commands::Info(args)) => cmd::info::run(args),
        Some(Commands::Init(args)) => cmd::init::run(cmd::init::InitInstallArgs::Init(args)),
        Some(Commands::Lint(args)) => cmd::lint::run(args).await,
        Some(Commands::Optimize(args)) => cmd::optimizer::run(args),
        Some(Commands::Publish(args)) => cmd::publish::run(args),
        Some(Commands::Remove(args)) => cmd::rm::run(args).await,
        Some(Commands::Reset(args)) => cmd::reset::run(args).await,
        Some(Commands::Schema(args)) => cmd::schema::run(args),
        Some(Commands::Search(args)) => cmd::search::run(args),
        Some(Commands::Serve(args)) => cmd::serve::run(args),
        Some(Commands::Sign(args)) => cmd::sign::run(args),
        Some(Commands::Test(args)) => cmd::test::run(args).await,
        Some(Commands::Validate(args)) => cmd::validate::run(args),
        Some(Commands::Vlt(args)) => cmd::vlt::run(args).map_err(|e| anyhow!("Vault error: {}", e)),
        Some(Commands::Watch(args)) => cmd::watch::run(args),
        Some(Commands::Workflow(args)) => cmd::workflow::run(args),
        Some(Commands::Tui) => helix::dna::vlt::tui::launch().map_err(|e| anyhow!("TUI error: {}", e)),
        None => helix::dna::vlt::tui::launch().map_err(|e| anyhow!("TUI error: {}", e)),
    };
    if let Err(e) = result {
        eprintln!("Error: {}", e);
        process::exit(1);
    }
}

