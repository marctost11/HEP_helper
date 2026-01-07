"""LangGraph workflow for sophisticated agent with planning, testing, and code generation phases.
Python 3.10+ only.
"""
from __future__ import annotations

import sys
import os
from typing import TypedDict, Annotated, Literal

if sys.version_info < (3, 10):
    raise RuntimeError(
        f"HEP_helper requires Python 3.10+ (you have {sys.version_info.major}.{sys.version_info.minor})."
    )
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import operator

from .llm import get_llm
from .prompts import get_system_prompt
from .code_executor import (
    extract_code_blocks,
    validate_code_syntax,
    extract_import_modules,
    check_imports,
)


MAX_CONTEXT_MESSAGES = 10


def _tail_messages(messages: list[BaseMessage], n: int = MAX_CONTEXT_MESSAGES) -> list[BaseMessage]:
    """Keep only the last N messages to avoid huge prompts / TPM spikes."""
    if len(messages) <= n:
        return messages
    return messages[-n:]


class AgentState(TypedDict):
    """State schema for the LangGraph workflow."""
    messages: Annotated[list[BaseMessage], operator.add]
    phase: Literal["planning", "code_generation", "import_check", "testing", "complete"]
    requirements: dict  # Collected requirements from planning phase
    generated_code: str  # Generated code
    import_results: dict  # Results from import-check phase
    test_results: dict  # Results from code testing
    iteration_count: int  # Track iterations to prevent infinite loops


def route_phase(state: AgentState) -> Literal["planning", "code_generation", "import_check", "testing", "complete"]:
    """
    Decide which phase node to run for this *turn*.

    IMPORTANT: This graph is intentionally turn-based (one phase step per user input)
    to keep latency reasonable and avoid accidental multi-LLM-call loops.
    """
    return state.get("phase", "planning")  # type: ignore[return-value]


def create_planning_prompt() -> ChatPromptTemplate:
    """Create prompt for the planning phase."""
    return ChatPromptTemplate.from_messages([
        ("system", """You are a particle physics analysis agent in PLANNING mode.

Your goal is to gather all necessary information from the user to generate working code.

Ask clarifying questions about:
- Dataset format and location
- Specific analysis goals (what physics to extract)
- Any constraints or preferences

Once you have enough information, summarize the requirements and ask the user if they are ready to proceed to code generation, or would like to provide additional guidance. If they are ready, say "READY_TO_CODE"."""),
        MessagesPlaceholder("messages"),
    ])


def create_code_generation_prompt() -> ChatPromptTemplate:
    """Create prompt for code generation phase."""
    # Keep examples small to avoid TPM spikes (your org limit is 30k TPM).
    system_prompt = get_system_prompt(
        examples_dir=os.getenv("HEP_EXAMPLES_DIR", "examples/hep-programming-hints"),
        max_chars=int(os.getenv("HEP_EXAMPLES_MAX_CHARS", "20000")),
        include_examples=os.getenv("HEP_USE_EXAMPLES", "1") not in {"0", "false", "False", "no", "NO"},
    )
    return ChatPromptTemplate.from_messages([
        ("system", f"""{system_prompt}

You are now in CODE GENERATION mode. Generate complete, executable Python code based on the requirements.

IMPORTANT:
- Output a SINGLE complete script as one ```python``` block (not multiple fragments).
- Structure like the provided examples: imports first, then configuration/constants, then helper functions, then a `main()` and `if __name__ == "__main__": main()`.
- Avoid placeholders like TODO/INSERT/REPLACE; if something is unknown, ask in planning instead.
- Generate complete, runnable code blocks wrapped in ```python code blocks
- Include all necessary imports
- Make sure the code is self-contained and executable
- Follow the examples and patterns from the code examples
- When done, say "CODE_READY" to proceed to testing."""),
        MessagesPlaceholder("messages"),
    ])


