"""Prompt generator module."""

from typing import Optional, List, Dict, Any, Type
from pathlib import Path
from promptron.services.llm_service import LLMService
from promptron.llm_config import LLMConfig


class PromptGenerator:
    """Main class for Promptron functionality."""
    
    @staticmethod
    def create_sample_config(output_path: str = "config.yml", force: bool = False) -> None:
        """
        Create a sample config.yml file with example prompts configuration.
        
        Args:
            output_path: Path where to create the config.yml file (default: "config.yml")
            force: If True, overwrite existing file. If False, raise error if file exists.
        
        Raises:
            FileExistsError: If file exists and force=False
        
        Example:
            from promptron import PromptGenerator
            
            # Create sample config.yml in current directory
            PromptGenerator.create_sample_config()
            
            # Create in specific location
            PromptGenerator.create_sample_config("my_project/config.yml")
            
            # Overwrite existing file
            PromptGenerator.create_sample_config(force=True)
        """
        output_file = Path(output_path)
        
        # Check if file exists
        if output_file.exists() and not force:
            raise FileExistsError(
                f"config.yml already exists at {output_file}. "
                f"Use force=True to overwrite, or delete the file first."
            )
        
        # Ensure directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Sample config content
        sample_config = """prompts:
  - category: "default"
    topic: "your_topic_here"
    count: 5
  
  - category: "red_teaming"
    topic: "your_topic_here"
    count: 3
"""
        
        with open(output_file, "w") as f:
            f.write(sample_config)
        
        print(f"✓ Created sample config.yml at: {output_file}")
        print("\nNext steps:")
        print("1. Edit config.yml to customize your prompts (category, topic, count)")
        print("2. Configure your LLM settings (see README for LLMConfig usage)")
        print("3. Run generate_prompts(config_file='config.yml')")


def generate_prompts(
    prompts: Optional[List[Dict[str, Any]]] = None,
    config_file: Optional[str] = None,
    artifacts_location: str = "./artifacts",
    single_file: bool = False,
    output_format: str = "evaluation",
    llm_config: Optional[Type[LLMConfig]] = None,
):
    """
    Generate prompts using the LLM service.
    
    Args:
        prompts: List of prompt configs directly (bypasses config.yml file). 
                 Each dict should have: {"category": str, "topic": str, "count": int}
                 Category must be one of: "default", "red_teaming", "out_of_scope", "edge_cases", "reasoning"
        config_file: Path to config.yml file (optional, ignored if prompts provided)
        artifacts_location: Directory to save output files (default: "./artifacts")
        single_file: If True, create one file with all categories. If False, separate file per category.
        output_format: Output format - 'evaluation', 'jsonl', 'simple', 'openai', 'anthropic', 'plain'
        llm_config: LLMConfig class with mandatory fields (name, provider, url). 
                   If provided, overrides .env file settings.
    
    Returns:
        None (writes to file)
    
    Raises:
        ValueError: If both prompts and config_file are None
    
    Examples:
        # Using config.yml file with .env
        generate_prompts(config_file="./config.yml")
        
        # Using LLMConfig class (programmatic)
        from promptron import LLMConfig
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        class MyLLMConfig(LLMConfig):
            name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
            provider = os.getenv("PROMPTRON_PROVIDER", "ollama")
            url = os.getenv("PROMPTRON_BASE_URL", "http://localhost:11434")
        
        generate_prompts(
            prompts=[{"category": "default", "topic": "openshift", "count": 5}],
            llm_config=MyLLMConfig
        )
    
    Note: LLM configuration priority: llm_config parameter > .env file > defaults
    """
    # Validate inputs
    if prompts is None and config_file is None:
        raise ValueError(
            "Either 'prompts' array or 'config_file' must be provided. "
            "Use PromptGenerator.create_sample_config() to create an example config.yml file."
        )
    
    # Determine output directory
    artifacts_dir = Path(artifacts_location)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create LLMService instance
    llm_service = LLMService(
        config_file=config_file,
        artifacts_location=str(artifacts_dir),
        output_format=output_format,
        llm_config=llm_config,
    )
    
    # If prompts provided directly, override the config
    if prompts is not None:
        llm_service.config = prompts
    
    # Generate questions
    llm_service.generate_questions(single_file=single_file)
    
    return None
