"""LangGraph state machine setup for DevAgent."""

from langgraph.graph import StateGraph, END
from typing import Dict, Any

from .state import AgentState
from ..agents.dispatcher import dispatcher_agent
from ..agents.retriever import retriever_agent
from ..agents.editor import editor_agent
from ..agents.executor import executor_agent
from ..agents.verifier import verifier_agent
from ..agents.reflector import reflector_agent
from ..agents.pr_bot import pr_bot_agent


class DevAgentGraph:
    """Main LangGraph orchestrator for the multi-agent system."""
    
    def __init__(self):
        self.graph = StateGraph(AgentState)
        self._setup_graph()
        self.compiled_graph = None
    
    def _setup_graph(self) -> None:
        """Set up the graph structure with all agents and routing."""
        # Add all agent nodes
        self.graph.add_node("dispatcher", dispatcher_agent)
        self.graph.add_node("retriever", retriever_agent) 
        self.graph.add_node("editor", editor_agent)
        self.graph.add_node("executor", executor_agent)
        self.graph.add_node("verifier", verifier_agent)
        self.graph.add_node("reflector", reflector_agent)
        self.graph.add_node("pr_bot", pr_bot_agent)
        
        # Set up routing - all agents use the same router
        self.graph.add_conditional_edges("dispatcher", self._agent_router)
        self.graph.add_conditional_edges("retriever", self._agent_router)
        self.graph.add_conditional_edges("editor", self._agent_router)
        self.graph.add_conditional_edges("executor", self._agent_router)
        self.graph.add_conditional_edges("verifier", self._agent_router)
        self.graph.add_conditional_edges("reflector", self._agent_router)
        
        # PR Bot ends the workflow
        self.graph.add_edge("pr_bot", END)
        
        # Set entry point
        self.graph.set_entry_point("dispatcher")
    
    def _agent_router(self, state: AgentState) -> str:
        """Route to the next agent based on current_agent field."""
        current_agent = state.get("current_agent", "dispatcher")
        
        # Map agent names to valid node names
        valid_agents = {
            "dispatcher", "retriever", "editor", "executor", 
            "verifier", "reflector", "pr_bot"
        }
        
        if current_agent == "end":
            return END
        elif current_agent in valid_agents:
            return current_agent
        else:
            # Default fallback
            return "dispatcher"
    
    def compile(self):
        """Compile the graph for execution."""
        if not self.compiled_graph:
            self.compiled_graph = self.graph.compile()
        return self.compiled_graph
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input through the agent workflow."""
        # Initialize state
        initial_state = {
            "goal": user_input,
            "user_intent": "",
            "plan": {},
            "context": "",
            "diff": "",
            "run_result": {},
            "verdict": "",
            "iter": 0,
            "current_agent": "dispatcher",
            "error_msg": "",
            "response": None,
            "pr_url": None,
            "conversation_history": None
        }
        
        try:
            # Execute the workflow
            compiled_graph = self.compile()
            result = compiled_graph.invoke(initial_state)
            
            # Check if there was an error in the workflow
            if result.get("error_msg") and result.get("current_agent") == "end":
                # Error occurred - return to initial state for next input
                return {
                    "response": result.get("response", f"Error occurred: {result.get('error_msg', 'Unknown error')}"),
                    "state": self._reset_to_initial_state()
                }
            
            # Extract response from final state
            response = result.get("response", f"Processed: '{user_input}' (workflow completed)")
            
            return {
                "response": response,
                "state": result
            }
            
        except Exception as e:
            # Handle any unhandled exceptions - return to initial state
            return {
                "response": f"❌ Unexpected error: {str(e)}\n\nReturning to initial state. You can try again.",
                "state": self._reset_to_initial_state()
            }
    
    def _reset_to_initial_state(self) -> Dict[str, Any]:
        """Reset to clean initial state for next input."""
        return {
            "goal": "",
            "user_intent": "",
            "plan": {},
            "context": "",
            "diff": "",
            "run_result": {},
            "verdict": "",
            "iter": 0,
            "current_agent": "dispatcher",
            "error_msg": "",
            "response": None,
            "pr_url": None,
            "conversation_history": None
        }