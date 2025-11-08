"""Promptron - A Python package for generating evaluation datasets using LLMs."""

__version__ = "0.1.1"

from promptron.services.llm_service import LLMService
from promptron.prompt_generator import generate_prompts

__all__ = ["LLMService", "generate_prompts", "__version__"]

