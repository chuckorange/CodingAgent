"""Retriever agent for codebase analysis and context gathering."""

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.prebuilt import create_react_agent

from ..tools.core_tools import RETRIEVER_TOOLS


def create_retriever_agent(model: BaseChatModel):
    """Create a retriever agent for codebase search and context gathering.
    
    Args:
        model: LangChain-compatible model for agent reasoning
        
    Returns:
        Configured retriever agent
    """
    return create_react_agent(
        model=model,
        tools=RETRIEVER_TOOLS,
        prompt=(
            "You are a codebase analysis specialist. Your job is to search, read, and understand code structures. "
            "Use glob_tool to find files, read_file_tool to examine code, grep_tool to search for patterns, "
            "and bash_tool for system commands. Provide detailed analysis of codebases and file contents."
        ),
        name="retriever"
    )