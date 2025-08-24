"""CLI entry point for DevAgent."""

import click
from rich.console import Console
from rich.prompt import Prompt

from .core.graph import DevAgentGraph

console = Console()


@click.command()
@click.version_option()
def main():
    """DevAgent - Your local AI coding assistant."""
    console.print("🤖 [bold blue]DevAgent[/bold blue] - Starting conversation mode...")
    console.print("Hi! I'm your coding assistant. What would you like to know or do?")
    console.print("[dim]Type 'exit' or 'quit' to end the conversation.[/dim]")
    console.print()
    
    # Initialize the agent graph
    agent_graph = DevAgentGraph()
    
    while True:
        try:
            user_input = Prompt.ask("👤 You")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("👋 Goodbye!")
                break
            
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