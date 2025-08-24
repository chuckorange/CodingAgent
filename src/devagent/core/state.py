"""State management for DevAgent conversations."""

from typing import TypedDict, Literal, Optional, Dict, Any, List


class AgentState(TypedDict):
    """State shared across all agents in the conversation.
    
    Based on SPEC.md requirements for multi-agent workflow state management.
    """
    
    # User input and intent
    goal: str
    user_intent: str  # "explore", "explain", "feature", "fix", "pr"
    
    # Planning and context
    plan: Dict[str, Any]
    context: str
    
    # Code changes and execution
    diff: str
    run_result: Dict[str, Any]
    
    # Flow control and routing  
    verdict: str  # "pass", "fail", "error"
    iter: int
    current_agent: str
    error_msg: str
    
    # Optional output fields
    response: Optional[str]
    pr_url: Optional[str]
    conversation_history: Optional[List[Dict[str, str]]]