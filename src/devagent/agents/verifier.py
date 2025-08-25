"""Verifier agent for result analysis and decision making."""

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph_supervisor import create_react_agent

from ..tools.core_tools import VERIFIER_TOOLS


def create_verifier_agent(model: BaseChatModel):
    """Create a verifier agent for analyzing results and making decisions.
    
    Args:
        model: LangChain-compatible model for agent reasoning
        
    Returns:
        Configured verifier agent
    """
    return create_react_agent(
        model=model,
        tools=VERIFIER_TOOLS,
        state_modifier=(
            "You are a code review and quality assurance specialist. Your job is to analyze results and make decisions. "
            "Use read_file_tool to examine code and test results, bash_tool to run quality checks. "
            "Provide thorough analysis of code quality, test results, and overall project health."
        )
    )