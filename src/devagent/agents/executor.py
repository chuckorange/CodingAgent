"""Executor agent for code execution and testing."""

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph_supervisor import create_react_agent

from ..tools.core_tools import EXECUTOR_TOOLS


def create_executor_agent(model: BaseChatModel):
    """Create an executor agent for running tests and validating code changes.
    
    Args:
        model: LangChain-compatible model for agent reasoning
        
    Returns:
        Configured executor agent
    """
    return create_react_agent(
        model=model,
        tools=EXECUTOR_TOOLS,
        state_modifier=(
            "You are a code execution and testing specialist. Your job is to run tests and validate code changes. "
            "Use bash_tool to execute tests, run commands, and validate functionality. "
            "Use read_file_tool to examine test files and results. Report on test outcomes and code quality."
        )
    )