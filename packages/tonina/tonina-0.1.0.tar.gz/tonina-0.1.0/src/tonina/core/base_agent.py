"""
Base Agent Class for Tonina Multi-Agent System

This module provides the base class that all specialized agents inherit from,
ensuring consistent interface and behavior across the system.
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from strands import Agent
from strands.models.ollama import OllamaModel
from strands.models.anthropic import AnthropicModel
from strands.models.gemini import GeminiModel
from strands.models.openai import OpenAIModel


class BaseAgent(ABC):
    """
    Base class for all Tonina agents.
    
    Provides common functionality for model configuration, tool management,
    and agent initialization following the gffutilsAI patterns.
    """
    
    def __init__(self, agent_name: str, system_prompt: str):
        """
        Initialize the base agent.
        
        Args:
            agent_name (str): Name of the agent (e.g., "gff", "sequence")
            system_prompt (str): System prompt for the agent
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.agent = None
        self.tools = []
        
    @abstractmethod
    def get_tools(self, server_type: str = "local", provider: str = "ollama") -> List:
        """
        Get the list of tools available for this agent.
        
        Args:
            server_type (str): "local" or "cloud"
            provider (str): LLM provider name
            
        Returns:
            List: List of tool functions
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities description for this agent.
        
        Returns:
            Dict: Agent capabilities and supported operations
        """
        pass
    
    def configure_model(self, args) -> Any:
        """
        Configure the LLM model based on arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Configured model instance
        """
        # Ollama (local) model configuration
        if args.model and not any([args.anthropic, args.gemini, args.openai]):
            host = getattr(args, 'host', None) or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            return OllamaModel(
                model_id=args.model,
                host=host,
                max_tokens=getattr(args, 'max_tokens', 4096),
                temperature=getattr(args, 'temperature', 0.1)
            )
        
        # Anthropic model configuration
        elif args.anthropic:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic models")
            
            model_id = args.model or os.getenv('DEFAULT_ANTHROPIC_MODEL', 'claude-3-5-sonnet-latest')
            return AnthropicModel(
                model_id=model_id,
                api_key=api_key,
                max_tokens=getattr(args, 'max_tokens', 4096),
                temperature=getattr(args, 'temperature', 0.1)
            )
        
        # Gemini model configuration
        elif args.gemini:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini models")
            
            model_id = args.model or os.getenv('DEFAULT_GEMINI_MODEL', 'gemini-2.0-flash-exp')
            return GeminiModel(
                model_id=model_id,
                api_key=api_key,
                max_tokens=getattr(args, 'max_tokens', 4096),
                temperature=getattr(args, 'temperature', 0.1)
            )
        
        # OpenAI model configuration
        elif args.openai:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI models")
            
            model_id = args.model or os.getenv('DEFAULT_OPENAI_MODEL', 'gpt-4o')
            return OpenAIModel(
                model_id=model_id,
                api_key=api_key,
                max_tokens=getattr(args, 'max_tokens', 4096),
                temperature=getattr(args, 'temperature', 0.1)
            )
        
        # Default to Ollama
        else:
            host = getattr(args, 'host', None) or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            model_id = getattr(args, 'model', None) or os.getenv('DEFAULT_OLLAMA_MODEL', 'llama3.1')
            return OllamaModel(
                model_id=model_id,
                host=host,
                max_tokens=getattr(args, 'max_tokens', 4096),
                temperature=getattr(args, 'temperature', 0.1)
            )
    
    def filter_tools_for_security(self, tools: List, server_type: str, provider: str) -> List:
        """
        Filter tools based on security restrictions.
        
        Args:
            tools (List): List of tool functions
            server_type (str): "local" or "cloud"
            provider (str): LLM provider name
            
        Returns:
            List: Filtered list of tools
        """
        # For cloud providers, restrict file operations unless explicitly allowed
        if server_type == "cloud":
            allow_file_ops = os.getenv('ALLOW_FILE_OPERATIONS_CLOUD', 'false').lower() == 'true'
            
            if not allow_file_ops:
                # Filter out file operation tools for cloud providers
                file_operation_names = {'file_read', 'file_write', 'list_files'}
                filtered_tools = []
                
                for tool in tools:
                    tool_name = getattr(tool, '__name__', str(tool))
                    if tool_name not in file_operation_names:
                        filtered_tools.append(tool)
                
                return filtered_tools
        
        return tools
    
    def initialize_agent(self, args) -> Agent:
        """
        Initialize the Strands agent with model and tools.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Agent: Initialized Strands agent
        """
        # Configure model
        model = self.configure_model(args)
        
        # Get and filter tools
        server_type = getattr(args, 'server', 'local')
        provider = self._get_provider_from_args(args)
        tools = self.get_tools(server_type, provider)
        filtered_tools = self.filter_tools_for_security(tools, server_type, provider)
        
        # Create agent
        self.agent = Agent(
            system_prompt=self.system_prompt,
            model=model,
            tools=filtered_tools
        )
        
        return self.agent
    
    def _get_provider_from_args(self, args) -> str:
        """
        Determine the provider from command line arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            str: Provider name
        """
        if args.anthropic:
            return "anthropic"
        elif args.gemini:
            return "gemini"
        elif args.openai:
            return "openai"
        else:
            return "ollama"
    
    def process_query(self, query: str) -> str:
        """
        Process a query using this agent.
        
        Args:
            query (str): User query
            
        Returns:
            str: Agent response
        """
        if not self.agent:
            raise RuntimeError(f"Agent {self.agent_name} not initialized. Call initialize_agent() first.")
        
        return self.agent.run(query)
    
    def can_handle_query(self, query: str, file_path: Optional[str] = None) -> float:
        """
        Determine if this agent can handle the given query.
        
        Args:
            query (str): User query
            file_path (str, optional): Path to file being analyzed
            
        Returns:
            float: Confidence score (0.0 to 1.0) that this agent can handle the query
        """
        # Default implementation - subclasses should override
        return 0.0