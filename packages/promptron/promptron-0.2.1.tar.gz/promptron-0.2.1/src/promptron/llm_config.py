"""LLM Configuration class for Promptron."""


class LLMConfig:
    """
    LLM Configuration base class.
    
    Users should create a subclass with class attributes:
    - name: Model name (e.g., "llama3:latest", "gpt-4", "claude-3-opus")
    - provider: LLM provider - "ollama", "openai", or "anthropic" (optional, auto-detected)
    - api_key: API key for OpenAI/Anthropic (optional, only needed for those providers)
    - url: Base URL for Ollama (optional, only needed for Ollama, defaults to http://localhost:11434)
    
    Auto-detection rules:
    - If model name contains "llama" or "ollama" → provider = "ollama"
    - If model name starts with "gpt-" or "text-" → provider = "openai"
    - If model name starts with "claude-" → provider = "anthropic"
    - If provider is explicitly set, it takes precedence
    
    Users can read values from .env file or hardcode them.
    
    Example (Ollama - local):
        class MyLLMConfig(LLMConfig):
            name = "llama3:latest"
            provider = "ollama"  # Optional, auto-detected
            url = "http://localhost:11434"  # Optional, has default
    
    Example (OpenAI):
        class MyLLMConfig(LLMConfig):
            name = "gpt-4"
            provider = "openai"  # Optional, auto-detected from model name
            api_key = "sk-..."  # Required for OpenAI
    
    Example (Anthropic):
        class MyLLMConfig(LLMConfig):
            name = "claude-3-opus-20240229"
            provider = "anthropic"  # Optional, auto-detected from model name
            api_key = "sk-ant-..."  # Required for Anthropic
    
    Example (reading from .env):
        from promptron import LLMConfig, generate_prompts
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        class MyLLMConfig(LLMConfig):
            name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
            provider = os.getenv("PROMPTRON_PROVIDER", None)  # Auto-detect if None
            api_key = os.getenv("PROMPTRON_API_KEY", None)
            url = os.getenv("PROMPTRON_BASE_URL", None)
    """
    
    @classmethod
    def _detect_provider(cls, model_name: str) -> str:
        """Auto-detect provider from model name."""
        model_lower = model_name.lower()
        
        if "llama" in model_lower or "ollama" in model_lower:
            return "ollama"
        elif model_lower.startswith("gpt-") or model_lower.startswith("text-"):
            return "openai"
        elif model_lower.startswith("claude-"):
            return "anthropic"
        else:
            # Default to ollama for backward compatibility
            return "ollama"
    
    @classmethod
    def validate(cls):
        """Validate configuration class attributes and return config dict."""
        if not hasattr(cls, 'name') or not cls.name:
            raise ValueError("LLMConfig.name is mandatory (class attribute)")
        
        # Get provider (auto-detect if not set)
        if hasattr(cls, 'provider') and cls.provider:
            provider = cls.provider.lower()
        else:
            provider = cls._detect_provider(cls.name)
        
        # Validate provider
        if provider not in ["ollama", "openai", "anthropic"]:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: 'ollama', 'openai', 'anthropic'"
            )
        
        # Get API key (optional)
        api_key = getattr(cls, 'api_key', None)
        
        # Get URL (optional, only needed for Ollama)
        url = getattr(cls, 'url', None)
        
        # For OpenAI and Anthropic, API key should be provided (but we don't validate it)
        # For Ollama, URL is optional (defaults to http://localhost:11434)
        if provider == "ollama" and not url:
            url = "http://localhost:11434"
        
        return {
            "name": cls.name,
            "provider": provider,
            "api_key": api_key,
            "url": url
        }
