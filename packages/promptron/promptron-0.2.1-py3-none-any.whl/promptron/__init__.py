"""Promptron - A Python package for generating evaluation datasets using LLMs."""

__version__ = "0.2.1"

from promptron.prompt_generator import generate_prompts, PromptGenerator
from promptron.llm_config import LLMConfig

__all__ = ["generate_prompts", "PromptGenerator", "LLMConfig", "__version__"]

