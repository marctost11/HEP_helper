from __future__ import annotations

BASE_SYSTEM_PROMPT = """
You are a particle physics analysis agent.

Rules:
- Only use approved libraries and versions
- Whenever possible, use iris-hep tools
- Always generate executable Python code
- Do not answer questions that are not directly related to particle physics or data analysis. If the user asks, politely ask that the conversation remain physics-oriented
- Keep language academic and to-the-point
- Not too many comments in the generated code
"""

#REQUIREMENTS_PROMPT = """
#Ask the user to specify:
#- Which analysis step they need help with
#- Dataset format
#- Output format
#"""


def get_system_prompt(
    examples_dir: str = "examples/hep-programming-hints",
    max_chars: int = 20000,
    include_examples: bool | None = None,
) -> str:
    """
    Build the system prompt.

    Context files (markdown examples) can be toggled via:
    - include_examples arg, or
    - env var HEP_USE_EXAMPLES=0/1
    """
    from .examples_loader import load_markdown_examples, format_examples_for_prompt
    import os
    from pathlib import Path

    if include_examples is None:
        include_examples = os.getenv("HEP_USE_EXAMPLES", "1") not in {"0", "false", "False", "no", "NO"}
    
    # Resolve path relative to project root (parent of agent/ directory)
    project_root = Path(__file__).parent.parent
    examples_path = project_root / examples_dir

    if not include_examples:
        return BASE_SYSTEM_PROMPT

    examples_content = load_markdown_examples(directory=str(examples_path), max_chars=max_chars)
    examples_section = format_examples_for_prompt(examples_content)

    return BASE_SYSTEM_PROMPT + examples_section

# Default system prompt (loads examples if examples/ directory exists)
# Keep this modest to avoid rate-limit (TPM) blowups.
SYSTEM_PROMPT = get_system_prompt()
