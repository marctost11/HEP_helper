from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.chains import LLMChain
from .llm import get_llm
from .memory import get_memory
from .prompts import SYSTEM_PROMPT
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory

def build_agent(tools=None):
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        #MessagesPlaceholder("agent_scratchpad"),
    ])

    llm = get_llm()
    chain = prompt | llm

    agent = RunnableWithMessageHistory(
        chain,
        get_memory,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return agent
