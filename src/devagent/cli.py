"""CLI entry point for DevAgent."""

import os
import click
from rich.console import Console
from rich.prompt import Prompt

from .core.graph import DevAgentGraph

console = Console()


@click.command()
@click.version_option()
def main():
    """DevAgent - Your local AI coding assistant."""
    # Get current working directory for codebase context
    current_dir = os.getcwd()
    
    console.print("🤖 [bold blue]DevAgent[/bold blue] - Starting conversation mode...")
    console.print(f"Working directory: [cyan]{current_dir}[/cyan]")
    console.print("Hi! I'm your coding assistant. What would you like to know or do?")
    console.print("[dim]Type 'exit' or 'quit' to end the conversation.[/dim]")
    console.print("[dim]Type 'reset' to start a fresh conversation.[/dim]")
    console.print()
    
    # Initialize the agent graph with current directory context
    agent_graph = DevAgentGraph(working_directory=current_dir)
    
    while True:
        try:
            user_input = Prompt.ask("👤 You")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                agent_graph.reset_conversation()
                console.print("🔄 [yellow]Conversation reset. Starting fresh![/yellow]")
                console.print()
                continue
            
            if not user_input.strip():
                continue
            
            # Process through LangGraph agents
            console.print("🤖 [bold blue]DevAgent[/bold blue]: Let me process that...")
            
            result = agent_graph.process_user_input(user_input)
            response = result.get("response", "No response generated")
            
            console.print(f"🤖 [bold blue]DevAgent[/bold blue]: {response}")
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
            break
        except EOFError:
            console.print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()