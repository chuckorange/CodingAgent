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
            "You are a codebase analysis specialist. You MUST use the available tools to gather real information about the codebase.\n\n"
            
            "**CRITICAL**: ALWAYS use tools before answering. Do not guess or make assumptions. Use bash_tool('pwd') first, then glob_tool to find files, then read_file_tool to examine them.\n\n"
            
            "Follow this process:\n"
            "1. Use bash_tool('pwd') to see current directory\n"
            "2. Use bash_tool('ls -la') to see top-level structure\n"
            "3. Use glob_tool('**/*.py') to find Python files\n"
            "4. Use read_file_tool() to examine key files\n"
            "5. Use grep_tool() to search for specific content if needed\n\n"
            
            "Always use tools to get real information. Never guess or make up file names."
        ),
        name="retriever"
    )