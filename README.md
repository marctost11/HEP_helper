# HEP_helper
Building an AI agent to help grad students do physics faster

## Setup

### Python Version Requirement

**Important:** LangGraph requires **Python 3.10 or higher**. 

Check your Python version:
```bash
python3 --version
```

If you have Python 3.8 or 3.9, you have two options:
1. **Upgrade to Python 3.10+** (recommended for LangGraph workflow)
2. **Use the simple chain mode** (works with Python 3.8+, but without advanced workflow)

### Virtual Environment

Create and activate a virtual environment:

```bash
python3 -m venv .hep_env
source .hep_env/bin/activate  # On macOS/Linux
# or
.hep_env\Scripts\activate  # On Windows
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**LangGraph Installation (for advanced workflow):**

**Requires Python 3.10+**

If you have Python 3.10+ and want to use the LangGraph workflow, install langgraph separately:

```bash
# Try standard installation first
pip install langgraph langgraph-checkpoint

# If that fails, try installing from GitHub
pip install git+https://github.com/langchain-ai/langgraph.git
```

**Note:** 
- The agent will automatically fall back to simple chain mode if LangGraph is not available
- If you're using Python 3.8 or 3.9, the simple chain mode will work fine (just without the advanced 3-phase workflow)

### Run the Agent

```bash
python agent/run.py
```

## Features

- **LangGraph Workflow**: Sophisticated 3-phase workflow (Planning → Code Generation → Testing)
- **Code Examples**: Automatically loads markdown examples for better code generation
- **Code Validation**: Executes and tests generated code before delivery
- **Particle Physics Focus**: Specialized for HEP analysis tasks
