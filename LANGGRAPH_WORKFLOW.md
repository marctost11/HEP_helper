# LangGraph Workflow Documentation

## Overview

The agent now uses LangGraph to implement a sophisticated 3-phase workflow:

1. **Planning Phase** - Gathers requirements from the user
2. **Code Generation Phase** - Creates executable Python code
3. **Testing Phase** - Validates code works correctly
4. **Complete** - Delivers ready-to-run code

## Installation

### Python Version Requirement

**⚠️ IMPORTANT: LangGraph requires Python 3.10 or higher!**

Check your version:
```bash
python3 --version
```

If you have Python 3.8 or 3.9, you'll need to upgrade to Python 3.10+ to use LangGraph.

### 1. Create Virtual Environment

```bash
python3 -m venv .hep_env
source .hep_env/bin/activate  # On macOS/Linux
# or
.hep_env\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install LangGraph (Python 3.10+ only)

```bash
pip install langgraph langgraph-checkpoint
```

If that fails, try:
```bash
pip install git+https://github.com/langchain-ai/langgraph.git
```

## How It Works

### Phase 1: Planning
- Agent asks clarifying questions about:
  - Dataset format and location
  - Analysis goals
  - Required libraries
  - Output format
- Continues until agent says "READY_TO_CODE"

### Phase 2: Code Generation
- Uses collected requirements to generate Python code
- Code is extracted from markdown code blocks
- Follows examples and patterns from your markdown files

### Phase 3: Testing
- Code is executed in a subprocess
- Results are validated
- If errors occur, agent fixes code and retries
- Agent says "CODE_APPROVED" when ready

### Phase 4: Complete
- Final code is delivered to user
- Ready to run immediately

## Usage

Run the agent as before:

```bash
python agent/run.py
```

The agent will guide you through the phases automatically.

## Architecture

### Files Created

- `agent/graph.py` - LangGraph workflow definition
- `agent/code_executor.py` - Code execution and testing utilities

### Files Modified

- `agent/agent.py` - Now supports both graph and simple chain modes
- `agent/run.py` - Updated to work with LangGraph
- `requirements.txt` - Added langgraph dependency

## State Management

The workflow uses a state schema (`AgentState`) that tracks:
- `messages` - Conversation history
- `phase` - Current workflow phase
- `requirements` - Collected requirements
- `generated_code` - Generated code
- `test_results` - Test execution results
- `iteration_count` - Prevents infinite loops

## Customization

You can customize the workflow by modifying:
- Prompts in `graph.py` (planning, code generation, testing prompts)
- Code execution timeout in `code_executor.py`
- Phase routing logic in the conditional edge functions

## Fallback Mode

If you want to use the simple chain-based agent instead:

```python
from agent.agent import build_agent
agent = build_agent(use_graph=False)
```

