"""CLI entry point for DevAgent."""

import click
from rich.console import Console
from rich.prompt import Prompt

console = Console()


@click.command()
@click.version_option()
def main():
    """DevAgent - Your local AI coding assistant."""
    console.print("🤖 [bold blue]DevAgent[/bold blue] - Starting conversation mode...")
    console.print("Hi! I'm your coding assistant. What would you like to know or do?")
    console.print("[dim]Type 'exit' or 'quit' to end the conversation.[/dim]")
    console.print()
    
    while True:
        try:
            user_input = Prompt.ask("👤 You")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("👋 Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            # TODO: Process user input through LangGraph agents
            console.print("🤖 [bold blue]DevAgent[/bold blue]: I understand you want to:")
            console.print(f"   '{user_input}'")
            console.print("   [yellow]But I'm still learning how to help with that![/yellow]")
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
            break
        except EOFError:
            console.print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()