use clap::Args;
use std::path::PathBuf;
use crate::dna::mds::runtime;




#[derive(Args)]
pub struct RunArgs {
    /// Input file path (defaults to current directory)
    #[arg(short, long)]
    pub input: Option<PathBuf>,

    /// Additional arguments
    pub args: Vec<String>,

    /// Optimization level
    #[arg(short = 'O', long, default_value = "2")]
    pub optimize: u8,
}


pub async fn run(args: RunArgs) -> anyhow::Result<()> {
    runtime::run_project(args.input, args.args, args.optimize, false)
}