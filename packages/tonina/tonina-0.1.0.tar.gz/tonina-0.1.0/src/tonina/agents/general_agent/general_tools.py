"""
General Tools for Tonina Multi-Agent System

This module contains general-purpose tools for file operations,
system utilities, and cross-domain bioinformatics tasks.
"""

import os
import platform
import sys
from datetime import datetime
from typing import Dict, List, Any
from strands import tool


@tool
def get_system_info() -> dict:
    """Get system information including platform, Python version, and environment.

    Returns:
        dict: System information
    """
    try:
        info = {
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "current_directory": os.getcwd(),
            "user": os.getenv('USER', 'unknown'),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add environment variables related to bioinformatics
        bio_env_vars = {}
        for key in os.environ:
            if any(term in key.upper() for term in ['BLAST', 'NCBI', 'BIO', 'FASTA', 'GFF']):
                bio_env_vars[key] = os.environ[key]
        
        if bio_env_vars:
            info["bioinformatics_env"] = bio_env_vars
        
        return info
        
    except Exception as e:
        return {"error": f"Error getting system info: {str(e)}"}


@tool
def convert_file_format(input_file: str, output_file: str, target_format: str) -> str:
    """Convert a file from one format to another.

    Args:
        input_file (str): Path to input file
        output_file (str): Path to output file
        target_format (str): Target format (csv, tsv, json, etc.)

    Returns:
        str: Success message or error description
    """
    try:
        if not os.path.exists(input_file):
            return f"Error: Input file '{input_file}' not found"
        
        # Basic format conversion logic
        target_format = target_format.lower()
        
        if target_format == "csv":
            return _convert_to_csv(input_file, output_file)
        elif target_format == "tsv":
            return _convert_to_tsv(input_file, output_file)
        elif target_format == "json":
            return _convert_to_json(input_file, output_file)
        else:
            return f"Error: Unsupported target format '{target_format}'"
            
    except Exception as e:
        return f"Error converting file: {str(e)}"


@tool
def batch_process_files(directory: str, pattern: str, operation: str) -> dict:
    """Process multiple files in a directory with a specific pattern.

    Args:
        directory (str): Directory to search for files
        pattern (str): File pattern to match (e.g., "*.gff", "*.fasta")
        operation (str): Operation to perform (list, count, validate)

    Returns:
        dict: Results of batch processing
    """
    try:
        if not os.path.exists(directory):
            return {"error": f"Directory '{directory}' not found"}
        
        import glob
        
        # Find matching files
        search_pattern = os.path.join(directory, pattern)
        matching_files = glob.glob(search_pattern)
        
        results = {
            "directory": directory,
            "pattern": pattern,
            "operation": operation,
            "total_files": len(matching_files),
            "files": []
        }
        
        for file_path in matching_files:
            file_info = {
                "path": file_path,
                "name": os.path.basename(file_path),
                "size": os.path.getsize(file_path)
            }
            
            if operation == "validate":
                file_info["valid"] = _validate_file_format(file_path)
            elif operation == "info":
                stat = os.stat(file_path)
                file_info["modified"] = stat.st_mtime
                file_info["extension"] = os.path.splitext(file_path)[1]
            
            results["files"].append(file_info)
        
        return results
        
    except Exception as e:
        return {"error": f"Error in batch processing: {str(e)}"}


@tool
def create_workflow(steps: list, description: str = "") -> dict:
    """Create a multi-step analysis workflow.

    Args:
        steps (list): List of workflow steps
        description (str): Description of the workflow

    Returns:
        dict: Workflow definition
    """
    try:
        workflow = {
            "id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": description,
            "created": datetime.now().isoformat(),
            "steps": [],
            "total_steps": len(steps)
        }
        
        for i, step in enumerate(steps, 1):
            step_info = {
                "step_number": i,
                "description": step,
                "status": "pending",
                "agent_suggestion": _suggest_agent_for_step(step)
            }
            workflow["steps"].append(step_info)
        
        return workflow
        
    except Exception as e:
        return {"error": f"Error creating workflow: {str(e)}"}


@tool
def get_agent_recommendations(query: str, file_types: list = None) -> dict:
    """Get recommendations for which agent to use for a specific query.

    Args:
        query (str): User query or task description
        file_types (list, optional): List of file types involved

    Returns:
        dict: Agent recommendations with confidence scores
    """
    try:
        query_lower = query.lower()
        recommendations = []
        
        # GFF Agent scoring
        gff_score = 0
        gff_keywords = ['gff', 'gtf', 'gene', 'exon', 'cds', 'chromosome', 'genomic', 'annotation']
        for keyword in gff_keywords:
            if keyword in query_lower:
                gff_score += 0.2
        
        if file_types and any('.gff' in ft or '.gtf' in ft for ft in file_types):
            gff_score += 0.5
        
        if gff_score > 0:
            recommendations.append({
                "agent": "gff",
                "confidence": min(gff_score, 1.0),
                "reason": "Query contains GFF/genomic annotation keywords"
            })
        
        # Sequence Agent scoring
        seq_score = 0
        seq_keywords = ['fasta', 'sequence', 'dna', 'rna', 'protein', 'orf', 'nucleotide']
        for keyword in seq_keywords:
            if keyword in query_lower:
                seq_score += 0.2
        
        if file_types and any('.fasta' in ft or '.fa' in ft for ft in file_types):
            seq_score += 0.5
        
        if seq_score > 0:
            recommendations.append({
                "agent": "sequence",
                "confidence": min(seq_score, 1.0),
                "reason": "Query contains sequence analysis keywords"
            })
        
        # Proteomics Agent scoring
        prot_score = 0
        prot_keywords = ['protein', 'domain', 'structure', 'pdb', 'fold', 'binding']
        for keyword in prot_keywords:
            if keyword in query_lower:
                prot_score += 0.2
        
        if file_types and any('.pdb' in ft for ft in file_types):
            prot_score += 0.5
        
        if prot_score > 0:
            recommendations.append({
                "agent": "proteomics",
                "confidence": min(prot_score, 1.0),
                "reason": "Query contains protein/structure analysis keywords"
            })
        
        # General Agent as fallback
        if not recommendations:
            recommendations.append({
                "agent": "general",
                "confidence": 0.3,
                "reason": "General file operations or unclear domain"
            })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "query": query,
            "file_types": file_types or [],
            "recommendations": recommendations,
            "top_recommendation": recommendations[0] if recommendations else None
        }
        
    except Exception as e:
        return {"error": f"Error getting recommendations: {str(e)}"}


