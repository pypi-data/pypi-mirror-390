"""
Shared File Operations Tools for Tonina Multi-Agent System

This module contains common file operation tools that can be used
across multiple agents in the system.
"""

import os
import csv
from strands import tool


@tool
def file_read(file_path: str) -> str:
    """Read a file and return its content.

    Args:
        file_path (str): Path to the file to read

    Returns:
        str: Content of the file

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    try:
        with open(file_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def file_write(file_path: str, content: str) -> str:
    """Write content to a file.

    Args:
        file_path (str): The path to the file
        content (str): The content to write to the file

    Returns:
        str: A message indicating success or failure
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        with open(file_path, "w") as file:
            file.write(content)
        return f"File '{file_path}' written successfully."
    except Exception as e:
        return f"Error writing to file: {str(e)}"


@tool
def list_files(directory_path: str = ".") -> str:
    """List files and directories in the specified path.

    Args:
        directory_path (str): Path to the directory to list

    Returns:
        str: A formatted string listing all files and directories
    """
    try:
        items = os.listdir(directory_path)
        files = []
        directories = []

        for item in items:
            full_path = os.path.join(directory_path, item)
            if os.path.isdir(full_path):
                directories.append(f"Folder: {item}/")
            else:
                files.append(f"File: {item}")

        result = f"Contents of {os.path.abspath(directory_path)}:\n"
        result += (
            "\nDirectories:\n" + "\n".join(sorted(directories))
            if directories
            else "\nNo directories found."
        )
        result += (
            "\n\nFiles:\n" + "\n".join(sorted(files))
            if files
            else "\nNo files found."
        )

        return result
    except FileNotFoundError:
        return f"Error: Directory '{directory_path}' not found."
    except PermissionError:
        return f"Error: Permission denied to access '{directory_path}'."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def get_file_info(file_path: str) -> dict:
    """Get information about a file.

    Args:
        file_path (str): Path to the file

    Returns:
        dict: File information including size, type, and modification time
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File '{file_path}' not found"}
        
        stat_info = os.stat(file_path)
        file_info = {
            "path": os.path.abspath(file_path),
            "name": os.path.basename(file_path),
            "size_bytes": stat_info.st_size,
            "size_human": _format_file_size(stat_info.st_size),
            "is_directory": os.path.isdir(file_path),
            "is_file": os.path.isfile(file_path),
            "extension": os.path.splitext(file_path)[1].lower(),
            "modified_time": stat_info.st_mtime,
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK)
        }
        
        return file_info
        
    except Exception as e:
        return {"error": f"Error getting file info: {str(e)}"}


@tool
def check_file_format(file_path: str) -> dict:
    """Check and identify the format of a biological data file.

    Args:
        file_path (str): Path to the file to check

    Returns:
        dict: Information about the file format and type
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File '{file_path}' not found"}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # File type mappings
        format_info = {
            "path": file_path,
            "extension": file_ext,
            "detected_type": "unknown",
            "description": "Unknown file format",
            "suggested_agent": "general"
        }
        
        # Check by extension first
        if file_ext in ['.gff', '.gff3', '.gtf']:
            format_info.update({
                "detected_type": "genomic_annotation",
                "description": "Genomic annotation file (GFF/GTF format)",
                "suggested_agent": "gff"
            })
        elif file_ext in ['.fasta', '.fa', '.fas', '.fna', '.ffn', '.faa']:
            format_info.update({
                "detected_type": "sequence",
                "description": "FASTA sequence file",
                "suggested_agent": "sequence"
            })
        elif file_ext in ['.pdb', '.pdbx', '.cif']:
            format_info.update({
                "detected_type": "protein_structure",
                "description": "Protein structure file",
                "suggested_agent": "proteomics"
            })
        elif file_ext in ['.nwk', '.newick', '.tree', '.phy', '.phylip']:
            format_info.update({
                "detected_type": "phylogenetic",
                "description": "Phylogenetic tree file",
                "suggested_agent": "phylogenetics"
            })
        
        # Try to validate by content for common formats
        try:
            with open(file_path, 'r') as f:
                first_lines = [f.readline().strip() for _ in range(3)]
            
            # Check FASTA format
            if any(line.startswith('>') for line in first_lines):
                format_info.update({
                    "detected_type": "sequence",
                    "description": "FASTA sequence file (detected by content)",
                    "suggested_agent": "sequence"
                })
            
            # Check GFF format
            elif any(line.startswith('##gff-version') for line in first_lines):
                format_info.update({
                    "detected_type": "genomic_annotation",
                    "description": "GFF annotation file (detected by content)",
                    "suggested_agent": "gff"
                })
            
        except Exception:
            # If we can't read the file, stick with extension-based detection
            pass
        
        return format_info
        
    except Exception as e:
        return {"error": f"Error checking file format: {str(e)}"}


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"