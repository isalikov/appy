//! `appy` — the Appy command-line interface.

mod tui;

use anyhow::Result;
use clap::{Parser, Subcommand};

/// Greeting printed by the default command.
pub const GREETING: &str = "Hello from Appy";

#[derive(Debug, Parser)]
#[command(name = "appy", version, about, propagate_version = true)]
struct Cli {
    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Print the greeting (default).
    Hello,
    /// Open the interactive terminal UI.
    Tui,
}

fn main() -> Result<()> {
    match Cli::parse().command.unwrap_or(Command::Hello) {
        Command::Hello => println!("{GREETING}"),
        Command::Tui => tui::run()?,
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::CommandFactory;

    #[test]
    fn cli_definition_is_valid() {
        Cli::command().debug_assert();
    }

    #[test]
    fn defaults_to_hello() {
        let cli = Cli::parse_from(["appy"]);
        assert!(cli.command.is_none());
    }
}
