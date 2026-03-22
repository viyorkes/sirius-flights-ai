import json
from typing import AsyncGenerator
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage
from tools.registry import get_tools
from rag.retriever import query_knowledge_base
from config import get_settings
from exceptions import AgentError

settings = get_settings()

# In-memory session store
# Java equivalent: private static Map<String, List<Message>> sessions = new HashMap<>();
sessions: dict = {}


def get_or_create_session(session_id: str) -> list:
    """Returns existing session history or creates a new one."""
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]


def build_agent():
    """
    Builds and returns the LangChain agent with tools.
    Called once per request — stateless agent, stateful memory via sessions.
    """
    llm = ChatAnthropic(
        model=settings.model,
        anthropic_api_key=settings.anthropic_api_key,
        max_tokens=settings.max_tokens
    )

    tools = get_tools()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are Sirius, an intelligent flight search assistant powered by AI.
You help users find the best flights, compare prices, and plan their trips.

Guidelines:
- Always use tools to search for real flight data — never make up prices or schedules
- Use IATA airport codes (GRU, JFK, LHR, CDG) when calling tools
- When user mentions a city, convert to the main airport IATA code
- Always present prices clearly with currency
- Suggest alternatives when no exact match is found
- Be concise, friendly and helpful
- If the user asks about travel tips, visa info or destination advice, use your knowledge base

Today's date context: you are helping users plan future travel."""
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )


def run_agent(message: str, session_id: str = "default") -> dict:
    """
    Runs the agent synchronously.
    Returns the full response with tools used.
    """
    try:
        history = get_or_create_session(session_id)
        agent_executor = build_agent()

        # Try to enrich with RAG context
        rag_context = ""
        try:
            rag_context = query_knowledge_base(message)
        except Exception:
            pass  # RAG is optional — agent works without it

        enriched_message = message
        if rag_context:
            enriched_message = f"{message}\n\n[Travel Knowledge Context]: {rag_context}"

        result = agent_executor.invoke({
            "input": enriched_message,
            "chat_history": history
        })

        # Update session history
        history.append(HumanMessage(content=message))
        history.append(AIMessage(content=result["output"]))

        # Keep last 10 messages only
        if len(history) > 10:
            sessions[session_id] = history[-10:]

        return {
            "reply": result["output"],
            "session_id": session_id,
            "tools_used": []
        }

    except Exception as e:
        raise AgentError(
            message="Agent failed to process request",
            details={"error": str(e), "session_id": session_id}
        )


async def stream_agent(message: str, session_id: str = "default") -> AsyncGenerator[str, None]:
    """
    Runs the agent with streaming — yields chunks as they arrive.
    Used by the SSE endpoint in main.py.
    """
    try:
        history = get_or_create_session(session_id)

        llm = ChatAnthropic(
            model=settings.model,
            anthropic_api_key=settings.anthropic_api_key,
            max_tokens=settings.max_tokens,
            streaming=True
        )

        tools = get_tools()

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are Sirius, an intelligent flight search assistant.
Use the available tools to search for real flight data.
Always use IATA airport codes when calling tools.
Be concise, friendly and helpful."""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=5,
            handle_parsing_errors=True
        )

        # Try RAG enrichment
        rag_context = ""
        try:
            rag_context = query_knowledge_base(message)
        except Exception:
            pass

        enriched_message = message
        if rag_context:
            enriched_message = f"{message}\n\n[Travel Knowledge Context]: {rag_context}"

        full_response = ""

        async for chunk in agent_executor.astream(
            {"input": enriched_message, "chat_history": history}
        ):
            if "output" in chunk:
                token = chunk["output"]
                full_response += token
                yield token

        # Update session history
        history.append(HumanMessage(content=message))
        history.append(AIMessage(content=full_response))

        if len(history) > 10:
            sessions[session_id] = history[-10:]

    except Exception as e:
        raise AgentError(
            message="Streaming agent failed",
            details={"error": str(e), "session_id": session_id}
        )