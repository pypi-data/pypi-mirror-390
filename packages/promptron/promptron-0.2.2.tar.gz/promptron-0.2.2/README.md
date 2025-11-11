# Promptron

A Python package for generating evaluation datasets using Large Language Models (LLMs). Promptron helps you create structured question datasets for testing and evaluating LLM applications through code-only API.

## Features

- **Multi-Provider Support**: Works with Ollama (local), OpenAI, and Anthropic with auto-detection
- **LLM-Powered Generation**: Automatically generates questions using your chosen LLM provider
- **5 Evaluation Categories**: Pre-configured templates for comprehensive LLM evaluation
- **Code-Only API**: Simple Python functions for automation and integration
- **Flexible Configuration**: Use YAML config file or pass prompts directly
- **Structured Output**: Generates JSON datasets ready for evaluation pipelines

## Installation

### Prerequisites

- Python 3.8 or higher
- One of the following:
  - **Ollama** (local): [Install Ollama](https://ollama.ai/) and download a model (e.g., `ollama pull llama3:latest`)
  - **OpenAI**: API key from [OpenAI](https://platform.openai.com/)
  - **Anthropic**: API key from [Anthropic](https://www.anthropic.com/)

### Install from PyPI

**Base installation (Ollama only):**
```bash
pip install promptron
```

**With OpenAI support:**
```bash
pip install promptron[openai]
```

**With Anthropic support:**
```bash
pip install promptron[anthropic]
```

**With all providers:**
```bash
pip install promptron[openai,anthropic]
```


## Quick Start

### 1. Install Promptron

```bash
pip install promptron
```

### 2. Ensure Ollama is Running

```bash
ollama serve
```

### 3. Download a Model (default: llama3:latest)

```bash
ollama pull llama3:latest
```

**Optional:** Use a different model by setting environment variable:
```bash
export PROMPTRON_MODEL=llama3.2:latest
```

### 4. Choose Your Usage Method

Promptron supports two ways to provide prompts:

**Method 1: Direct Prompts Array (Simplest)**
```python
from promptron import generate_prompts

generate_prompts(
    prompts=[
        {"category": "default", "topic": "openshift", "count": 5}
    ]
)
```

**Method 2: Config File (Recommended for Projects)**

Create `config.yml` manually in your project directory:

```yaml
prompts:
  - category: "default"
    topic: "openshift"
    count: 5
  
  - category: "red_teaming"
    topic: "kubernetes"
    count: 3
```

Then use it:
```python
from promptron import generate_prompts

generate_prompts(config_file="./config.yml")
```

### 5. Generate Questions

**Option A: Using prompts array directly (no config file needed)**
```python
from promptron import generate_prompts

generate_prompts(
    prompts=[
        {"category": "default", "topic": "openshift", "count": 5}
    ],
    artifacts_location="./artifacts",
    single_file=False
)
```

**Option B: Using config file (create config.yml manually first)**
```python
from promptron import generate_prompts

# Uses config.yml you created manually
generate_prompts(
    config_file="./config.yml",
    artifacts_location="./artifacts",
    single_file=False
)
```

**Option C: Using LLMConfig class (programmatic approach)**

**Ollama (Local):**
```python
from promptron import generate_prompts, LLMConfig

class MyLLMConfig(LLMConfig):
    name = "llama3:latest"  # Provider auto-detected from "llama"
    # url defaults to http://localhost:11434

generate_prompts(
    config_file="./config.yml",
    llm_config=MyLLMConfig
)
```

**OpenAI:**
```python
from promptron import generate_prompts, LLMConfig

class MyLLMConfig(LLMConfig):
    name = "gpt-4"  # Provider auto-detected from "gpt-"
    api_key = "sk-..."  # Required for OpenAI

generate_prompts(
    config_file="./config.yml",
    llm_config=MyLLMConfig
)
```

**Anthropic:**
```python
from promptron import generate_prompts, LLMConfig

class MyLLMConfig(LLMConfig):
    name = "claude-3-opus-20240229"  # Provider auto-detected from "claude-"
    api_key = "sk-ant-..."  # Required for Anthropic

generate_prompts(
    config_file="./config.yml",
    llm_config=MyLLMConfig
)
```

## Recommended Categories

Promptron provides 5 recommended categories for comprehensive LLM evaluation:

1. **"default"** - Standard, straightforward questions for baseline evaluation
2. **"red_teaming"** - Adversarial, tricky, or misleading questions to test robustness and safety
3. **"out_of_scope"** - Questions outside the domain to test boundary handling
4. **"edge_cases"** - Unusual, extreme, or corner-case scenarios to test edge case handling
5. **"reasoning"** - Multi-step, complex, analytical questions to test reasoning depth

**Note:** Using categories outside these recommended ones may reduce prompt accuracy. The system will fallback to the "default" template with a warning.

## Usage Examples

### Method 1: Direct Prompts Array (Simplest - No Config File)

```python
from promptron import generate_prompts

# No config file needed - pass prompts directly
generate_prompts(
    prompts=[
        {"category": "default", "topic": "openshift", "count": 5},
        {"category": "red_teaming", "topic": "kubernetes", "count": 3}
    ],
    artifacts_location="./output",
    single_file=True,
    output_format="jsonl"
)
```

### Method 2: Using config.yml File with .env

**First, create `config.yml` manually:**
```yaml
prompts:
  - category: "default"
    topic: "openshift"
    count: 5
  - category: "red_teaming"
    topic: "kubernetes"
    count: 3
```

**Then use it:**
```python
from promptron import generate_prompts

# Reads LLM config from .env file
generate_prompts(
    config_file="./config.yml",
    artifacts_location="./output",
    single_file=True,
    output_format="jsonl"
)
```

### Method 3: Using config.yml File with LLMConfig

**First, create `config.yml` manually (same as Method 2).**

**Then use it with LLMConfig:**
```python
from promptron import generate_prompts, LLMConfig
from dotenv import load_dotenv
import os

load_dotenv()

class MyLLMConfig(LLMConfig):
    name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
    provider = os.getenv("PROMPTRON_PROVIDER", "ollama")
    url = os.getenv("PROMPTRON_BASE_URL", "http://localhost:11434")

generate_prompts(
    config_file="./config.yml",
    artifacts_location="./output",
    llm_config=MyLLMConfig
)
```

### Method 4: Direct Prompts with LLMConfig (No YAML File)

```python
from promptron import generate_prompts, LLMConfig
from dotenv import load_dotenv
import os

load_dotenv()

class MyLLMConfig(LLMConfig):
    name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
    provider = os.getenv("PROMPTRON_PROVIDER", "ollama")
    url = os.getenv("PROMPTRON_BASE_URL", "http://localhost:11434")

# Pass prompts directly
generate_prompts(
    prompts=[
        {"category": "default", "topic": "openshift", "count": 5},
        {"category": "red_teaming", "topic": "kubernetes", "count": 3}
    ],
    artifacts_location="./artifacts",
    llm_config=MyLLMConfig
)
```

### Complete Workflow Example

**Workflow A: Using .env file**
```python
from promptron import generate_prompts

# 1. Create config.yml manually (see structure in README)

# 2. Create .env file with your LLM settings (optional, can use LLMConfig instead)

# 3. Generate questions (reads from .env automatically if not using LLMConfig)
generate_prompts(
    config_file="./config.yml",
    artifacts_location="./evaluation_data",
    single_file=True
)
```

**Workflow B: Using LLMConfig class**
```python
from promptron import generate_prompts, LLMConfig
from dotenv import load_dotenv
import os

# 1. Create config.yml manually (see structure in README)

# 2. Load .env (user creates this)
load_dotenv()

# 3. Create LLMConfig class (user writes this)
class MyLLMConfig(LLMConfig):
    name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
    provider = os.getenv("PROMPTRON_PROVIDER", "ollama")
    url = os.getenv("PROMPTRON_BASE_URL", "http://localhost:11434")

# 4. Edit config.yml with your prompts

# 5. Generate questions with LLMConfig
generate_prompts(
    config_file="./config.yml",
    artifacts_location="./evaluation_data",
    llm_config=MyLLMConfig,
    single_file=True
)
```

## API Reference

### `LLMConfig`

Base class for LLM configuration. Supports **Ollama**, **OpenAI**, and **Anthropic** with auto-detection.

**Attributes:**
- `name` (str, required): Model name (e.g., "llama3:latest", "gpt-4", "claude-3-opus-20240229")
- `provider` (str, optional): LLM provider - "ollama", "openai", or "anthropic" (auto-detected if not set)
- `api_key` (str, optional): API key for OpenAI/Anthropic (required for those providers)
- `url` (str, optional): Base URL for Ollama (defaults to http://localhost:11434)

**Auto-detection rules:**
- Model name contains "llama" or "ollama" → provider = "ollama"
- Model name starts with "gpt-" or "text-" → provider = "openai"
- Model name starts with "claude-" → provider = "anthropic"

**Example (Ollama - auto-detected):**
```python
from promptron import LLMConfig

class MyLLMConfig(LLMConfig):
    name = "llama3:latest"  # Provider auto-detected
    # url defaults to http://localhost:11434
```

**Example (OpenAI - auto-detected):**
```python
from promptron import LLMConfig

class MyLLMConfig(LLMConfig):
    name = "gpt-4"  # Provider auto-detected
    api_key = "sk-..."  # Required
```

**Example (Anthropic - auto-detected):**
```python
from promptron import LLMConfig

class MyLLMConfig(LLMConfig):
    name = "claude-3-opus-20240229"  # Provider auto-detected
    api_key = "sk-ant-..."  # Required
```

**Example (reading from .env):**
```python
from promptron import LLMConfig
from dotenv import load_dotenv
import os

load_dotenv()

class MyLLMConfig(LLMConfig):
    name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
    provider = os.getenv("PROMPTRON_PROVIDER", None)  # Auto-detect if None
    api_key = os.getenv("PROMPTRON_API_KEY", None)
    url = os.getenv("PROMPTRON_BASE_URL", None)  # Optional for Ollama
```

### `generate_prompts(prompts=None, config_file=None, artifacts_location="./artifacts", single_file=False, output_format="evaluation", llm_config=None)`

Generate questions using the LLM service.

**Parameters:**
- `prompts` (list, optional): List of prompt configs. Each dict: `{"category": str, "topic": str, "count": int}`. 
  Either `prompts` or `config_file` must be provided.
- `config_file` (str, optional): Path to config.yml file (must exist, created manually by user).
  Either `prompts` or `config_file` must be provided.
- `artifacts_location` (str): Directory to save output files (default: "./artifacts")
- `single_file` (bool): If True, create one file with all categories. If False, separate file per category.
- `output_format` (str): Output format - 'evaluation', 'jsonl', 'simple', 'openai', 'anthropic', 'plain'
- `llm_config` (LLMConfig class, optional): LLM configuration class. If provided, overrides .env file settings.

**Raises:**
- `ValueError`: If both prompts and config_file are None, or if config contains dummy/example values
- `FileNotFoundError`: If config_file is provided but file doesn't exist

**LLM Configuration Priority:**
1. `llm_config` parameter (if provided)
2. `.env` file (if exists)
3. Defaults (ollama, llama3:latest, http://localhost:11434)

**Supported Providers:**
- **Ollama** (local, no API key needed) - Install: `pip install promptron`
- **OpenAI** (requires API key) - Install: `pip install promptron[openai]`
- **Anthropic** (requires API key) - Install: `pip install promptron[anthropic]`

**Example:**
```python
from promptron import generate_prompts, LLMConfig
from dotenv import load_dotenv
import os

load_dotenv()

class MyLLMConfig(LLMConfig):
    name = os.getenv("PROMPTRON_MODEL", "llama3:latest")
    provider = os.getenv("PROMPTRON_PROVIDER", "ollama")
    url = os.getenv("PROMPTRON_BASE_URL", "http://localhost:11434")

# Using LLMConfig
generate_prompts(
    config_file="./config.yml",
    artifacts_location="./output",
    llm_config=MyLLMConfig
)

# Or using .env file (no LLMConfig needed)
generate_prompts(
    config_file="./config.yml",
    artifacts_location="./output"
)
```

## Output Formats

### 1. Evaluation Format (default)

Best for tracking answers from multiple LLMs:

```json
{
  "categories": [
    {
      "category": "default",
      "prompts": [
        {
          "topic": "openshift",
          "questions": [
            {"user_question": "How do I configure pod resource limits?"},
            {"user_question": "What is the difference between requests and limits?"}
          ]
        }
      ]
    }
  ]
}
```

When `single_file=False`, each category gets its own file: `artifacts/default.json`, `artifacts/red_teaming.json`, etc.

### 2. JSONL Format

Perfect for batch processing:

```jsonl
{"prompt": "How do I configure pod resource limits?", "topic": "openshift", "category": "default"}
{"prompt": "What is the difference between requests and limits?", "topic": "openshift", "category": "default"}
```

### 3. Simple JSON Format

Clean array format:

```json
[
  {"question": "How do I configure pod resource limits?", "topic": "openshift", "category": "default"},
  {"question": "What is the difference between requests and limits?", "topic": "openshift", "category": "default"}
]
```

### 4. OpenAI API Format

Ready to send to OpenAI:

```json
[
  {
    "messages": [{"role": "user", "content": "How do I configure pod resource limits?"}],
    "metadata": {"topic": "openshift", "category": "default"}
  }
]
```

### 5. Anthropic API Format

Ready to send to Anthropic:

```json
[
  {
    "messages": [{"role": "user", "content": "How do I configure pod resource limits?"}],
    "metadata": {"topic": "openshift", "category": "default"}
  }
]
```

### 6. Plain Text Format

Simple text file:

```
# Category: default

## Topic: openshift

How do I configure pod resource limits?
What is the difference between requests and limits?
```

## Output Structure

### When `single_file=True`:

One file (`artifacts/questions.json`) with all categories:

```json
{
  "categories": [
    {
      "category": "default",
      "prompts": [
        {
          "topic": "openshift",
          "questions": [{"user_question": "..."}, ...]
        },
        {
          "topic": "kubernetes",
          "questions": [{"user_question": "..."}, ...]
        }
      ]
    },
    {
      "category": "red_teaming",
      "prompts": [...]
    }
  ]
}
```

### When `single_file=False`:

Separate file per category (`artifacts/default.json`, `artifacts/red_teaming.json`, etc.):

**File: `artifacts/default.json`**
```json
{
  "category": "default",
  "prompts": [
    {
      "topic": "openshift",
      "questions": [{"user_question": "..."}, ...]
    }
  ]
}
```

## Configuration

### config.yml Structure

```yaml
prompts:
  - category: "default"        # One of 5 recommended categories
    topic: "openshift"         # User-defined topic (anything)
    count: 5                   # Number of questions to generate
  
  - category: "red_teaming"
    topic: "kubernetes"
    count: 3
```

### LLM Configuration (.env file)

Create a `.env` file in your project directory (or copy from `.env.example`):

```bash
# LLM Provider (currently only 'ollama' is supported)
PROMPTRON_PROVIDER=ollama

# Model name (for Ollama: e.g., llama3:latest, llama3.2:latest)
PROMPTRON_MODEL=llama3:latest

# Ollama base URL (optional, defaults to http://localhost:11434)
PROMPTRON_BASE_URL=http://localhost:11434
```

**Note:** Currently only Ollama (local) is supported. Support for OpenAI, Anthropic, and other providers will be added in future versions.

**Using environment variables directly:**
```bash
export PROMPTRON_PROVIDER=ollama
export PROMPTRON_MODEL=llama3.2:latest
export PROMPTRON_BASE_URL=http://localhost:11434
```

## Requirements

- `langchain-ollama>=0.1.0`
- `pyyaml>=6.0`
- `python-dotenv>=1.0.0` (for automatic .env file loading)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

**Hit Shiroya**

- Email: 24.hiit@gmail.com

## License

MIT License

## Support

For issues and questions, please open an issue on the GitHub repository.
