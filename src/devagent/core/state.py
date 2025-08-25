"""State management for DevAgent conversations."""

from typing import TypedDict, Optional, Dict, Any, List
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State shared across all agents in the supervisor pattern workflow.
    
    Compatible with langgraph-supervisor package state requirements.
    """
    
    # Required by langgraph-supervisor
    messages: List[BaseMessage]  # LangChain message format for supervisor
    
    # DevAgent specific fields
    goal: str                    # Original user request  
    user_intent: str            # Classified intent (set by supervisor)
    
    # Agent work products  
    context: str                # Research/analysis from retriever
    diff: str                   # Code changes from editor
    run_result: Dict[str, Any]  # Test results from executor
    review_result: str          # Analysis from verifier
    
    # Planning and coordination
    plan: Dict[str, Any]        # High-level execution plan
    completed_tasks: List[str]  # Tasks finished by agents
    pending_tasks: List[str]    # Tasks still needed
    
    # Flow control
    max_iterations: int         # Prevent infinite loops
    iteration_count: int        # Current iteration
    is_complete: bool          # Task completion flag
    
    # Error handling and output
    error_msg: str             # Error details
    response: Optional[str]    # Final response to user
    pr_url: Optional[str]      # GitHub PR if created