def _convert_to_csv(input_file: str, output_file: str) -> str:
    """Convert file to CSV format."""
    try:
        # Basic implementation - can be extended for specific formats
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                # Simple tab-to-comma conversion
                csv_line = line.replace('\t', ',')
                outfile.write(csv_line)
        
        return f"Successfully converted '{input_file}' to CSV format: '{output_file}'"
    except Exception as e:
        return f"Error converting to CSV: {str(e)}"


def _convert_to_tsv(input_file: str, output_file: str) -> str:
    """Convert file to TSV format."""
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                # Simple comma-to-tab conversion
                tsv_line = line.replace(',', '\t')
                outfile.write(tsv_line)
        
        return f"Successfully converted '{input_file}' to TSV format: '{output_file}'"
    except Exception as e:
        return f"Error converting to TSV: {str(e)}"


def _convert_to_json(input_file: str, output_file: str) -> str:
    """Convert file to JSON format."""
    try:
        import json
        
        # Basic implementation for structured data
        data = []
        with open(input_file, 'r') as infile:
            lines = infile.readlines()
            
            # Assume first line is header
            if lines:
                header = lines[0].strip().split('\t')
                for line in lines[1:]:
                    values = line.strip().split('\t')
                    if len(values) == len(header):
                        row_dict = dict(zip(header, values))
                        data.append(row_dict)
        
        with open(output_file, 'w') as outfile:
            json.dump(data, outfile, indent=2)
        
        return f"Successfully converted '{input_file}' to JSON format: '{output_file}'"
    except Exception as e:
        return f"Error converting to JSON: {str(e)}"


def _validate_file_format(file_path: str) -> bool:
    """Validate if a file matches its expected format based on extension."""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
        
        # Basic validation rules
        if ext in ['.fasta', '.fa', '.fas']:
            return first_line.startswith('>')
        elif ext in ['.gff', '.gff3']:
            return first_line.startswith('##gff-version') or not first_line.startswith('#')
        elif ext == '.gtf':
            return '\t' in first_line  # GTF should be tab-separated
        
        return True  # Default to valid for unknown formats
        
    except Exception:
        return False


def _suggest_agent_for_step(step_description: str) -> str:
    """Suggest which agent should handle a workflow step."""
    step_lower = step_description.lower()
    
    if any(keyword in step_lower for keyword in ['gff', 'gtf', 'gene', 'annotation']):
        return "gff"
    elif any(keyword in step_lower for keyword in ['fasta', 'sequence', 'dna', 'rna']):
        return "sequence"
    elif any(keyword in step_lower for keyword in ['protein', 'structure', 'pdb']):
        return "proteomics"
    elif any(keyword in step_lower for keyword in ['tree', 'phylogen', 'evolution']):
        return "phylogenetics"
    else:
        return "general"