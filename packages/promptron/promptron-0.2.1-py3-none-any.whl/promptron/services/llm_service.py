import json
import re
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Type
import yaml
from langchain_ollama import ChatOllama

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip auto-loading
    pass

# Optional imports for OpenAI and Anthropic
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


# Recommended categories for LLM evaluation
RECOMMENDED_CATEGORIES = ["default", "red_teaming", "out_of_scope", "edge_cases", "reasoning"]


class LLMService:
    def __init__(
        self,
        config_file: Optional[str] = None,
        artifacts_location: str = "./artifacts",
        output_format: str = "evaluation",
        llm_config: Optional[Type] = None,
    ):
        """
        Initialize the LLM service.
        
        Args:
            config_file: Path to config.yml file (uses default if None)
            artifacts_location: Directory to save output files (default: "./artifacts")
            output_format: Output format - 'evaluation', 'jsonl', 'simple', 'openai', 'anthropic', 'plain'
            llm_config: LLMConfig class with fields (name, provider, api_key, url).
                       If provided, overrides .env file settings.
        """
        # Get LLM configuration (priority: llm_config > .env > defaults)
        if llm_config:
            # Use provided LLMConfig class
            config_values = llm_config.validate()
            provider = config_values["provider"]
            model_name = config_values["name"]
            api_key = config_values.get("api_key")
            base_url = config_values.get("url")
        else:
            # Read from environment variables or use defaults
            model_name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
            api_key = os.getenv("PROMPTRON_API_KEY", None)
            
            # Auto-detect provider if not set
            provider_env = os.getenv("PROMPTRON_PROVIDER", None)
            if provider_env:
                provider = provider_env.lower()
            else:
                # Auto-detect from model name
                model_lower = model_name.lower()
                if "llama" in model_lower or "ollama" in model_lower:
                    provider = "ollama"
                elif model_lower.startswith("gpt-") or model_lower.startswith("text-"):
                    provider = "openai"
                elif model_lower.startswith("claude-"):
                    provider = "anthropic"
                else:
                    provider = "ollama"  # Default
            
            base_url = os.getenv("PROMPTRON_BASE_URL", None)
        
        # Initialize LLM based on provider
        if provider == "ollama":
            llm_kwargs = {"model": model_name}
            if base_url:
                llm_kwargs["base_url"] = base_url
            self.llm = ChatOllama(**llm_kwargs)
            self.provider = "ollama"
            self.model_name = model_name
            self.base_url = base_url or "http://localhost:11434"
        elif provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "OpenAI support requires 'langchain-openai' package. "
                    "Install it with: pip install promptron[openai]"
                )
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY", None)
            if not api_key:
                raise ValueError(
                    "OpenAI API key is required. "
                    "Set PROMPTRON_API_KEY or OPENAI_API_KEY environment variable, "
                    "or provide api_key in LLMConfig."
                )
            self.llm = ChatOpenAI(model=model_name, api_key=api_key)
            self.provider = "openai"
            self.model_name = model_name
            self.base_url = None
        elif provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError(
                    "Anthropic support requires 'langchain-anthropic' package. "
                    "Install it with: pip install promptron[anthropic]"
                )
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY", None)
            if not api_key:
                raise ValueError(
                    "Anthropic API key is required. "
                    "Set PROMPTRON_API_KEY or ANTHROPIC_API_KEY environment variable, "
                    "or provide api_key in LLMConfig."
                )
            self.llm = ChatAnthropic(model=model_name, api_key=api_key)
            self.provider = "anthropic"
            self.model_name = model_name
            self.base_url = None
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: 'ollama', 'openai', 'anthropic'"
            )
        
        # Use default paths if not provided
        if config_file is None:
            config_file = Path(__file__).resolve().parent.parent / "config" / "config.yml"
        else:
            config_file = Path(config_file)
        
        self.config_file = config_file
        self.artifacts_location = Path(artifacts_location)
        self.artifacts_location.mkdir(parents=True, exist_ok=True)
        self.output_format = output_format
        
        # Load templates (internal)
        prompt_template_file = Path(__file__).resolve().parent.parent / "prompt_templates" / "prompt_template.json"
        self.prompt_template = self._load_prompt_template(prompt_template_file)
        
        # Initialize config
        self.global_template_config = {}
        self.config = self.load_config() if self.config_file.exists() else []

    def load_config(self) -> List[Dict[str, Any]]:
        """Load prompts configuration from YAML file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        with open(self.config_file, "r") as f:
            data = yaml.safe_load(f)
            prompts = data.get("prompts", [])
            self.global_template_config = data.get("template_config", {})
            return prompts

    def _load_prompt_template(self, template_file: Path) -> Dict[str, Any]:
        """Load prompt templates from JSON file."""
        if not template_file.exists():
            raise FileNotFoundError(f"Template file not found: {template_file}")

        with open(template_file, "r") as f:
            return json.load(f)

    def _get_template_for_category(self, category: str) -> str:
        """Get template for category, with fallback to default and warning for non-recommended categories."""
        # Check if category is recommended
        if category not in RECOMMENDED_CATEGORIES:
            print(f"Warning: Category '{category}' is not in recommended categories: {RECOMMENDED_CATEGORIES}")
            print("   Prompt accuracy may be reduced. Falling back to 'default' template.")
            category = "default"
        
        # Get template
        if category in self.prompt_template:
            return self.prompt_template[category]
        elif "default" in self.prompt_template:
            return self.prompt_template["default"]
        else:
            raise ValueError(
                f"No template found for category '{category}' and no default template available. "
                f"Available templates: {list(self.prompt_template.keys())}"
            )

    def generate_questions(self, single_file: bool = False) -> None:
        """
        Generate questions from the loaded prompt templates.
        
        Args:
            single_file: If True, create one file with all categories. If False, separate file per category.
        """
        print("Phase-1: Generate Questions")
        
        user_data = self.config
        
        # Group prompts by category, then by topic
        # Structure: {category: {topic: [prompt_configs]}}
        prompts_by_category_topic = {}
        for prompt_config in user_data:
            category = prompt_config.get("category", "default")
            topic = prompt_config.get("topic", "unknown")
            
            if category not in prompts_by_category_topic:
                prompts_by_category_topic[category] = {}
            if topic not in prompts_by_category_topic[category]:
                prompts_by_category_topic[category][topic] = []
            
            prompts_by_category_topic[category][topic].append(prompt_config)
        
        # Generate questions for each category
        for category, topics_dict in prompts_by_category_topic.items():
            # Get template for this category
            template = self._get_template_for_category(category)
            
            # Determine output file based on single_file flag
            if single_file:
                # Use single file for all categories
                output_file = self.artifacts_location / "questions.json"
            else:
                # Create category-specific filename
                category_safe = "".join(c for c in category if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
                output_file = self.artifacts_location / f"{category_safe}.json"
            
            # Collect all questions for this category
            category_questions = []
            
            # Generate questions for each topic in this category
            for topic, prompt_configs in topics_dict.items():
                for prompt_config in prompt_configs:
                    count = prompt_config.get("count", 1)
                    
                    print(f"\nGenerating questions")
                    print(f"   Category: '{category}'")
                    print(f"   Topic: '{topic}'")
                    print(f"   Count: {count} questions")
                    
                    # Build template variables
                    template_vars = {
                        "topic": topic,
                        "count": count,
                        "category": category,
                    }
                    
                    # Add any additional variables from prompt config
                    if isinstance(prompt_config, dict):
                        for key, value in prompt_config.items():
                            if key not in ["category", "topic", "count"]:
                                template_vars[key] = value
                    
                    # Add global template config variables
                    if hasattr(self, 'global_template_config'):
                        template_vars.update(self.global_template_config)
                    
                    # Format template and generate
                    formatted_prompt = self._format_template(template, template_vars)
                    generated_prompts = self.get_response(formatted_prompt)
                    sanitized_response = self.sanitize_response(generated_prompts)
                    
                    # Store questions with topic info
                    category_questions.append({
                        "topic": topic,
                        "questions": sanitized_response
                    })
            
            # Write all questions for this category
            self.write_prompts_to_file(category_questions, category, output_file, single_file)

    def get_response(self, prompt: str) -> str:
        """Send a prompt to the LLM and return its response."""
        response = self.llm.invoke(prompt)
        return response.content.strip()

    def _format_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Safely format template string with variables."""
        try:
            class SafeFormatter:
                def __init__(self, variables):
                    self.variables = variables
                
                def __getitem__(self, key):
                    return self.variables.get(key, "{" + key + "}")
            
            formatter = SafeFormatter(variables)
            return template.format_map(formatter)
        except (KeyError, ValueError):
            try:
                return template.format(**variables)
            except KeyError:
                return template.format(**{k: v for k, v in variables.items() if "{" + k + "}" in template})

    def sanitize_response(self, questions: str) -> List[str]:
        """Sanitize the response and extract numbered questions."""
        total_questions = [q.strip() for q in re.findall(r"\d+\.\s*(.*)", questions)]
        return total_questions

    def write_prompts_to_file(
        self, 
        category_questions: List[Dict[str, List[str]]], 
        category: str, 
        output_file: Path,
        single_file: bool
    ) -> None:
        """
        Write generated questions to file in the specified format.
        
        Args:
            category_questions: List of dicts with "topic" and "questions" keys
            category: Category name
            output_file: Output file path
            single_file: Whether this is a single file or category-specific file
        """
        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write based on format
        if self.output_format == "evaluation":
            self._write_evaluation_format(category_questions, category, output_file, single_file)
        elif self.output_format == "jsonl":
            self._write_jsonl_format(category_questions, category, output_file)
        elif self.output_format == "simple":
            self._write_simple_format(category_questions, category, output_file)
        elif self.output_format == "openai":
            self._write_openai_format(category_questions, category, output_file)
        elif self.output_format == "anthropic":
            self._write_anthropic_format(category_questions, category, output_file)
        elif self.output_format == "plain":
            self._write_plain_format(category_questions, category, output_file)
        else:
            raise ValueError(f"Unknown output format: {self.output_format}")

    def _write_evaluation_format(
        self, 
        category_questions: List[Dict[str, List[str]]], 
        category: str, 
        output_file: Path,
        single_file: bool
    ) -> None:
        """Write in evaluation format: group by category, then topics with questions."""
        # Read existing data if the file exists
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {"categories": []} if single_file else {}
        else:
            data = {"categories": []} if single_file else {}
        
        if single_file:
            # Structure: {"categories": [{"category": "...", "prompts": [{"topic": "...", "questions": [...]}]}]}
            categories = data.get("categories", [])
            category_entry = next((item for item in categories if item.get("category") == category), None)
            
            if not category_entry:
                category_entry = {"category": category, "prompts": []}
                categories.append(category_entry)
            
            # Add all topics for this category
            for item in category_questions:
                topic = item["topic"]
                questions = item["questions"]
                
                # Find or create topic entry
                topic_entry = next((t for t in category_entry["prompts"] if t.get("topic") == topic), None)
                if not topic_entry:
                    topic_entry = {
                        "topic": topic, 
                        "questions": [{"user_question": q} for q in questions]
                    }
                    category_entry["prompts"].append(topic_entry)
                else:
                    topic_entry["questions"].extend([{"user_question": q} for q in questions])
            
            data["categories"] = categories
        else:
            # Structure: {"category": "...", "prompts": [{"topic": "...", "questions": [...]}]}
            data["category"] = category
            if "prompts" not in data:
                data["prompts"] = []
            
            # Add all topics
            for item in category_questions:
                topic = item["topic"]
                questions = item["questions"]
                
                topic_entry = next((t for t in data["prompts"] if t.get("topic") == topic), None)
                if not topic_entry:
                    topic_entry = {
                        "topic": topic, 
                        "questions": [{"user_question": q} for q in questions]
                    }
                    data["prompts"].append(topic_entry)
                else:
                    topic_entry["questions"].extend([{"user_question": q} for q in questions])
        
        # Write back to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        total_questions = sum(len(item["questions"]) for item in category_questions)
        print(f"Added {total_questions} questions for category '{category}'")
        print(f"   Saved to: {output_file}")

    def _write_jsonl_format(
        self, 
        category_questions: List[Dict[str, List[str]]], 
        category: str, 
        output_file: Path
    ) -> None:
        """Write in JSONL format (one JSON object per line)."""
        mode = "a" if os.path.exists(output_file) else "w"
        with open(output_file, mode, encoding="utf-8") as f:
            for item in category_questions:
                topic = item["topic"]
                for question in item["questions"]:
                    record = {
                        "prompt": question,
                        "topic": topic,
                        "category": category,
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        total_questions = sum(len(item["questions"]) for item in category_questions)
        print(f"Added {total_questions} questions for category '{category}'")
        print(f"   Saved to: {output_file}")

    def _write_simple_format(
        self, 
        category_questions: List[Dict[str, List[str]]], 
        category: str, 
        output_file: Path
    ) -> None:
        """Write in simple JSON array format."""
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        
        # Add questions with topic and category metadata
        for item in category_questions:
            topic = item["topic"]
            for question in item["questions"]:
                data.append({
                    "question": question,
                    "topic": topic,
                    "category": category
                })
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        total_questions = sum(len(item["questions"]) for item in category_questions)
        print(f"Added {total_questions} questions for category '{category}'")
        print(f"   Saved to: {output_file}")

    def _write_openai_format(
        self, 
        category_questions: List[Dict[str, List[str]]], 
        category: str, 
        output_file: Path
    ) -> None:
        """Write in OpenAI API format (messages array)."""
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        
        # Add questions in OpenAI messages format
        for item in category_questions:
            topic = item["topic"]
            for question in item["questions"]:
                data.append({
                    "messages": [
                        {"role": "user", "content": question}
                    ],
                    "metadata": {
                        "topic": topic,
                        "category": category
                    }
                })
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        total_questions = sum(len(item["questions"]) for item in category_questions)
        print(f"Added {total_questions} questions for category '{category}'")
        print(f"   Saved to: {output_file}")

    def _write_anthropic_format(
        self, 
        category_questions: List[Dict[str, List[str]]], 
        category: str, 
        output_file: Path
    ) -> None:
        """Write in Anthropic API format."""
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        
        # Add questions in Anthropic messages format
        for item in category_questions:
            topic = item["topic"]
            for question in item["questions"]:
                data.append({
                    "messages": [
                        {"role": "user", "content": question}
                    ],
                    "metadata": {
                        "topic": topic,
                        "category": category
                    }
                })
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        total_questions = sum(len(item["questions"]) for item in category_questions)
        print(f"Added {total_questions} questions for category '{category}'")
        print(f"   Saved to: {output_file}")

    def _write_plain_format(
        self, 
        category_questions: List[Dict[str, List[str]]], 
        category: str, 
        output_file: Path
    ) -> None:
        """Write in plain text format (one question per line)."""
        mode = "a" if os.path.exists(output_file) else "w"
        with open(output_file, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write(f"# Category: {category}\n\n")
            else:
                f.write(f"\n# Category: {category}\n\n")
            
            for item in category_questions:
                topic = item["topic"]
                f.write(f"## Topic: {topic}\n\n")
                for question in item["questions"]:
                    f.write(f"{question}\n")
                f.write("\n")
        
        total_questions = sum(len(item["questions"]) for item in category_questions)
        print(f"Added {total_questions} questions for category '{category}'")
        print(f"   Saved to: {output_file}")
