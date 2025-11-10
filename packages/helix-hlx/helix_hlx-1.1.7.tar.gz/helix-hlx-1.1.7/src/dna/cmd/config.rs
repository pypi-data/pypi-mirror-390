use clap::Args;

#[derive(Args)]
pub struct ConfigArgs {
    action: String,
    key: Option<String>,
    value: Option<String>,
}