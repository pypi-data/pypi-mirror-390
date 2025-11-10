"""
General Agent for Tonina Multi-Agent System

This agent handles general file operations, format conversions,
and tasks that don't fit into specialized agent categories.
"""

from typing import List, Dict, Any, Optional
from ...core.base_agent import BaseAgent
from ...tools.file_operations import file_read, file_write, list_files, get_file_info, check_file_format
from .general_tools import (
    get_system_info, convert_file_format, batch_process_files,
    create_workflow, get_agent_recommendations
)


class GeneralAgent(BaseAgent):
    """
    General-purpose agent for file operations and cross-domain tasks.
    
    Handles file management, format conversions, system information,
    and coordination between different bioinformatics domains.
    """
    
    def __init__(self, system_prompt: str):
        """
        Initialize the General agent.
        
        Args:
            system_prompt (str): System prompt for the agent
        """
        super().__init__("general", system_prompt)
    
    def get_tools(self, server_type: str = "local", provider: str = "ollama") -> List:
        """
        Get the list of tools available for general operations.
        
        Args:
            server_type (str): "local" or "cloud"
            provider (str): LLM provider name
            
        Returns:
            List: List of tool functions
        """
        # Core file operations
        file_tools = [file_read, file_write, list_files, get_file_info, check_file_format]
        
        # General utility tools
        general_tools = [
            get_system_info, convert_file_format, batch_process_files,
            create_workflow, get_agent_recommendations
        ]
        
        return file_tools + general_tools
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities description for the General agent.
        
        Returns:
            Dict: Agent capabilities and supported operations
        """
        return {
            "agent_type": "general",
            "description": "General file operations and cross-domain bioinformatics utilities",
            "tool_count": len(self.get_tools()),
            "supported_formats": ["all common formats"],
            "capabilities": {
                "file_operations": [
                    "Read and write files",
                    "List directory contents",
                    "Get file information and metadata",
                    "Detect file formats automatically"
                ],
                "format_conversion": [
                    "Convert between common formats",
                    "Validate file formats",
                    "Extract metadata from files"
                ],
                "system_utilities": [
                    "Get system information",
                    "Batch process multiple files",
                    "Create analysis workflows"
                ],
                "agent_coordination": [
                    "Recommend appropriate agents",
                    "Route complex queries",
                    "Coordinate multi-step analyses"
                ]
            },
            "example_queries": [
                "List all files in this directory",
                "What format is this file?",
                "Convert this file to a different format",
                "Which agent should I use for this analysis?",
                "Create a workflow for analyzing multiple files"
            ]
        }
    
    def can_handle_query(self, query: str, file_path: Optional[str] = None) -> float:
        """
        Determine if this agent can handle the given query.
        
        Args:
            query (str): User query
            file_path (str, optional): Path to file being analyzed
            
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        confidence = 0.0
        query_lower = query.lower()
        
        # Strong indicators for general operations
        general_keywords = [
            'file', 'directory', 'list', 'convert', 'format', 'export',
            'import', 'batch', 'workflow', 'system', 'help'
        ]
        
        for keyword in general_keywords:
            if keyword in query_lower:
                confidence += 0.3
        
        # File operation indicators
        file_ops = [
            'read', 'write', 'create', 'delete', 'copy', 'move',
            'info', 'metadata', 'size', 'type'
        ]
        
        for op in file_ops:
            if op in query_lower:
                confidence += 0.2
        
        # Agent coordination indicators
        coordination_phrases = [
            'which agent', 'what tool', 'how to analyze', 'recommend',
            'suggest', 'best way', 'appropriate'
        ]
        
        for phrase in coordination_phrases:
            if phrase in query_lower:
                confidence += 0.4
        
        # Default fallback - general agent can handle most basic queries
        if confidence == 0.0:
            confidence = 0.1  # Low but non-zero confidence as fallback
        
        return min(confidence, 1.0)  # Cap at 1.0