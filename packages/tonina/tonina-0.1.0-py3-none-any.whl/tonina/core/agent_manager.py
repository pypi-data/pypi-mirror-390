"""
Agent Manager for Tonina Multi-Agent System

This module manages the lifecycle and coordination of multiple specialized
bioinformatics agents, providing a unified interface for query processing.
"""

import os
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent
from .router import QueryRouter


class AgentManager:
    """
    Manages multiple specialized agents and coordinates their interactions.
    
    Provides a unified interface for registering agents, routing queries,
    and managing multi-agent workflows.
    """
    
    def __init__(self):
        """Initialize the agent manager."""
        self.router = QueryRouter()
        self.agents: Dict[str, BaseAgent] = {}
        self.initialized_agents: Dict[str, bool] = {}
        self.current_args = None
        
    def register_agent(self, agent_name: str, agent: BaseAgent):
        """
        Register a specialized agent with the manager.
        
        Args:
            agent_name (str): Unique name for the agent
            agent (BaseAgent): Agent instance to register
        """
        self.agents[agent_name] = agent
        self.router.register_agent(agent_name, agent)
        self.initialized_agents[agent_name] = False
        
    def initialize_agents(self, args):
        """
        Initialize all registered agents with the given configuration.
        
        Args:
            args: Parsed command line arguments
        """
        self.current_args = args
        
        for agent_name, agent in self.agents.items():
            try:
                agent.initialize_agent(args)
                self.initialized_agents[agent_name] = True
                print(f"✅ Initialized {agent_name} agent")
            except Exception as e:
                print(f"❌ Failed to initialize {agent_name} agent: {str(e)}")
                self.initialized_agents[agent_name] = False
    
    def process_query(self, query: str, file_path: Optional[str] = None, 
                     force_agent: Optional[str] = None, debug: bool = False) -> str:
        """
        Process a user query using the appropriate agent.
        
        Args:
            query (str): User query
            file_path (str, optional): Path to file being analyzed
            force_agent (str, optional): Force use of specific agent
            debug (bool): Show routing decision details
            
        Returns:
            str: Agent response
        """
        # Determine which agent to use
        if force_agent:
            if force_agent not in self.agents:
                return f"Error: Agent '{force_agent}' not found. Available agents: {list(self.agents.keys())}"
            
            if not self.initialized_agents.get(force_agent, False):
                return f"Error: Agent '{force_agent}' not properly initialized."
            
            selected_agent = force_agent
            confidence = 1.0
        else:
            selected_agent, confidence = self.router.route_query(query, file_path)
            
            if selected_agent not in self.agents:
                selected_agent = 'general'  # Fallback to general agent
            
            if not self.initialized_agents.get(selected_agent, False):
                # Try to find an initialized agent as fallback
                for agent_name, initialized in self.initialized_agents.items():
                    if initialized:
                        selected_agent = agent_name
                        break
                else:
                    return "Error: No agents are properly initialized."
        
        # Show routing decision if debug mode
        if debug:
            explanation = self.router.explain_routing_decision(query, file_path)
            print(f"\n🔍 Routing Decision:")
            print(f"   Selected Agent: {selected_agent}")
            print(f"   Confidence: {confidence:.2f}")
            for reason in explanation['reasoning']:
                print(f"   - {reason}")
            print()
        
        # Process the query
        try:
            agent = self.agents[selected_agent]
            response = agent.process_query(query)
            
            if debug:
                print(f"✅ Query processed by {selected_agent} agent\n")
            
            return response
            
        except Exception as e:
            error_msg = f"Error processing query with {selected_agent} agent: {str(e)}"
            
            # Try fallback to general agent if available and different
            if selected_agent != 'general' and 'general' in self.agents and self.initialized_agents.get('general', False):
                try:
                    if debug:
                        print(f"⚠️  Falling back to general agent due to error: {str(e)}")
                    
                    general_agent = self.agents['general']
                    return general_agent.process_query(query)
                except Exception as fallback_error:
                    return f"{error_msg}\nFallback to general agent also failed: {str(fallback_error)}"
            
            return error_msg
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all registered agents.
        
        Returns:
            Dict: Status information for each agent
        """
        status = {}
        
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                'initialized': self.initialized_agents.get(agent_name, False),
                'capabilities': agent.get_capabilities() if self.initialized_agents.get(agent_name, False) else None,
                'class': agent.__class__.__name__
            }
        
        return status
    
    def get_available_agents(self) -> List[str]:
        """
        Get list of available and initialized agents.
        
        Returns:
            List[str]: Names of initialized agents
        """
        return [name for name, initialized in self.initialized_agents.items() if initialized]
    
    def get_all_capabilities(self) -> Dict[str, Dict]:
        """
        Get capabilities of all initialized agents.
        
        Returns:
            Dict: Capabilities by agent name
        """
        capabilities = {}
        
        for agent_name, initialized in self.initialized_agents.items():
            if initialized:
                agent = self.agents[agent_name]
                capabilities[agent_name] = agent.get_capabilities()
        
        return capabilities
    
    def reinitialize_agent(self, agent_name: str) -> bool:
        """
        Reinitialize a specific agent.
        
        Args:
            agent_name (str): Name of agent to reinitialize
            
        Returns:
            bool: True if successful
        """
        if agent_name not in self.agents:
            return False
        
        if not self.current_args:
            return False
        
        try:
            agent = self.agents[agent_name]
            agent.initialize_agent(self.current_args)
            self.initialized_agents[agent_name] = True
            return True
        except Exception:
            self.initialized_agents[agent_name] = False
            return False
    
    def interactive_mode(self):
        """
        Run interactive mode allowing continuous queries.
        """
        print("🤖 Tonina Multi-Agent Bioinformatics System")
        print("Type 'help' for commands, 'quit' to exit")
        print("Available agents:", ", ".join(self.get_available_agents()))
        print()
        
        while True:
            try:
                user_input = input("tonina> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                elif user_input.lower() == 'status':
                    self._show_status()
                    continue
                
                elif user_input.lower().startswith('agent '):
                    # Force specific agent: "agent gff what genes are there?"
                    parts = user_input.split(' ', 2)
                    if len(parts) >= 3:
                        force_agent = parts[1]
                        query = parts[2]
                        response = self.process_query(query, force_agent=force_agent, debug=True)
                    else:
                        response = "Usage: agent <agent_name> <query>"
                
                elif user_input.lower().startswith('debug '):
                    # Debug mode: "debug what genes are there?"
                    query = user_input[6:]  # Remove "debug "
                    response = self.process_query(query, debug=True)
                
                else:
                    # Normal query
                    response = self.process_query(user_input)
                
                print(response)
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except EOFError:
                print("\nGoodbye! 👋")
                break
    
    def _show_help(self):
        """Show help information."""
        print("""