def planning_node(state: AgentState) -> AgentState:
    """Node for planning phase - gather requirements from user."""
    messages = state.get("messages", [])
    llm = get_llm()
    prompt = create_planning_prompt()
    
    chain = prompt | llm
    response = chain.invoke({"messages": _tail_messages(messages, n=12)})
    
    # Check if ready to move to code generation
    if "READY_TO_CODE" in response.content.upper():
        # Extract requirements summary
        requirements = {
            "summary": response.content,
            "conversation": [msg.content for msg in messages if isinstance(msg, (HumanMessage, AIMessage))]
        }
        return {
            **state,  # Preserve existing state
            "messages": messages + [response],
            "phase": "code_generation",
            "requirements": requirements,
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    # Still in planning - need more info
    return {
        **state,  # Preserve existing state
        "messages": messages + [response],
        "phase": "planning",
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def code_generation_node(state: AgentState) -> AgentState:
    """Node for code generation phase - generate Python code."""
    messages = state.get("messages", [])
    llm = get_llm()
    prompt = create_code_generation_prompt()
    
    # Add requirements summary to context if available
    requirements = state.get("requirements", {})
    if requirements and requirements.get("summary"):
        requirements_context = f"\n\nRequirements Summary:\n{requirements.get('summary', 'N/A')}\n"
        enhanced_messages = _tail_messages(messages) + [HumanMessage(content=requirements_context)]
    else:
        enhanced_messages = _tail_messages(messages)
    
    chain = prompt | llm
    response = chain.invoke({"messages": enhanced_messages})
    
    # Extract code from response
    code_blocks = extract_code_blocks(response.content)
    generated_code = "\n\n".join(code_blocks) if code_blocks else ""
    
    return {
        **state,  # Preserve existing state
        "messages": messages + [response],
        "phase": "import_check",
        "generated_code": generated_code,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def import_check_node(state: AgentState) -> AgentState:
    """
    Check all import statements independently.

    This phase does NOT execute the script — it only imports the modules in isolation
    and reports missing modules to the user.
    """
    messages = state.get("messages", [])
    code = state.get("generated_code", "") or ""

    modules = extract_import_modules(code)
    results = check_imports(modules)

    if results["success"]:
        msg = AIMessage(content="✅ Import check passed (all imported modules are available).")
        return {
            **state,
            "messages": messages + [msg],
            "phase": "testing",
            "import_results": results,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    missing = results.get("missing", [])
    failed = results.get("failed", {})

    lines = ["❌ Import check failed."]
    if missing:
        lines.append("")
        lines.append("Missing modules (ModuleNotFoundError):")
        for m in sorted(set(missing)):
            lines.append(f"- {m}")
    if failed:
        lines.append("")
        lines.append("Modules that raised an error during import:")
        for m, err in failed.items():
            first_line = (err.splitlines()[0] if err else "unknown error")
            lines.append(f"- {m}: {first_line}")
    lines.append("")
    lines.append("Install missing modules, or ask me to regenerate code using only available packages.")

    msg = AIMessage(content="\n".join(lines))
    return {
        **state,
        "messages": messages + [msg],
        "phase": "code_generation",
        "import_results": results,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def testing_node(state: AgentState) -> AgentState:
    """Node for testing phase - SYNTAX ONLY (no execution)."""
    messages = state.get("messages", [])
    code = state.get("generated_code", "")
    
    if not code:
        # No code to test, go back to code generation
        return {
            **state,  # Preserve existing state
            "messages": messages + [
                AIMessage(content="No code found in the response. Please generate code.")
            ],
            "phase": "code_generation",
            "iteration_count": state.get("iteration_count", 0) + 1
        }
    
    syntax = validate_code_syntax(code)
    if syntax["valid"]:
        test_results = {"success": True, "mode": "syntax_only"}
        test_message = "✅ Syntax check passed (no execution performed)."
    else:
        test_results = {"success": False, "mode": "syntax_only", "error": syntax.get("error")}
        test_message = f"❌ Syntax check failed:\n\n{syntax.get('error', 'Unknown syntax error')}"
    
    # Add test results to messages
    test_msg = AIMessage(content=test_message)

    if test_results["success"]:
        # Mark complete; `run.py` will print the final code.
        return {
            **state,
            "messages": messages + [test_msg],
            "phase": "complete",
            "test_results": test_results,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    # On failure, stay in code_generation for the next turn; include the error in history.
    return {
        **state,
        "messages": messages + [test_msg],
        "phase": "code_generation",
        "test_results": test_results,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def build_graph() -> StateGraph:
    """Build and return the LangGraph workflow."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", lambda s: s)
    workflow.add_node("planning", planning_node)
    workflow.add_node("code_generation", code_generation_node)
    workflow.add_node("import_check", import_check_node)
    workflow.add_node("testing", testing_node)
    
    # Turn-based entry point
    workflow.set_entry_point("router")

    # Route to exactly one phase per turn
    workflow.add_conditional_edges(
        "router",
        route_phase,
        {
            "planning": "planning",
            "code_generation": "code_generation",
            "import_check": "import_check",
            "testing": "testing",
            "complete": END,
        },
    )

    # End the turn after each node. (No internal loops.)
    workflow.add_edge("planning", END)
    workflow.add_edge("code_generation", "import_check")
    # import_check decides whether we proceed to syntax-check or stop early (request regen)
    workflow.add_conditional_edges(
        "import_check",
        lambda s: "testing" if s.get("phase") == "testing" else "end",
        {"testing": "testing", "end": END},
    )
    workflow.add_edge("testing", END)
    
    # IMPORTANT: return the uncompiled workflow here.
    # We compile in `create_agent_with_graph()` so we can optionally attach a checkpointer.
    return workflow


def create_agent_with_graph():
    """Create an agent instance using the LangGraph workflow."""
    graph = build_graph()

    # If `build_graph()` ever returns an already-compiled graph (older codepath),
    # just return it as-is.
    if not hasattr(graph, "compile"):
        return graph

    from langgraph.checkpoint.memory import MemorySaver

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)

