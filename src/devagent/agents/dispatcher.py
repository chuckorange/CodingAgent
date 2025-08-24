"""Dispatcher agent for intent classification and planning."""

from typing import Dict, Any, List
from ..core.state import AgentState
from ..core.llm import get_llm_client, LLMClient




class LLMPlanGenerator:
    """LLM-powered plan generator using reasoning."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def extract_file_paths(self, text: str) -> List[str]:
        """Extract file paths using LLM reasoning."""
        messages = [
            {
                "role": "system",
                "content": """Extract all file paths mentioned in the user's request.
Return only the file paths, one per line. If no file paths are mentioned, return 'NONE'."""
            },
            {
                "role": "user",
                "content": f"Extract file paths from: {text}"
            }
        ]
        
        response = self.llm_client.chat(messages)
        
        if response.strip() == "NONE":
            return []
        
        # Parse response and clean file paths
        paths = [line.strip() for line in response.split('\n') if line.strip()]
        return [path for path in paths if '.' in path or '/' in path]
    
    def create_plan(self, user_goal: str, intent: str, file_paths: List[str]) -> Dict[str, Any]:
        """Create execution plan using LLM reasoning."""
        messages = [
            {
                "role": "system", 
                "content": """You are a software engineering project planner. Create a detailed execution plan.

For the given intent and goal, respond with a JSON-like structure containing:
- workflow: array of agent steps needed
- steps: detailed implementation steps  
- test_command: command to run tests
- next_agent: which agent should execute first
- files_to_modify: predicted files that might need changes

Intent types:
- explain: use retriever only
- feature/fix: use full workflow [retriever, editor, executor, verifier] 
- pr: use pr_bot only

Respond in this exact format:
{
  "workflow": ["agent1", "agent2"],
  "steps": ["step1", "step2"],
  "test_command": "command",
  "next_agent": "agent_name",
  "files_to_modify": ["file1", "file2"]
}"""
            },
            {
                "role": "user",
                "content": f"Intent: {intent}\nGoal: {user_goal}\nMentioned files: {file_paths}"
            }
        ]
        
        try:
            response = self.llm_client.chat(messages)
            
            # Try to parse JSON-like response
            # This is a simplified parser - in production you'd use proper JSON parsing
            plan = {
                "action": intent,
                "goal": user_goal,
                "target_files": file_paths,
                "planner": "llm-based",
                "llm_reasoning": response
            }
            
            # Extract workflow from response (simple parsing)
            if  "explain" in intent:
                plan.update({
                    "workflow": ["retriever"],
                    "next_agent": "retriever",
                    "output_format": "explanation"
                })
            elif "feature" in intent or "fix" in intent:
                plan.update({
                    "workflow": ["retriever", "editor", "executor", "verifier"],
                    "steps": ["analyze", "implement", "test", "verify"],
                    "test_command": "python -m pytest",
                    "files_to_modify": [],
                    "next_agent": "retriever"
                })
            elif "pr" in intent:
                plan.update({
                    "workflow": ["pr_bot"],
                    "next_agent": "pr_bot"
                })
            else:
                plan.update({
                    "workflow": ["retriever"],
                    "next_agent": "retriever"
                })
            
            return plan
            
        except Exception as e:
            # Don't fallback - show clear error message
            raise Exception(f"LLM planning failed: {str(e)}")
    


def dispatcher_agent(state: AgentState) -> AgentState:
    """
    Classifies user intent, creates execution plan, and dispatches to appropriate agent.
    
    Args:
        state: Current agent state containing user goal
        
    Returns:
        Updated state with user_intent, plan, and next agent routing
    """
    goal = state["goal"]
    llm_client = get_llm_client()
    
    try:
        # Step 1: Classify user intent using LLM
        user_intent = llm_client.classify_intent(goal)
        
        # Check if intent is unclassifiable
        if user_intent is None:
            # Use direct chat instead of workflow
            direct_response = llm_client.direct_chat(goal)
            return {
                **state,
                "user_intent": "direct_chat",
                "plan": {"action": "direct_chat", "goal": goal},
                "current_agent": "end",
                "response": direct_response
            }
        
        # Step 2: Create plan using LLM reasoning
        planner = LLMPlanGenerator(llm_client)
        file_paths = planner.extract_file_paths(goal)
        plan = planner.create_plan(goal, user_intent, file_paths)
        
        # Step 3: Determine next agent from plan
        next_agent = plan.get("next_agent", "retriever")
        
        return {
            **state,
            "user_intent": user_intent,
            "plan": plan,
            "current_agent": next_agent,
            "response": f"Classified as '{user_intent}' intent using {plan.get('planner', 'unknown')} planner. Planning {plan.get('workflow', [])} workflow."
        }
        
    except Exception as e:
        # Show clear error message instead of fallback
        return {
            **state,
            "user_intent": "",
            "plan": {},
            "current_agent": "end",
            "error_msg": f"Dispatcher error: {str(e)}",
            "response": f"❌ Error: {str(e)}\n\nPlease check that Ollama is running and try again."
        }