Available commands:
  help                    - Show this help message
  status                  - Show agent status
  quit/exit/q            - Exit the program
  agent <name> <query>   - Force use of specific agent
  debug <query>          - Show routing decision details
  
Available agents: """ + ", ".join(self.get_available_agents()) + """

Examples:
  What genes are in chromosome 1?
  agent gff find all exons
  debug analyze this protein sequence
        """)
    
    def _show_status(self):
        """Show agent status information."""
        status = self.get_agent_status()
        
        print("\n📊 Agent Status:")
        for agent_name, info in status.items():
            status_icon = "✅" if info['initialized'] else "❌"
            print(f"  {status_icon} {agent_name}: {info['class']}")
            
            if info['capabilities']:
                caps = info['capabilities']
                if 'tool_count' in caps:
                    print(f"      Tools: {caps['tool_count']}")
                if 'description' in caps:
                    print(f"      Description: {caps['description']}")
        print()
    
    def batch_mode(self, batch_file: str):
        """
        Process queries from a batch file.
        
        Args:
            batch_file (str): Path to file containing queries
        """
        try:
            with open(batch_file, 'r') as f:
                queries = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            print(f"📁 Processing {len(queries)} queries from {batch_file}")
            print()
            
            for i, query in enumerate(queries, 1):
                print(f"Query {i}/{len(queries)}: {query}")
                response = self.process_query(query)
                print(response)
                print("-" * 80)
                
        except FileNotFoundError:
            print(f"Error: Batch file '{batch_file}' not found.")
        except Exception as e:
            print(f"Error processing batch file: {str(e)}")