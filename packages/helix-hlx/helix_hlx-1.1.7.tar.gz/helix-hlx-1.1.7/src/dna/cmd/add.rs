use crate::dna::mds::add::*;
use clap::Args;

#[derive(Args)]
pub struct AddArgs {
    /// Dependency to add
    #[arg(short, long)]
    dependency: String,

    /// Version to add
    #[arg(short, long)]
    version: Option<String>,

    /// Dev dependency (defaults to false)
    #[arg(long)]
    dev: bool,

    /// Verbose output
    #[arg(short, long)]
    verbose: bool,
}

pub async fn run(args: AddArgs) -> anyhow::Result<()> {
    // The `add_dependency` function is imported via the wildcard import above,
    // so we can call it directly without the `add::` prefix.
    add_dependency(args.dependency, args.version, args.dev, args.verbose)
}
