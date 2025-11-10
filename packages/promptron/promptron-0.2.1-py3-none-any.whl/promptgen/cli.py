"""Command-line interface for PromptGen."""

import argparse
import sys
import json
import yaml
from pathlib import Path
from promptgen.prompt_generator import generate_prompts
from promptgen.services.llm_service import LLMService


def check_ollama_connection() -> bool:
    """Check if Ollama is running and model is available."""
    import os
    model_name = os.getenv("PROMPTGEN_MODEL", "llama3:latest")
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model=model_name)
        # Try a simple test call
        llm.invoke("test")
        return True
    except Exception as e:
        print(f"Warning: Could not connect to Ollama or model '{model_name}' not found.")
        print(f"   Error: {e}")
        print(f"   Make sure Ollama is running: ollama serve")
        print(f"   And the model is downloaded: ollama pull {model_name}")
        print(f"   Or set PROMPTGEN_MODEL environment variable to use a different model")
        return False


def init_config(output_dir: Path = Path.cwd()):
    """Initialize example configuration files."""
    topics_file = output_dir / "topics.yml"
    templates_file = output_dir / "prompt_templates.json"
    
    if topics_file.exists() or templates_file.exists():
        response = input(f"Config files already exist in {output_dir}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    # Create example config.yml with simplified structure
    example_config = {
        "prompts": [
            {
                "category": "openshift",
                "topic": "Pod scheduling and resource management",
                "count": 6
            },
            {
                "category": "openshift",
                "topic": "Kubernetes ingress controller",
                "count": 10
            },
            {
                "category": "kubernetes",
                "topic": "Pod scheduling and resource management",
                "count": 6
            }
        ]
    }
    
    with open(topics_file, "w") as f:
        yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)
    
    # Create example prompt templates (category-based or default)
    example_templates = {
        "default": "You are an expert. Generate exactly {count} concise questions about '{topic}'. Output only numbered questions:\n1. <question>\n2. <question>",
        # Users can add category-specific templates like:
        # "openshift": "You are an OpenShift expert. Generate {count} questions about '{topic}'...",
        # "kubernetes": "You are a Kubernetes expert. Generate {count} questions about '{topic}'..."
    }
    
    with open(templates_file, "w") as f:
        json.dump(example_templates, f, indent=2)
    
    print(f"Created example configuration files:")
    print(f"   - {topics_file}")
    print(f"   - {templates_file}")
    print(f"\nEdit these files to customize your topics and templates.")


def list_categories(prompt_file: str = None):
    """List available templates (categories)."""
    try:
        if prompt_file:
            template_path = Path(prompt_file)
        else:
            template_path = Path(__file__).resolve().parent / "prompt_templates" / "prompt_template.json"
        
        if not template_path.exists():
            print(f"Error: Template file not found: {template_path}")
            return
        
        with open(template_path, "r") as f:
            templates = json.load(f)
        
        print("Available templates:")
        print("=" * 50)
        for template_name in templates.keys():
            print(f"   - {template_name}")
        if "default" in templates:
            print("\nNote: 'default' template will be used for categories not found above.")
    except Exception as e:
        print(f"Error loading templates: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PromptGen - Generate evaluation datasets using LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize config files in current directory
  promptgen init

  # Generate questions with default settings
  promptgen generate

  # Use custom configuration files
  promptgen generate --topics-file my_topics.yml --prompt-file my_templates.json

  # List available categories and question types
  promptgen list

  # Generate in JSONL format (ready for batch LLM processing)
  promptgen generate --output-format jsonl

  # Generate in OpenAI API format (ready to send to OpenAI)
  promptgen generate --output-format openai

  # Generate in simple JSON format
  promptgen generate --output-format simple
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize example configuration files")
    init_parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Directory to create config files (default: current directory)",
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available categories and question types")
    list_parser.add_argument(
        "--prompt-file",
        type=str,
        help="Path to prompt template JSON file (uses default if not provided)",
    )
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate questions")
    gen_parser.add_argument(
        "--single-file",
        action="store_true",
        help="Create one file with all categories (default: separate file per category)",
    )
    gen_parser.add_argument(
        "--topics-file",
        type=str,
        help="Path to topics YAML file (uses default if not provided)",
    )
    gen_parser.add_argument(
        "--prompt-file",
        type=str,
        help="Path to prompt template JSON file (uses default if not provided)",
    )
    gen_parser.add_argument(
        "--output-file",
        type=str,
        help="Path to output JSON file (default: ./artifacts/questions.json)",
    )
    gen_parser.add_argument(
        "--skip-check",
        action="store_true",
        help="Skip Ollama connection check (not recommended)",
    )
    gen_parser.add_argument(
        "--output-format",
        type=str,
        default="evaluation",
        choices=["evaluation", "jsonl", "simple", "openai", "anthropic", "plain"],
        help="Output format: 'evaluation' (for tracking answers), 'jsonl' (one JSON per line), 'simple' (JSON array), 'openai' (OpenAI API format), 'anthropic' (Anthropic API format), 'plain' (text file). Default: evaluation",
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "init":
        init_config(Path(args.output_dir))
    
    elif args.command == "list":
        list_categories(args.prompt_file)
    
    elif args.command == "generate":
        # Check Ollama connection unless skipped
        if not args.skip_check:
            print("Checking Ollama connection...")
            if not check_ollama_connection():
                print("\nError: Ollama connection failed. Use --skip-check to bypass (not recommended).")
                sys.exit(1)
            print("Ollama connection successful!\n")
        
        try:
            import os
            model_name = os.getenv("PROMPTGEN_MODEL", "llama3:latest")
            print(f"Starting question generation...")
            print(f"   Model: {model_name} (set PROMPTGEN_MODEL env var to change)")
            print(f"   Output Format: {args.output_format}")
            print(f"   Output Mode: {'Single file (all categories)' if args.single_file else 'Separate file per category'}")
            if args.topics_file:
                print(f"   Config File: {args.topics_file}")
            if args.prompt_file:
                print(f"   Templates File: {args.prompt_file}")
            print()
            
            generate_prompts(
                prompt_file=args.prompt_file,
                topics_file=args.topics_file,
                output_file=args.output_file,
                single_file=args.single_file,
                output_format=args.output_format,
            )
            print("\nQuestion generation completed successfully!")
        except KeyboardInterrupt:
            print("\n\nGeneration cancelled by user.")
            sys.exit(130)
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)
            import traceback
            if "--verbose" in sys.argv or "-v" in sys.argv:
                traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
