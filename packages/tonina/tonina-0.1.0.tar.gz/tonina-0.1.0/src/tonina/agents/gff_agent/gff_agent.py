"""
GFF Agent for Tonina Multi-Agent System

This agent specializes in GFF (General Feature Format) file analysis,
providing all the capabilities from the original gffutilsAI system.
"""

import re
from typing import List, Dict, Any, Optional
from ...core.base_agent import BaseAgent
from ...tools.file_operations import file_read, file_write, list_files, get_file_info, check_file_format

# Import all GFF-specific tools
from .gff_tools import (
    get_organism_info, get_gff_feature_types, get_gene_lenght, get_gene_attributes,
    get_multiple_gene_lenght, get_all_attributes, get_genes_and_features_from_attribute,
    get_protein_product_from_gene, get_features_in_region, get_features_at_position,
    get_gene_structure, get_feature_parents, get_features_by_type, get_feature_statistics,
    get_chromosomes_info, get_chromosome_summary, get_length_distribution,
    search_features_by_attribute, search_genes_by_go_function_attribute,
    get_features_with_attribute, get_country_or_region, get_intergenic_regions,
    get_feature_density, get_strand_distribution, export_features_to_csv,
    get_feature_summary_report, get_tools_list
)


class GFFAgent(BaseAgent):
    """
    Specialized agent for GFF file analysis.
    
    Provides comprehensive genomic annotation analysis capabilities including
    coordinate-based queries, statistical analysis, attribute searches,
    and export functionality.
    """
    
    def __init__(self, system_prompt: str):
        """
        Initialize the GFF agent.
        
        Args:
            system_prompt (str): System prompt for the agent
        """
        super().__init__("gff", system_prompt)
    
    def get_tools(self, server_type: str = "local", provider: str = "ollama") -> List:
        """
        Get the list of tools available for GFF analysis.
        
        Args:
            server_type (str): "local" or "cloud"
            provider (str): LLM provider name
            
        Returns:
            List: List of tool functions
        """
        # Core file operations (may be filtered for cloud providers)
        file_tools = [file_read, file_write, list_files, get_file_info, check_file_format]
        
        # GFF-specific analysis tools
        gff_tools = [
            get_organism_info, get_gff_feature_types, get_gene_lenght, get_gene_attributes,
            get_multiple_gene_lenght, get_all_attributes, get_genes_and_features_from_attribute,
            get_protein_product_from_gene, get_features_in_region, get_features_at_position,
            get_gene_structure, get_feature_parents, get_features_by_type, get_feature_statistics,
            get_chromosomes_info, get_chromosome_summary, get_length_distribution,
            search_features_by_attribute, search_genes_by_go_function_attribute,
            get_features_with_attribute, get_country_or_region, get_intergenic_regions,
            get_feature_density, get_strand_distribution, export_features_to_csv,
            get_feature_summary_report, get_tools_list
        ]
        
        return file_tools + gff_tools
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities description for the GFF agent.
        
        Returns:
            Dict: Agent capabilities and supported operations
        """
        return {
            "agent_type": "gff",
            "description": "Comprehensive GFF/GTF genomic annotation analysis",
            "tool_count": len(self.get_tools()),
            "supported_formats": [".gff", ".gff3", ".gtf"],
            "capabilities": {
                "coordinate_queries": [
                    "Find features by genomic coordinates",
                    "Query features in specific regions",
                    "Identify features at specific positions"
                ],
                "statistical_analysis": [
                    "Calculate feature statistics and counts",
                    "Generate length distributions",
                    "Analyze per-chromosome summaries",
                    "Feature density calculations"
                ],
                "attribute_searches": [
                    "Search by attribute key-value pairs",
                    "GO function-based gene searches",
                    "Pattern matching in attributes"
                ],
                "structural_analysis": [
                    "Gene structure exploration",
                    "Parent-child feature relationships",
                    "Intergenic region identification",
                    "Strand distribution analysis"
                ],
                "export_capabilities": [
                    "CSV export with filtering",
                    "Summary report generation",
                    "Feature data extraction"
                ]
            },
            "example_queries": [
                "What feature types are in my GFF file?",
                "Find all genes on chromosome 1 between positions 1000-5000",
                "Calculate feature statistics for this annotation",
                "Get the structure of gene AT1G01010",
                "Export all membrane proteins to CSV"
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
        
        # Strong indicators for GFF analysis
        gff_keywords = [
            'gff', 'gtf', 'gene', 'exon', 'cds', 'chromosome', 'genomic',
            'annotation', 'feature', 'intergenic', 'transcript', 'locus'
        ]
        
        for keyword in gff_keywords:
            if keyword in query_lower:
                confidence += 0.3
        
        # Medium indicators
        genomic_keywords = [
            'position', 'coordinate', 'region', 'strand', 'start', 'end',
            'length', 'statistics', 'export', 'attribute'
        ]
        
        for keyword in genomic_keywords:
            if keyword in query_lower:
                confidence += 0.1
        
        # File extension check
        if file_path:
            file_ext = file_path.lower()
            if any(ext in file_ext for ext in ['.gff', '.gff3', '.gtf']):
                confidence += 0.5
        
        # Specific GFF operations
        if any(phrase in query_lower for phrase in [
            'feature type', 'gene structure', 'genomic region',
            'chromosome summary', 'go function', 'membrane protein'
        ]):
            confidence += 0.4
        
        return min(confidence, 1.0)  # Cap at 1.0