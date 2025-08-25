"""LLM abstraction layer with extensible and interchangeable clients."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import re
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to LLM and get response."""
        pass
    
    def direct_chat(self, user_message: str) -> str:
        """Direct chat with user message for unclassifiable intents."""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful coding assistant. Answer the user's question directly and concisely."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        return self.chat(messages)
    
    def classify_intent(self, user_goal: str) -> str:
        """Classify user intent into predefined categories."""
        messages = [
            {
                "role": "system",
                "content": """You are a coding assistant that classifies user intents. 
Classify the user's request into exactly one of these categories:
- "explain" - User wants to understand the codebase structure or explain specific code files or functions  
- "feature" - User wants to add new functionality or features
- "fix" - User wants to fix bugs, failing tests, or issues
- "pr" - User wants to create a pull request
- "direct_chat" - User just want to have regular conversion

Respond with ONLY the category name, nothing else."""
            },
            {
                "role": "user", 
                "content": f"Classify this request: {user_goal}"
            }
        ]
        
        response = self.chat(messages)
        
        # Extract intent from response, return None if unclassifiable
        intent = response.strip().lower()
        valid_intents = {"explain", "feature", "fix", "pr"}
        
        return intent if intent in valid_intents else None


class OllamaClient(LLMClient):
    """Ollama local LLM client implementation."""
    
    def __init__(self, model: str = "llama3.1:8b", timeout: int = 20):
        self.model = model
        self.timeout = timeout
        
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to Ollama and get response."""
        try:
            import ollama
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Ollama request timed out after {self.timeout} seconds")
            
            # Set up timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout)
            
            try:
                response = ollama.chat(model=self.model, messages=messages)
                return response.get('message', {}).get('content', '')
            finally:
                # Cancel the timeout
                signal.alarm(0)
                
        except ImportError:
            return "Error: ollama package not installed. Run: pip install ollama"
        except TimeoutError as e:
            return f"Timeout: {str(e)}"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"


class OpenAIClient(LLMClient):
    """OpenAI API client implementation."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send messages to OpenAI and get response."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500
            )
            return response.choices[0].message.content
        except ImportError:
            return "Error: openai package not installed. Run: pip install openai"
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"


class LLMFactory:
    """Factory for creating LLM client instances."""
    
    @staticmethod
    def create_client(provider: str = "ollama", **kwargs) -> LLMClient:
        """Create LLM client instance."""
        if provider == "ollama":
            return OllamaClient(**kwargs)
        elif provider == "openai":
            return OpenAIClient(**kwargs)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")




# Global client instance
_llm_client: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    """Get singleton LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMFactory.create_client("ollama")
    return _llm_client

def set_llm_client(client: LLMClient) -> None:
    """Set the global LLM client instance."""
    global _llm_client
    _llm_client = client


class DevAgentChatModel(BaseChatModel):
    """Adapter to use DevAgent LLM clients as LangChain chat models."""
    
    llm_client: LLMClient
    
    def __init__(self, llm_client: Optional[LLMClient] = None, **kwargs):
        # Initialize with the LLM client as a model field
        super().__init__(llm_client=llm_client or get_llm_client(), **kwargs)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: List[str] = None,
        run_manager = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response using DevAgent LLM client."""
        
        # Convert LangChain messages to DevAgent format
        devagent_messages = self._convert_to_devagent_messages(messages)
        
        # Call DevAgent LLM client
        response_text = self.llm_client.chat(devagent_messages)
        
        # Convert response back to LangChain format
        ai_message = AIMessage(content=response_text)
        generation = ChatGeneration(message=ai_message)
        
        return ChatResult(generations=[generation])
    
    def _convert_to_devagent_messages(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages to DevAgent format."""
        devagent_messages = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            elif isinstance(message, SystemMessage):
                role = "system"
            else:
                role = "user"  # Fallback
            
            devagent_messages.append({
                "role": role,
                "content": message.content
            })
        
        return devagent_messages
    
    @property
    def _llm_type(self) -> str:
        """Return identifier of llm type."""
        return "devagent_chat_model"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {"llm_client": str(type(self.llm_client).__name__)}
    
    def bind_tools(self, tools, **kwargs):
        """Bind tools to the model - required for create_react_agent."""
        # For now, just return self since our tools are handled by the agent framework
        # In a full implementation, we'd need to convert tools to the format our LLM understands
        return self


def get_langchain_model() -> BaseChatModel:
    """Get a LangChain-compatible model using DevAgent's LLM client."""
    return DevAgentChatModel()