"""Promptron - A Python package for generating evaluation datasets using LLMs."""

__version__ = "0.2.0"

from promptron.prompt_generator import generate_prompts
from promptron.config_helper import init_config
from promptron.llm_config import LLMConfig

__all__ = ["generate_prompts", "init_config", "LLMConfig", "__version__"]

