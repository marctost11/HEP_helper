BASE_SYSTEM_PROMPT = """
You are a particle physics analysis agent.

Rules:
- Only use approved libraries and versions
- Always generate executable Python code
- Ask clarifying questions before coding
- Do not answer questions that are not directly related to particle physics or data analysis. If the user asks, politely ask that the conversation remain physics-oriented
"""

def get_system_prompt(examples_dir: str = "examples/hep-programming-hints", max_chars: int = 100000) -> str:
    """
    Get the system prompt with examples loaded from markdown files.
    
    Args:
        examples_dir: Directory containing markdown example files (relative to project root)
        max_chars: Maximum characters for examples (default 100k = ~25k tokens)
    
    Returns:
        Complete system prompt string
    """
    from .examples_loader import load_markdown_examples, format_examples_for_prompt
    import os
    from pathlib import Path
    
    # Resolve path relative to project root (parent of agent/ directory)
    project_root = Path(__file__).parent.parent
    examples_path = project_root / examples_dir
    
    examples_content = load_markdown_examples(directory=str(examples_path), max_chars=max_chars)
    examples_section = format_examples_for_prompt(examples_content)
    
    return BASE_SYSTEM_PROMPT #+ examples_section

# Default system prompt (loads examples if examples/ directory exists)
SYSTEM_PROMPT = get_system_prompt()

REQUIREMENTS_PROMPT = """
Ask the user to specify:
- Which analysis step they need help with
- Dataset format
- Output format
"""
