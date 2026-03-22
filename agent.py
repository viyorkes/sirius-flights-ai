from datetime import datetime
from typing import AsyncGenerator
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from tools.registry import get_tools
from rag.retriever import query_knowledge_base
from config import get_settings
from exceptions import AgentError

settings = get_settings()

sessions: dict = {}


def get_or_create_session(session_id: str) -> list:
    if session_id not in sessions:
        sessions[session_id] = []
    return sessions[session_id]


def extract_output(result: dict) -> str:
    """Extracts string output from agent result regardless of format."""
    output = result.get("output", "")
    if isinstance(output, list):
        return " ".join([
            item.get("text", "")
            for item in output
            if isinstance(item, dict) and item.get("type") == "text"
        ])
    return str(output)


def extract_tools_used(result: dict) -> list:
    """Extracts list of tools used from intermediate steps."""
    tools_used = []
    if "intermediate_steps" in result:
        for action, _ in result["intermediate_steps"]:
            if hasattr(action, "tool") and action.tool not in tools_used:
                tools_used.append(action.tool)
    return tools_used


def build_agent():
    llm = ChatAnthropic(
        model=settings.model,
        anthropic_api_key=settings.anthropic_api_key,
        max_tokens=settings.max_tokens
    )

    tools = get_tools()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""You are Sirius, an intelligent flight search assistant powered by AI.
You help users find the best flights, compare prices, and plan their trips.

Today's date is {datetime.now().strftime('%Y-%m-%d')}.

Guidelines:
- Always use tools to search for real flight data — never make up prices or schedules
- Use IATA airport codes (GRU, JFK, LHR, CDG) when calling tools
- When user mentions a city, convert to the main airport IATA code
- Always use future dates when searching for flights
- Always present prices clearly with currency
- Suggest alternatives when no exact match is found
- Be concise, friendly and helpful
- If the user asks about travel tips, visa info or destination advice, use your knowledge base"""
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
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )


def run_agent(message: str, session_id: str = "default") -> dict:
    try:
        history = get_or_create_session(session_id)
        agent_executor = build_agent()

        rag_context = ""
        try:
            rag_context = query_knowledge_base(message)
        except Exception:
            pass

        enriched_message = message
        if rag_context:
            enriched_message = f"{message}\n\n[Travel Knowledge Context]: {rag_context}"

        result = agent_executor.invoke({
            "input": enriched_message,
            "chat_history": history
        })

        output = extract_output(result)
        tools_used = extract_tools_used(result)

        history.append(HumanMessage(content=message))
        history.append(AIMessage(content=output))

        if len(history) > 10:
            sessions[session_id] = history[-10:]

        return {
            "reply": output,
            "session_id": session_id,
            "tools_used": tools_used
        }

    except Exception as e:
        raise AgentError(
            message="Agent failed to process request",
            details={"error": str(e), "session_id": session_id}
        )


async def stream_agent(message: str, session_id: str = "default") -> AsyncGenerator[str, None]:
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
                f"""You are Sirius, an intelligent flight search assistant.
Today's date is {datetime.now().strftime('%Y-%m-%d')}.
Use the available tools to search for real flight data.
Always use IATA airport codes when calling tools.
Always use future dates when searching.
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
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

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
                if isinstance(token, list):
                    token = " ".join([
                        item.get("text", "")
                        for item in token
                        if isinstance(item, dict) and item.get("type") == "text"
                    ])
                full_response += token
                yield token

        history.append(HumanMessage(content=message))
        history.append(AIMessage(content=full_response))

        if len(history) > 10:
            sessions[session_id] = history[-10:]

    except Exception as e:
        raise AgentError(
            message="Streaming agent failed",
            details={"error": str(e), "session_id": session_id}
        )