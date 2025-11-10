"""Prompt generator module."""

from typing import Optional, List, Dict, Any
from promptgen.services.llm_service import LLMService


def generate_prompts(
    prompts: Optional[List[Dict[str, Any]]] = None,
    prompt_file: Optional[str] = None,
    topics_file: Optional[str] = None,
    output_file: Optional[str] = None,
    single_file: bool = False,
    output_format: str = "evaluation",
):
    """
    Generate prompts using the LLM service.
    
    Args:
        prompts: List of prompt configs directly (bypasses YAML file). 
                 Each dict should have: {"category": str, "topic": str, "count": int}
        prompt_file: Path to prompt template JSON file (uses default if None)
        topics_file: Path to config YAML file (uses default if None, ignored if prompts provided)
        output_file: Path to output file (default: ./artifacts/questions.json)
        single_file: If True, create one file with all categories. If False, separate file per category.
        output_format: Output format - 'evaluation', 'jsonl', 'simple', 'openai', 'anthropic', 'plain'
    
    Returns:
        None (writes to file)
    
    Examples:
        # Using YAML file
        generate_prompts(topics_file="./my_config.yml")
        
        # Using direct prompts (programmatic)
        generate_prompts(
            prompts=[
                {"category": "openshift", "topic": "Pod scheduling", "count": 5},
                {"category": "kubernetes", "topic": "Ingress", "count": 10}
            ],
            output_format="jsonl"
        )
    
    Note: Model is configured via PROMPTGEN_MODEL environment variable (default: llama3:latest)
    """
    llm_service = LLMService(
        prompt_file=prompt_file,
        topics_file=topics_file,
        output_file=output_file,
        output_format=output_format,
    )
    
    # If prompts provided directly, override the config
    if prompts is not None:
        llm_service.config = prompts
    
    results = llm_service.generate_questions(
        single_file=single_file,
    )
    return results

