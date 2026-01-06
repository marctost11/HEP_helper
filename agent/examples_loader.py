"""Utility to load and manage markdown example files for the LLM context."""
import os
from pathlib import Path
from typing import List, Optional


def load_markdown_examples(directory: str = "examples", max_chars: int = 100000) -> str:
    """
    Load markdown files from a directory and combine them into a single string.
    
    Args:
        directory: Path to directory containing markdown example files
        max_chars: Maximum characters to include (default ~100k chars = ~25k tokens)
    
    Returns:
        Combined markdown content as a string
    """
    examples_dir = Path(directory)
    
    if not examples_dir.exists():
        return ""
    
    # Find all markdown files
    markdown_files = sorted(examples_dir.glob("*.md"))
    
    if not markdown_files:
        return ""
    
    combined_content = []
    total_chars = 0
    
    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            content_with_header = f"\n\n## {md_file.stem}\n\n{content}\n"
            
            # Check if adding this file would exceed the limit
            if total_chars + len(content_with_header) > max_chars:
                # Try to include a truncated version if we have space
                remaining_space = max_chars - total_chars
                if remaining_space > 1000:  # Only if meaningful space remains
                    truncated = content[:remaining_space - 100] + "\n\n... (truncated)"
                    combined_content.append(f"\n\n## {md_file.stem}\n\n{truncated}\n")
                break
            
            combined_content.append(content_with_header)
            total_chars += len(content_with_header)
            
        except Exception as e:
            print(f"Warning: Could not load {md_file}: {e}")
            continue
    
    return "\n".join(combined_content)


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count (1 token ≈ 4 characters for English).
    More accurate: use tiktoken library for exact counts.
    """
    return len(text) // 4


def escape_curly_braces(text: str) -> str:
    """
    Escape curly braces in text so LangChain's ChatPromptTemplate treats them as literal.
    LangChain uses {variable} syntax, so we need {{ and }} for literal braces.
    
    This function doubles all curly braces. The order matters: we replace } first,
    then {, to avoid interfering with the replacements.
    """
    # Replace } first, then {, to avoid issues with replacement order
    # This doubles all braces: { becomes {{ and } becomes }}
    text = text.replace('}', '}}').replace('{', '{{')
    return text


def format_examples_for_prompt(examples_content: str) -> str:
    """
    Format examples content for inclusion in system prompt.
    Escapes curly braces so LangChain doesn't interpret them as template variables.
    """
    if not examples_content.strip():
        return ""
    
    # Escape curly braces in examples to prevent LangChain from treating them as variables
    escaped_content = escape_curly_braces(examples_content)
    
    return f"""
## Code Examples and Patterns

The following examples demonstrate preferred code structure and patterns:

{escaped_content}

Use these examples as reference when providing coding advice. Follow similar patterns, structure, and best practices shown in the examples.
"""

