"""Code execution and testing utilities for the agent."""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from typing import List, Dict, Any, Set
from pathlib import Path
import tempfile


def extract_code_blocks(text: str) -> List[str]:
    """
    Extract Python code blocks from markdown-formatted text.
    
    Args:
        text: Text that may contain ```python code blocks
        
    Returns:
        List of code strings extracted from code blocks
    """
    # Pattern to match ```python ... ``` blocks
    pattern = r'```python\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Also try without language specification
    pattern2 = r'```\s*\n(.*?)```'
    matches2 = re.findall(pattern2, text, re.DOTALL)
    
    # Combine and deduplicate
    all_matches = matches + matches2
    # Clean up whitespace
    cleaned = [match.strip() for match in all_matches if match.strip()]
    
    return cleaned


def execute_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute Python code in a subprocess and return results.
    
    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds
        
    Returns:
        Dictionary with 'success', 'output', 'error' keys
    """
    if not code.strip():
        return {
            "success": False,
            "error": "No code provided",
            "output": ""
        }
    
    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Execute the code
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd()
        )
        
        success = result.returncode == 0
        output = result.stdout
        error = result.stderr if not success else None
        
        return {
            "success": success,
            "output": output,
            "error": error,
            "returncode": result.returncode
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Code execution timed out after {timeout} seconds",
            "output": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Execution error: {str(e)}",
            "output": ""
        }
    finally:
        # Clean up temp file
        try:
            Path(temp_file).unlink()
        except:
            pass


def extract_import_modules(code: str) -> List[str]:
    """
    Extract top-level imported module names from Python source using AST.

    Returns a list of unique top-level module names, e.g.
    - 'numpy' from 'import numpy as np'
    - 'numpy' from 'from numpy import array'
    """
    modules: Set[str] = set()
    try:
        tree = ast.parse(code)
    except Exception:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # ignore relative imports (from .foo import bar)
            if getattr(node, "level", 0) and node.level > 0:
                continue
            if node.module:
                modules.add(node.module.split(".")[0])

    return sorted(modules)


def check_imports(modules: List[str], timeout: int = 10) -> Dict[str, Any]:
    """
    Try importing each module in an isolated subprocess.

    Returns:
      {
        "modules": [...],
        "missing": [...],          # subset where ModuleNotFoundError
        "failed": {mod: err},      # other import-time exceptions
        "success": bool
      }
    """
    missing: List[str] = []
    failed: Dict[str, str] = {}

    for mod in modules:
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {mod}"],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd(),
            )
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                # Normalize "No module named X"
                if "ModuleNotFoundError" in stderr or "No module named" in stderr:
                    missing.append(mod)
                else:
                    failed[mod] = stderr[:1000]
        except subprocess.TimeoutExpired:
            failed[mod] = f"Import timed out after {timeout}s"
        except Exception as e:
            failed[mod] = str(e)

    return {
        "modules": modules,
        "missing": missing,
        "failed": failed,
        "success": (len(missing) == 0 and len(failed) == 0),
    }


def validate_code_syntax(code: str) -> Dict[str, Any]:
    """
    Validate Python code syntax without executing it.
    
    Args:
        code: Python code to validate
        
    Returns:
        Dictionary with 'valid' and 'error' keys
    """
    try:
        compile(code, '<string>', 'exec')
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax error: {e.msg} at line {e.lineno}"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Error: {str(e)}"
        }

