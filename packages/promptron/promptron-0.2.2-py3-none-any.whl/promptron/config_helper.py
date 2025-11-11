"""Configuration helper functions."""

import yaml
from pathlib import Path
from typing import Optional


def init_config(
    output_dir: Optional[str] = None, 
    force: bool = False
) -> None:
    """
    Initialize example configuration files (config.yml and .env.example).
    
    Args:
        output_dir: Directory to create config files (default: current directory)
        force: If True, overwrite existing files. If False, raise error if exists.
    
    Raises:
        FileExistsError: If config.yml or .env.example exists and force=False
    
    Example:
        from promptron import init_config
        
        # Create config files in current directory
        init_config()
        
        # Create in specific directory
        init_config(output_dir="./my_project")
        
        # Overwrite existing files
        init_config(force=True)
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
    
    config_file = output_dir / "config.yml"
    env_example_file = output_dir / ".env.example"
    
    # Check if files exist
    if config_file.exists() and not force:
        raise FileExistsError(
            f"config.yml already exists at {config_file}. "
            f"Use force=True to overwrite, or delete the file first."
        )
    
    if env_example_file.exists() and not force:
        raise FileExistsError(
            f".env.example already exists at {env_example_file}. "
            f"Use force=True to overwrite, or delete the file first."
        )
    
    # Ensure directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create example config.yml
    example_config = {
        "prompts": [
            {
                "category": "default",
                "topic": "your_topic_here",
                "count": 5
            },
            {
                "category": "red_teaming",
                "topic": "your_topic_here",
                "count": 3
            }
        ]
    }
    
    with open(config_file, "w") as f:
        yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)
    
    # Create .env.example with defaults
    env_example_content = """# Promptron LLM Configuration
# Copy this file to .env and update with your settings
# Or create an LLMConfig class and read from .env in your code

# LLM Provider (currently only 'ollama' is supported)
PROMPTRON_PROVIDER=ollama

# Model name (for Ollama: e.g., llama3:latest, llama3.2:latest)
PROMPTRON_MODEL=llama3:latest

# Ollama base URL
PROMPTRON_BASE_URL=http://localhost:11434

# Future providers will support:
# PROMPTRON_API_KEY=your_api_key_here  # For OpenAI, Anthropic, etc.
"""
    
    with open(env_example_file, "w") as f:
        f.write(env_example_content)
    
    print(f"Created config.yml at: {config_file}")
    print(f"Created .env.example at: {env_example_file}")
    print("\nNext steps:")
    print("1. Copy .env.example to .env: cp .env.example .env")
    print("2. Edit .env with your LLM model settings")
    print("3. Edit config.yml to customize your prompts")

