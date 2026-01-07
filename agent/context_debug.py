"""Utilities to inspect what context (example files) are being injected."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .examples_loader import load_markdown_examples_with_manifest


def get_examples_manifest(examples_dir: str, max_chars: int) -> Dict[str, Any]:
    """Return the manifest for the examples that would be loaded."""
    # Resolve relative to project root
    project_root = Path(__file__).parent.parent
    examples_path = project_root / examples_dir
    _, manifest = load_markdown_examples_with_manifest(str(examples_path), max_chars=max_chars)
    return manifest


def format_examples_manifest(manifest: Dict[str, Any]) -> str:
    """Pretty-print the manifest."""
    lines = []
    lines.append(f'Examples directory: {manifest.get("directory")}')
    lines.append(f'Max chars: {manifest.get("max_chars")}')
    lines.append(f'Loaded chars: {manifest.get("total_chars_loaded")}')
    lines.append(f'Stopped early: {manifest.get("stopped_early")}')
    lines.append("")
    lines.append("Files:")
    for f in manifest.get("files", []):
        status = f.get("status")
        name = f.get("file")
        chars = f.get("chars_loaded", 0)
        if status == "error":
            lines.append(f"- {name}: ERROR ({f.get('error')})")
        else:
            lines.append(f"- {name}: {status} ({chars} chars)")
    return "\n".join(lines)


