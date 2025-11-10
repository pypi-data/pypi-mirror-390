"""
Query Router for Tonina Multi-Agent System

This module handles intelligent routing of user queries to the appropriate
specialized agent based on query content, file types, and domain keywords.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from .base_agent import BaseAgent


class QueryRouter:
    """
    Routes user queries to the most appropriate specialized agent.
    
    Uses multiple strategies including file type detection, keyword matching,
    and agent confidence scoring to determine the best agent for each query.
    """
    
    def __init__(self):
        """Initialize the query router."""
        self.agents: Dict[str, BaseAgent] = {}
        self.file_type_mappings = {
            '.gff': 'gff',
            '.gff3': 'gff',
            '.gtf': 'gff',
            '.fasta': 'sequence',
            '.fa': 'sequence',
            '.fas': 'sequence',
            '.fna': 'sequence',
            '.ffn': 'sequence',
            '.faa': 'sequence',
            '.pdb': 'proteomics',
            '.pdbx': 'proteomics',
            '.cif': 'proteomics',
            '.nwk': 'phylogenetics',
            '.newick': 'phylogenetics',
            '.tree': 'phylogenetics',
            '.phy': 'phylogenetics',
            '.phylip': 'phylogenetics'
        }
        
        # Keywords that strongly suggest specific agents
        self.agent_keywords = {
            'gff': {
                'strong': ['gff', 'gtf', 'gene', 'exon', 'cds', 'chromosome', 'genomic', 'annotation',
                          'feature', 'intergenic', 'transcript', 'locus'],
                'medium': ['position', 'coordinate', 'region', 'strand', 'start', 'end', 'length']
            },
            'sequence': {
                'strong': ['fasta', 'sequence', 'nucleotide', 'protein', 'amino acid', 'dna', 'rna',
                          'orf', 'open reading frame', 'gc content', 'motif', 'alignment'],
                'medium': ['translate', 'reverse complement', 'composition', 'codon']
            },
            'proteomics': {
                'strong': ['protein', 'domain', 'structure', 'pdb', 'fold', 'active site',
                          'binding site', 'secondary structure', 'tertiary structure'],
                'medium': ['amino acid', 'residue', 'chain', 'ligand', 'enzyme']
            },
            'phylogenetics': {
                'strong': ['phylogenetic', 'tree', 'evolution', 'evolutionary', 'species',
                          'taxonomy', 'ortholog', 'paralog', 'divergence', 'ancestor'],
                'medium': ['distance', 'branch', 'clade', 'monophyletic', 'bootstrap']
            },
            'general': {
                'strong': ['convert', 'format', 'export', 'import', 'batch', 'workflow'],
                'medium': ['file', 'directory', 'list', 'summary', 'report']
            }
        }
    
    def register_agent(self, agent_name: str, agent: BaseAgent):
        """
        Register a specialized agent with the router.
        
        Args:
            agent_name (str): Name of the agent
            agent (BaseAgent): Agent instance
        """
        self.agents[agent_name] = agent
    
    def route_query(self, query: str, file_path: Optional[str] = None) -> Tuple[str, float]:
        """
        Route a query to the most appropriate agent.
        
        Args:
            query (str): User query
            file_path (str, optional): Path to file being analyzed
            
        Returns:
            Tuple[str, float]: (agent_name, confidence_score)
        """
        scores = {}
        
        # Score based on file type
        if file_path:
            file_ext = self._get_file_extension(file_path)
            if file_ext in self.file_type_mappings:
                agent_name = self.file_type_mappings[file_ext]
                scores[agent_name] = scores.get(agent_name, 0) + 0.8
        
        # Score based on keywords
        keyword_scores = self._score_by_keywords(query)
        for agent_name, score in keyword_scores.items():
            scores[agent_name] = scores.get(agent_name, 0) + score
        
        # Score based on agent confidence
        for agent_name, agent in self.agents.items():
            confidence = agent.can_handle_query(query, file_path)
            scores[agent_name] = scores.get(agent_name, 0) + confidence * 0.5
        
        # Find the best agent
        if not scores:
            return 'general', 0.1  # Default to general agent
        
        best_agent = max(scores.items(), key=lambda x: x[1])
        return best_agent
    
    def _get_file_extension(self, file_path: str) -> str:
        """
        Get the file extension from a file path.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: File extension (including the dot)
        """
        return os.path.splitext(file_path.lower())[1]
    
    def _score_by_keywords(self, query: str) -> Dict[str, float]:
        """
        Score agents based on keyword matching in the query.
        
        Args:
            query (str): User query
            
        Returns:
            Dict[str, float]: Agent scores based on keyword matching
        """
        query_lower = query.lower()
        scores = {}
        
        for agent_name, keywords in self.agent_keywords.items():
            score = 0.0
            
            # Strong keywords
            for keyword in keywords['strong']:
                if keyword in query_lower:
                    score += 0.6
            
            # Medium keywords
            for keyword in keywords['medium']:
                if keyword in query_lower:
                    score += 0.3
            
            if score > 0:
                scores[agent_name] = score
        
        return scores
    
    def get_available_agents(self) -> List[str]:
        """
        Get list of available agent names.
        
        Returns:
            List[str]: List of registered agent names
        """
        return list(self.agents.keys())
    
    def get_agent_capabilities(self) -> Dict[str, Dict]:
        """
        Get capabilities of all registered agents.
        
        Returns:
            Dict[str, Dict]: Agent capabilities by agent name
        """
        capabilities = {}
        for agent_name, agent in self.agents.items():
            capabilities[agent_name] = agent.get_capabilities()
        return capabilities
    
    def explain_routing_decision(self, query: str, file_path: Optional[str] = None) -> Dict:
        """
        Explain why a particular agent was chosen for a query.
        
        Args:
            query (str): User query
            file_path (str, optional): Path to file being analyzed
            
        Returns:
            Dict: Detailed explanation of routing decision
        """
        agent_name, confidence = self.route_query(query, file_path)
        
        explanation = {
            'selected_agent': agent_name,
            'confidence': confidence,
            'reasoning': []
        }
        
        # File type reasoning
        if file_path:
            file_ext = self._get_file_extension(file_path)
            if file_ext in self.file_type_mappings:
                mapped_agent = self.file_type_mappings[file_ext]
                explanation['reasoning'].append(
                    f"File extension '{file_ext}' suggests {mapped_agent} agent"
                )
        
        # Keyword reasoning
        keyword_scores = self._score_by_keywords(query)
        for agent, score in sorted(keyword_scores.items(), key=lambda x: x[1], reverse=True):
            if score > 0:
                explanation['reasoning'].append(
                    f"Query keywords suggest {agent} agent (score: {score:.2f})"
                )
        
        # Agent confidence reasoning
        for agent_name, agent in self.agents.items():
            confidence_score = agent.can_handle_query(query, file_path)
            if confidence_score > 0.1:
                explanation['reasoning'].append(
                    f"{agent_name} agent confidence: {confidence_score:.2f}"
                )
        
        return explanation
    
    def force_agent(self, agent_name: str) -> bool:
        """
        Check if a specific agent can be forced for routing.
        
        Args:
            agent_name (str): Name of the agent to force
            
        Returns:
            bool: True if agent exists and can be used
        """
        return agent_name in self.agents