"""Utility to load and manage markdown example files for the LLM context."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_markdown_examples_with_manifest(
    directory: str = "examples", max_chars: int = 100000
) -> Tuple[str, Dict[str, Any]]:
    """
    Like `load_markdown_examples`, but also returns a manifest describing which files
    were included, truncated, or skipped for the given `max_chars`.
    """
    examples_dir = Path(directory)

    manifest: Dict[str, Any] = {
        "directory": str(examples_dir),
        "max_chars": max_chars,
        "total_chars_loaded": 0,
        "files": [],  # list[dict]
        "stopped_early": False,
    }

    if not examples_dir.exists():
        return "", manifest

    markdown_files = sorted(examples_dir.glob("*.md"))
    if not markdown_files:
        return "", manifest

    combined_content: List[str] = []
    total_chars = 0

    for md_file in markdown_files:
        entry: Dict[str, Any] = {"file": md_file.name, "status": "skipped", "chars_loaded": 0}
        try:
            content = md_file.read_text(encoding="utf-8")
            content_with_header = f"\n\n## {md_file.stem}\n\n{content}\n"

            if total_chars + len(content_with_header) > max_chars:
                remaining_space = max_chars - total_chars
                if remaining_space > 1000:
                    truncated = content[: max(0, remaining_space - 100)] + "\n\n... (truncated)"
                    block = f"\n\n## {md_file.stem}\n\n{truncated}\n"
                    combined_content.append(block)
                    total_chars += len(block)
                    entry["status"] = "truncated"
                    entry["chars_loaded"] = len(block)
                else:
                    entry["status"] = "skipped"
                    entry["chars_loaded"] = 0
                manifest["files"].append(entry)
                manifest["stopped_early"] = True
                break

            combined_content.append(content_with_header)
            total_chars += len(content_with_header)
            entry["status"] = "included"
            entry["chars_loaded"] = len(content_with_header)
            manifest["files"].append(entry)

        except Exception as e:
            entry["status"] = "error"
            entry["error"] = str(e)
            manifest["files"].append(entry)
            continue

    manifest["total_chars_loaded"] = total_chars
    return "\n".join(combined_content), manifest


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

