"""LangGraph state machine setup for DevAgent using langgraph-supervisor."""

from typing import Dict, Any
from langchain_core.messages import HumanMessage

from langgraph_supervisor import create_supervisor
from langchain_ollama import ChatOllama
from .state import AgentState
from .llm import get_langchain_model
from ..agents import (
    create_retriever_agent,
    create_editor_agent,
    create_executor_agent,
    create_verifier_agent,
    create_pr_bot_agent
)



class DevAgentGraph:
    """Main LangGraph orchestrator using langgraph-supervisor pattern."""
    
    def __init__(self, working_directory: str = None):
        self.compiled_graph = None
        self.current_state = None
        self.working_directory = working_directory or "."
        self._setup_graph()
    
    def _setup_graph(self) -> None:
        """Set up the supervisor pattern using create_react_agent."""
        
        # Use ChatOllama directly for better compatibility  
        model = ChatOllama(model="qwen2.5:14b-instruct", temperature=0.2)
        
        # Create specialist agents using dedicated factory functions
        retriever_agent = create_retriever_agent(model)
        editor_agent = create_editor_agent(model)
        executor_agent = create_executor_agent(model)
        verifier_agent = create_verifier_agent(model)
        pr_bot_agent = create_pr_bot_agent(model)
        
        # Create supervisor workflow with react agents
        supervisor_workflow = create_supervisor(
            [
                retriever_agent,
                editor_agent, 
                executor_agent,
                verifier_agent,
                pr_bot_agent
            ],
            model=model,
            prompt=(
                f"You are a software development team supervisor managing specialist agents. "
                f"Working directory: {self.working_directory} "
                f"For codebase analysis, use retriever. "
                f"For code changes, use editor. "
                f"For running tests, use executor. "
                f"For code review, use verifier. "
                f"For git operations, use pr_bot."
            )
        )
        
        self.supervisor_workflow = supervisor_workflow
    
    def compile(self):
        """Compile the graph for execution."""
        if not self.compiled_graph:
            self.compiled_graph = self.supervisor_workflow.compile()
        return self.compiled_graph
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input directly through the supervisor workflow."""
        
        # Use existing state or initialize new one
        if self.current_state is None:
            self.current_state = self._get_initial_state()
        
        # Add new user message to existing conversation
        self.current_state["messages"].append(HumanMessage(content=user_input))
        self.current_state["goal"] = user_input  # Update current goal
        
        try:
            # Execute supervisor workflow with current state
            compiled_graph = self.compile()
            result = compiled_graph.invoke(self.current_state)
            
            # Update current state with result
            self.current_state = result
            
            # Extract final response
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                response = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                response = f"Workflow completed for: '{user_input}'"
            
            return {
                "response": response,
                "state": result
            }
            
        except Exception as e:
            # Handle any unhandled exceptions but preserve conversation context
            error_response = f"❌ Unexpected error: {str(e)}\n\nContinuing with existing context. You can try again."
            return {
                "response": error_response,
                "state": self.current_state
            }
    
    
    def _get_initial_state(self) -> Dict[str, Any]:
        """Get clean initial state for new conversation."""
        return {
            "messages": [],
            "goal": "",
            "user_intent": "",
            "context": f"Working directory: {self.working_directory}",
            "diff": "",
            "run_result": {},
            "review_result": "",
            "plan": {},
            "completed_tasks": [],
            "pending_tasks": [],
            "max_iterations": 10,
            "iteration_count": 0,
            "is_complete": False,
            "error_msg": "",
            "response": None,
            "pr_url": None
        }
    
    def reset_conversation(self) -> None:
        """Manually reset conversation state (useful for starting fresh)."""
        self.current_state = None