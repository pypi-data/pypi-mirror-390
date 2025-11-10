"""
Main CLI Interface for Tonina Multi-Agent Bioinformatics System

This module provides the command-line interface and entry point for the
Tonina multi-agent system, extending gffutilsAI patterns for multiple agents.
"""

import os
import argparse
from importlib import resources
from dotenv import load_dotenv

from .core.agent_manager import AgentManager
from .agents.gff_agent.gff_agent import GFFAgent
from .agents.general_agent.general_agent import GeneralAgent

# Global variable to store tool call information for debugging
tool_call_log = []


def load_system_prompt(agent_name: str = "main") -> str:
    """
    Load system prompt from file.
    
    Args:
        agent_name (str): Name of the agent prompt to load
        
    Returns:
        str: System prompt content
    """
    try:
        # Try to load agent-specific prompt first
        prompt_file = f"{agent_name}_prompt.txt"
        with resources.open_text("tonina.prompts", prompt_file) as f:
            return f.read()
    except (FileNotFoundError, ModuleNotFoundError):
        # Fallback to main system prompt
        try:
            with open("system_prompt.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            # Default system prompt if no file found
            return """You are Tonina, a helpful multi-agent bioinformatics assistant with comprehensive analysis capabilities.

You can analyze various types of biological data through specialized agents:
- GFF files for genomic annotations
- FASTA files for sequence analysis  
- Protein structures for proteomics
- Phylogenetic trees for evolutionary analysis
- General file operations and data integration

Use the appropriate tools for each query and provide clear, informative responses."""


def main():
    """Main entry point for Tonina CLI."""
    global tool_call_log
    
    # Check if --version is being used (don't load env vars for version check)
    import sys
    is_version_check = "--version" in sys.argv or "-v" in sys.argv
    
    # Parse command line arguments first to get env-file option
    env_file_path = None
    if "--env-file" in sys.argv:
        try:
            env_file_index = sys.argv.index("--env-file")
            if env_file_index + 1 < len(sys.argv):
                env_file_path = sys.argv[env_file_index + 1]
        except (ValueError, IndexError):
            pass
    
    # Load environment variables from .env file
    if env_file_path:
        load_dotenv(env_file_path)
        if not is_version_check:
            if os.path.exists(env_file_path):
                print(f"🔧 Loaded environment variables from: {env_file_path}")
            else:
                print(f"⚠️  Warning: .env file not found: {env_file_path}")
    else:
        # Try to load from default .env file
        if os.path.exists(".env"):
            load_dotenv()
            if not is_version_check:
                print("🔧 Loaded environment variables from: .env")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Tonina - Multi-Agent Bioinformatics Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tonina --model llama3.1 --server local
  tonina --model gpt-4o --server cloud
  tonina --query "What genes are in chromosome 1?" --model claude-3-5-sonnet-latest
  
  Multi-agent examples:
  tonina --query "Analyze this GFF file" --agent gff
  tonina --query "Find ORFs in this FASTA" --agent sequence
  
  Provider examples:
  tonina --anthropic --model claude-3-5-sonnet-latest
  tonina --gemini --model gemini-2.0-flash-exp
  tonina --openai --model gpt-4o
  
  Batch mode:
  tonina --batch queries.txt --model llama3.1
  
  Debug mode:
  tonina --debug --query "What features are in my file?"
  
  Note: To use cloud models you need to set the API key as an environment variable. 
  You can use a .env file or export the variables directly. See README.md for more information.
        """
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="tonina 0.1.0"
    )
    
    # Model selection arguments
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Model to use (e.g., llama3.1, gpt-4o, claude-3-5-sonnet-latest)"
    )
    
    # Provider selection arguments
    parser.add_argument(
        "--anthropic",
        action="store_true",
        help="Use Anthropic Claude models"
    )
    
    parser.add_argument(
        "--gemini",
        action="store_true",
        help="Use Google Gemini models"
    )
    
    parser.add_argument(
        "--openai",
        action="store_true",
        help="Use OpenAI GPT models"
    )
    
    # Server configuration
    parser.add_argument(
        "--server",
        choices=["local", "cloud"],
        default="local",
        help="Server type: local (Ollama) or cloud (API providers)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        help="Ollama server host (default: http://localhost:11434)"
    )
    
    # Agent selection
    parser.add_argument(
        "--agent",
        choices=["gff", "sequence", "proteomics", "phylogenetics", "general"],
        help="Force use of specific agent"
    )
    
    # Query modes
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Single query to process"
    )
    
    parser.add_argument(
        "--batch", "-b",
        type=str,
        help="Batch file with multiple queries"
    )
    
    # Model parameters
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.1,
        help="Model temperature (default: 0.1)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Maximum tokens (default: 4096)"
    )
    
    # System prompt
    parser.add_argument(
        "--system-prompt",
        type=str,
        help="Path to custom system prompt file"
    )
    
    # Environment file
    parser.add_argument(
        "--env-file",
        type=str,
        help="Path to environment file (default: .env)"
    )
    
    # Debug mode
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with routing information"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate provider selection
    provider_count = sum([args.anthropic, args.gemini, args.openai])
    if provider_count > 1:
        print("Error: Please specify only one provider (--anthropic, --gemini, or --openai)")
        return 1
    
    # Set server type based on provider
    if any([args.anthropic, args.gemini, args.openai]):
        args.server = "cloud"
    
    # Load system prompt
    if args.system_prompt:
        try:
            with open(args.system_prompt, 'r') as f:
                system_prompt = f.read()
        except FileNotFoundError:
            print(f"Error: System prompt file '{args.system_prompt}' not found.")
            return 1
    else:
        system_prompt = load_system_prompt()
    
    # Initialize agent manager
    manager = AgentManager()
    
    # Register available agents
    print("🚀 Initializing Tonina Multi-Agent System...")
    
    # Register GFF agent
    try:
        gff_prompt = load_system_prompt("gff")
        gff_agent = GFFAgent(gff_prompt)
        manager.register_agent("gff", gff_agent)
    except Exception as e:
        print(f"⚠️  Warning: Could not register GFF agent: {e}")
    
    # Register General agent
    try:
        general_prompt = load_system_prompt("general")
        general_agent = GeneralAgent(general_prompt)
        manager.register_agent("general", general_agent)
    except Exception as e:
        print(f"⚠️  Warning: Could not register General agent: {e}")
    
    # TODO: Register other agents as they are implemented
    # sequence_agent = SequenceAgent(load_system_prompt("sequence"))
    # manager.register_agent("sequence", sequence_agent)
    
    # Initialize all agents
    try:
        manager.initialize_agents(args)
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        return 1
    
    # Check if any agents were successfully initialized
    available_agents = manager.get_available_agents()
    if not available_agents:
        print("❌ No agents were successfully initialized. Please check your configuration.")
        return 1
    
    print(f"✅ Tonina ready with agents: {', '.join(available_agents)}")
    print()
    
    # Execute based on mode
    try:
        if args.query:
            # Single query mode
            response = manager.process_query(
                args.query, 
                force_agent=args.agent,
                debug=args.debug
            )
            print(response)
            
        elif args.batch:
            # Batch mode
            manager.batch_mode(args.batch)
            
        else:
            # Interactive mode
            manager.interactive_mode()
            
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())