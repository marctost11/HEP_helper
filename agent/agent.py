"""Builds the LangGraph-based Physics Agent (Python 3.10+ required)."""
from __future__ import annotations

import sys

if sys.version_info < (3, 10):
    raise RuntimeError(
        f"HEP_helper requires Python 3.10+ (you have {sys.version_info.major}.{sys.version_info.minor})."
    )

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from .llm import get_llm
from .memory import get_memory
from .prompts import SYSTEM_PROMPT


def build_agent(tools=None, use_graph: bool = True):
    """Build and return an agent (LangGraph or legacy chain).

    Args:
        tools: Optional list of tools (ignored if use_graph=True).
        use_graph: Use LangGraph workflow if True.

    Returns:
        Agent instance (LangGraph app or RunnableWithMessageHistory).
    """
    if use_graph:
        from .graph import create_agent_with_graph
        return create_agent_with_graph()

    # Legacy mode—simple history-based chain
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    llm = get_llm()
    chain = prompt | llm
    return RunnableWithMessageHistory(
        chain,
        get_memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
