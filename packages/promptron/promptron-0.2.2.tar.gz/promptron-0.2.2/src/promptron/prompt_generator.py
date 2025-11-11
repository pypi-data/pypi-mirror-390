"""Prompt generator module."""

from typing import Optional, List, Dict, Any, Type
from pathlib import Path
from promptron.services.llm_service import LLMService
from promptron.llm_config import LLMConfig


def _validate_config_not_dummy(config_data: List[Dict[str, Any]], config_file: Optional[str] = None) -> None:
    """
    Validate that config doesn't contain dummy/example values.
    
    Raises:
        ValueError: If dummy values are detected
    """
    dummy_values = ["your_topic_here", "example_topic", "topic_here", "your_topic"]
    
    for prompt in config_data:
        topic = prompt.get("topic", "").strip().lower()
        if topic in dummy_values or not topic:
            config_path = config_file or "config.yml"
            raise ValueError(
                f"\n❌ Config file contains dummy/example values!\n"
                f"   Found topic: '{prompt.get('topic')}'\n\n"
                f"📝 Please edit {config_path} and replace dummy values with your actual topics.\n"
                f"   Example:\n"
                f"     - category: \"default\"\n"
                f"       topic: \"your_actual_topic\"  ← Change this!\n"
                f"       count: 5\n\n"
                f"   After editing, run generate_prompts() again.\n"
            )


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
    
    You must provide either 'prompts' array or 'config_file' path.
    Config files must be created manually (see README for structure).
    
    Args:
        prompts: List of prompt configs directly (bypasses config.yml file). 
                 Each dict should have: {"category": str, "topic": str, "count": int}
                 Category must be one of: "default", "red_teaming", "out_of_scope", "edge_cases", "reasoning"
        config_file: Path to config.yml file (must exist, created manually by user).
        artifacts_location: Directory to save output files (default: "./artifacts")
        single_file: If True, create one file with all categories. If False, separate file per category.
        output_format: Output format - 'evaluation', 'jsonl', 'simple', 'openai', 'anthropic', 'plain'
        llm_config: LLMConfig class with mandatory fields (name, provider, url). 
                   If provided, overrides .env file settings.
    
    Returns:
        None (writes to file)
    
    Raises:
        ValueError: If both prompts and config_file are None, or if config contains dummy/example values
        FileNotFoundError: If config_file is provided but file doesn't exist
    
    Examples:
        # Method 1: Using prompts array directly (no config file needed)
        generate_prompts(
            prompts=[
                {"category": "default", "topic": "openshift", "count": 5}
            ]
        )
        
        # Method 2: Using config file (create config.yml manually first)
        generate_prompts(config_file="./config.yml")
        
        # Method 3: Using LLMConfig class with prompts array
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
    # Validate that either prompts or config_file is provided
    if prompts is None and config_file is None:
        raise ValueError(
            "Either 'prompts' array or 'config_file' must be provided."
        )
    
    # If config_file is provided, check it exists
    if config_file is not None:
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_file}"
            )
    
    # Determine output directory
    artifacts_dir = Path(artifacts_location)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    # Create LLMService instance (this loads the config)
    llm_service = LLMService(
        config_file=config_file,
        artifacts_location=str(artifacts_dir),
        output_format=output_format,
        llm_config=llm_config,
    )
    
    # Get the config that will be used
    config_to_validate = prompts if prompts is not None else llm_service.config
    
    # Validate that config doesn't contain dummy values (only for config_file, not prompts array)
    # User controls prompts array directly, so we trust it
    if config_file is not None and config_to_validate:
        _validate_config_not_dummy(config_to_validate, config_file)
    
    # If prompts provided directly, override the config
    if prompts is not None:
        llm_service.config = prompts
    
    # Generate questions
    llm_service.generate_questions(single_file=single_file)
    
    return None
