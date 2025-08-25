"""PR Bot agent for version control and GitHub integration."""

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from ..tools.core_tools import PR_BOT_TOOLS


def create_pr_bot_agent(model: BaseChatModel):
    """Create a PR bot agent for version control and GitHub integration.
    
    Args:
        model: LangChain-compatible model for agent reasoning
        
    Returns:
        Configured PR bot agent
    """
    return create_react_agent(
        model=model,
        tools=PR_BOT_TOOLS,
        prompt=(
            "You are a version control and deployment specialist. Your job is to manage git operations and create PRs. "
            "Use bash_tool for git commands, PR creation, and deployment tasks. "
            "Use read_file_tool to examine changes. Handle all aspects of code deployment and version control."
        ),
        name="pr_bot"
    )