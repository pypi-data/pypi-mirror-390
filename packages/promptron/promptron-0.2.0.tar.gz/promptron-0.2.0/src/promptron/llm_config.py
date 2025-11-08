"""LLM Configuration class for Promptron."""


class LLMConfig:
    """
    LLM Configuration base class.
    
    Users should create a subclass with mandatory class attributes:
    - name: Model name (e.g., "llama3:latest")
    - provider: LLM provider (currently only "ollama" supported)
    - url: Base URL for the LLM service
    
    Users can read values from .env file or hardcode them.
    
    Example (reading from .env):
        from promptron import LLMConfig, generate_prompts
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
    
    Example (hardcoded):
        class MyLLMConfig(LLMConfig):
            name = "llama3.2:latest"
            provider = "ollama"
            url = "http://localhost:11434"
    """
    
    @classmethod
    def validate(cls):
        """Validate configuration class attributes exist."""
        if not hasattr(cls, 'name') or not cls.name:
            raise ValueError("LLMConfig.name is mandatory (class attribute)")
        if not hasattr(cls, 'provider') or not cls.provider:
            raise ValueError("LLMConfig.provider is mandatory (class attribute)")
        if not hasattr(cls, 'url') or not cls.url:
            raise ValueError("LLMConfig.url is mandatory (class attribute)")
        
        # Validate provider
        if cls.provider.lower() not in ["ollama"]:
            raise ValueError(
                f"Unsupported provider: {cls.provider}. "
                f"Currently only 'ollama' is supported."
            )
        
        return {
            "name": cls.name,
            "provider": cls.provider,
            "url": cls.url
        }

