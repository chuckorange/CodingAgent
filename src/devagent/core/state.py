"""State management for DevAgent conversations."""

from typing import TypedDict, Literal, Optional, Dict, Any, List


class AgentState(TypedDict):
    """State shared across all agents in the conversation."""
    
    # User input and conversation
    goal: str
    conversation_history: List[Dict[str, str]]
    user_intent: Optional[Literal["explore", "explain", "feature", "fix", "pr"]]
    
    # Planning and execution
    plan: Dict[str, Any]
    context: str
    diff: Optional[str]
    run_result: Optional[Dict[str, Any]]
    
    # Flow control
    verdict: Optional[Literal["pass", "fail", "error"]]
    iter: int
    current_agent: str
    error_msg: Optional[str]
    
    # Output
    response: Optional[str]
    pr_url: Optional[str]