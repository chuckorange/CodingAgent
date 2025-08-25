"""Editor agent for code generation and file modifications."""

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from ..tools.core_tools import EDITOR_TOOLS


def create_editor_agent(model: BaseChatModel):
    """Create an editor agent for code generation and file modifications.
    
    Args:
        model: LangChain-compatible model for agent reasoning
        
    Returns:
        Configured editor agent
    """
    return create_react_agent(
        model=model,
        tools=EDITOR_TOOLS,
        prompt=(
            "You are a code generation and editing specialist. Your job is to create, modify, and improve code. "
            "Use read_file_tool to understand existing code, write_file_tool to create/modify files, "
            "and bash_tool for file operations. Generate clean, well-documented, and functional code."
        ),
        name="editor"
    )