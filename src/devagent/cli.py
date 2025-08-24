"""CLI entry point for DevAgent."""

import click
from rich.console import Console

console = Console()


@click.command()
@click.version_option()
def main():
    """DevAgent - Your local AI coding assistant."""
    console.print("🤖 [bold blue]DevAgent[/bold blue] - Starting conversation mode...")
    console.print("Hi! I'm your coding assistant. What would you like to know or do?")
    
    # TODO: Implement conversation loop
    console.print("⚠️  [yellow]Not implemented yet - coming soon![/yellow]")


if __name__ == "__main__":
    main()