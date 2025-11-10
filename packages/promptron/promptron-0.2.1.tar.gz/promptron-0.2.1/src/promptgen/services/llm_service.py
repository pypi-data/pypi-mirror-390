import json
import re
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml
from langchain_ollama import ChatOllama


class LLMService:
    def __init__(
        self,
        prompt_file: Optional[str] = None,
        topics_file: Optional[str] = None,
        output_file: Optional[str] = None,
        output_format: str = "evaluation",
    ):
        """
        Initialize the LLM service.
        
        Args:
            prompt_file: Path to prompt template JSON file (uses default if None)
            topics_file: Path to topics YAML file (uses default if None)
            output_file: Path to output file (uses default if None)
            output_format: Output format - 'evaluation', 'jsonl', 'simple', 'openai', 'anthropic', 'plain'
        """
        # Get model name from environment variable, default to llama3:latest
        model_name = os.getenv("PROMPTGEN_MODEL", "llama3:latest")
        self.llm = ChatOllama(model=model_name)
        self.model_name = model_name
        
        # Use default paths if not provided
        if prompt_file is None:
            prompt_file = Path(__file__).resolve().parent.parent / "prompt_templates" / "prompt_template.json"
        if topics_file is None:
            topics_file = Path(__file__).resolve().parent.parent / "config" / "topics.yml"
        if output_file is None:
            output_file = Path.cwd() / "artifacts" / "questions.json"
        
        self.prompt_file = Path(prompt_file)
        self.topics_file = Path(topics_file)
        self.output_file = Path(output_file)
        self.output_format = output_format
        
        # Adjust file extension based on format
        if output_format == "jsonl":
            if str(self.output_file).endswith(".json"):
                self.output_file = Path(str(self.output_file).replace(".json", ".jsonl"))
        elif output_format == "plain":
            if str(self.output_file).endswith(".json"):
                self.output_file = Path(str(self.output_file).replace(".json", ".txt"))
        
        self.prompt_template = self._load_prompt_template()
        # Initialize defaults before load_config
        self.global_template_config = {}
        self.config = self.load_config()

    def load_config(self) -> List[Dict[str, Any]]:
        """Load prompts configuration from YAML file."""
        if not self.topics_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.topics_file}")
        
        with open(self.topics_file, "r") as f:
            data = yaml.safe_load(f)
            prompts = data.get("prompts", [])
            
            # Store global template config if present
            self.global_template_config = data.get("template_config", {})
            
            return prompts

    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt templates from JSON file."""
        if not self.prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")

        with open(self.prompt_file, "r") as f:
            return json.load(f)

    def generate_questions(
        self,
        single_file: bool = False,
    ) -> None:
        """
        Generate questions from the loaded prompt templates.
        
        Args:
            single_file: If True, create one file with all categories. If False, separate file per category.
        """
        print("Phase-1: Generate Questions")
        
        user_data = self.config
        
        # Group prompts by category
        prompts_by_category = {}
        for prompt_config in user_data:
            category = prompt_config.get("category")
            if category not in prompts_by_category:
                prompts_by_category[category] = []
            prompts_by_category[category].append(prompt_config)
        
        # Get template - use category-specific if available, otherwise use default
        # Generate questions for each category
        for category, prompts in prompts_by_category.items():
            # Try to get category-specific template, fallback to default
            if category in self.prompt_template:
                template = self.prompt_template[category]
            elif "default" in self.prompt_template:
                template = self.prompt_template["default"]
            else:
                raise ValueError(
                    f"No template found for category '{category}' and no default template available. "
                    f"Available templates: {list(self.prompt_template.keys())}"
                )
            
            # Determine output file based on single_file flag
            if single_file:
                # Use the main output file for all categories
                output_file = self.output_file
            else:
                # Create category-specific filename
                category_safe = "".join(c for c in category if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
                ext = self.output_file.suffix
                output_file = self.output_file.parent / f"{category_safe}{ext}"
            
            # Generate questions for each topic in this category
            for prompt_config in prompts:
                topic = prompt_config.get("topic")
                count = prompt_config.get("count")
                
                print(f"\nGenerating questions")
                print(f"   Category: '{category}'")
                print(f"   Topic: '{topic}'")
                print(f"   Count: {count} questions")
                
                # Build template variables dynamically
                template_vars = {
                    "topic": topic,
                    "count": count,
                    "category": category,
                }
                
                # Add any additional variables from prompt config
                if isinstance(prompt_config, dict):
                    for key, value in prompt_config.items():
                        if key not in ["category", "topic", "count", "template", "prompt_template"]:
                            template_vars[key] = value
                
                # Add global template config variables
                if hasattr(self, 'global_template_config'):
                    template_vars.update(self.global_template_config)
                
                # Format template with all available variables (safe format)
                formatted_prompt = self._format_template(template, template_vars)
                generated_prompts = self.get_response(formatted_prompt)
                sanitized_response = self.sanitize_response(generated_prompts)
                
                # Write to file (will append if single_file, or create separate files)
                self.write_prompts_to_file(sanitized_response, topic, category=category, output_file=output_file)

    def get_response(self, prompt: str) -> str:
        """Send a prompt to the LLM and return its response."""
        response = self.llm.invoke(prompt)
        return response.content.strip()

    def _format_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Safely format template string with variables.
        Only replaces variables that exist, leaves others as-is.
        """
        try:
            # Use safe formatting - only replace variables that exist
            class SafeFormatter:
                def __init__(self, variables):
                    self.variables = variables
                
                def __getitem__(self, key):
                    return self.variables.get(key, "{" + key + "}")
            
            formatter = SafeFormatter(variables)
            return template.format_map(formatter)
        except (KeyError, ValueError) as e:
            # Fallback to standard format if safe formatting fails
            try:
                return template.format(**variables)
            except KeyError:
                # If variable is missing, leave placeholder as-is
                return template.format(**{k: v for k, v in variables.items() if "{" + k + "}" in template})

    def sanitize_response(self, questions: str) -> List[str]:
        """Sanitize the response and extract numbered questions."""
        total_questions = [q.strip() for q in re.findall(r"\d+\.\s*(.*)", questions)]
        return total_questions

    def write_prompts_to_file(self, qs: List[str], topic: str, category: Optional[str] = None, output_file: Optional[Path] = None) -> None:
        """
        Write generated questions to file in the specified format.
        
        Args:
            qs: List of questions to write
            topic: Topic name for categorization
            category: Category name (optional, for grouping)
            output_file: Optional custom output file path (uses self.output_file if None)
        """
        if output_file is None:
            output_file = self.output_file
        
        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write based on format
        if self.output_format == "evaluation":
            self._write_evaluation_format(qs, topic, category, output_file)
        elif self.output_format == "jsonl":
            self._write_jsonl_format(qs, topic, category, output_file)
        elif self.output_format == "simple":
            self._write_simple_format(qs, topic, category, output_file)
        elif self.output_format == "openai":
            self._write_openai_format(qs, topic, category, output_file)
        elif self.output_format == "anthropic":
            self._write_anthropic_format(qs, topic, category, output_file)
        elif self.output_format == "plain":
            self._write_plain_format(qs, topic, category, output_file)
        else:
            raise ValueError(f"Unknown output format: {self.output_format}")

    def _write_evaluation_format(self, qs: List[str], topic: str, category: Optional[str], output_file: Path) -> None:
        """Write in evaluation format (for tracking answers)."""
        # Read existing data if the file exists
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        # Ensure categories array exists
        if "categories" not in data:
            data["categories"] = []

        # Find category entry if present
        category_entry = next((item for item in data["categories"] if item.get("category") == category), None)
        if not category_entry:
            category_entry = {"category": category, "topics": []}
            data["categories"].append(category_entry)

        # Find topic within category
        topic_entry = next((item for item in category_entry["topics"] if item["topic"] == topic), None)
        if not topic_entry:
            topic_entry = {"topic": topic, "data": []}
            category_entry["topics"].append(topic_entry)

        # Add new user questions (only user_question field)
        for q in qs:
            topic_entry["data"].append({
                "user_question": q
            })

        # Write back to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Added {len(qs)} questions under category '{category}', topic '{topic}'")
        print(f"   Saved to: {output_file}")

    def _write_jsonl_format(self, qs: List[str], topic: str, category: Optional[str], output_file: Path) -> None:
        """Write in JSONL format (one JSON object per line)."""
        mode = "a" if os.path.exists(output_file) else "w"
        with open(output_file, mode, encoding="utf-8") as f:
            for q in qs:
                record = {
                    "prompt": q,
                    "topic": topic,
                    "category": category,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"Added {len(qs)} questions under category '{category}', topic '{topic}'")
        print(f"   Saved to: {output_file}")

    def _write_simple_format(self, qs: List[str], topic: str, category: Optional[str], output_file: Path) -> None:
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
        for q in qs:
            data.append({
                "question": q,
                "topic": topic,
                "category": category
            })

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Added {len(qs)} questions under category '{category}', topic '{topic}'")
        print(f"   Saved to: {output_file}")

    def _write_openai_format(self, qs: List[str], topic: str, category: Optional[str], output_file: Path) -> None:
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
        for q in qs:
            data.append({
                "messages": [
                    {"role": "user", "content": q}
                ],
                "metadata": {
                    "topic": topic,
                    "category": category
                }
            })

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Added {len(qs)} questions under category '{category}', topic '{topic}'")
        print(f"   Saved to: {output_file}")

    def _write_anthropic_format(self, qs: List[str], topic: str, category: Optional[str], output_file: Path) -> None:
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
        for q in qs:
            data.append({
                "messages": [
                    {"role": "user", "content": q}
                ],
                "metadata": {
                    "topic": topic,
                    "category": category
                }
            })

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Added {len(qs)} questions under category '{category}', topic '{topic}'")
        print(f"   Saved to: {output_file}")

    def _write_plain_format(self, qs: List[str], topic: str, category: Optional[str], output_file: Path) -> None:
        """Write in plain text format (one question per line)."""
        mode = "a" if os.path.exists(output_file) else "w"
        with open(output_file, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write(f"# Category: {category}\n# Topic: {topic}\n\n")
            else:
                f.write(f"\n# Category: {category}\n# Topic: {topic}\n\n")
            for q in qs:
                f.write(f"{q}\n")
        print(f"Added {len(qs)} questions under category '{category}', topic '{topic}'")
        print(f"   Saved to: {output_file}")

