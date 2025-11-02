"""
Agent module: initializes LangGraph/Groq model and runs agricultural assistant queries.
Uses a ReAct-style reasoning agent with a web-search tool (Tavily).
"""

from typing import TypedDict
from langchain.tools import StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain.schema import SystemMessage, HumanMessage
from app.config import TAVILY_API_KEY, GROQ_API_KEY


# ---------- Tavily Search Tool ----------
def extract_search_results(raw_results):
    """Format Tavily search results into readable text."""
    extracted = []
    for item in raw_results:
        url = item.get("url", "")
        title = item.get("title", "")
        content = item.get("content", "")
        block = f"URL: {url}\nTitle: {title}\nContent: {content}\n---\n"
        extracted.append(block)
    return "\n".join(extracted)


web_search = TavilySearchResults(
    search_depth="basic",
    max_results=3,
    tavily_api_key=TAVILY_API_KEY,
    include_raw_content=False,
    include_images=False,
    include_answer=False,
)

class WebSearchInput(TypedDict):
    query: str

def web_search_tool_fn(query: str) -> str:
    """Search agricultural info (chemicals, fertilizers, etc.)"""
    try:
        print(f"[Search] Query: {query}")
        res = web_search.invoke({"query": query})
        if isinstance(res, str):
            return res
        raw = res.get("results", []) if isinstance(res, dict) else []
        if not raw:
            return "No relevant results found."
        return extract_search_results(raw)
    except Exception as e:
        return f"[Search Error]: {e}"

web_search_tool = StructuredTool.from_function(
    func=web_search_tool_fn,
    name="web_search_tool",
    description="Search agricultural information using Tavily.",
)


# ---------- Agent Initialization ----------
def initialize_agent():
    """Create and return a LangGraph ReAct agent."""
    try:
        print("[Agent] Initializing agent...")
        memory = MemorySaver()
        model = ChatGroq(
            model="openai/gpt-oss-120b",  
            temperature=0.3,
            max_tokens=1500,
            api_key=GROQ_API_KEY,
        )
        tools = [web_search_tool]
        agent_executor = create_react_agent(model, tools, checkpointer=memory)
        print("[Agent] Initialized.")
        return agent_executor
    except Exception as e:
        print(f"[Agent] Initialization error: {e}")
        return None


# ---------- Message Builder ----------
def chat_completion(user_input: str):
    """Convert user input into a structured prompt for the agent."""
    return [
        SystemMessage(
            content=(
                "You are a helpful agricultural assistant for farmers in Pakistan. "
                "You explain the usage, safety, and crop compatibility of agricultural "
                "chemicals like pesticides, herbicides, and fertilizers.\n\n"
                "If you are unsure, use the web_search_tool once to check reliable sources. "
                "Keep your answer short, clear, and practical."
            )
        ),
        HumanMessage(content=user_input),
    ]


# ---------- Main Query Runner ----------
def run_query(input_message, agent_executor=None):
    """Run the ReAct agent and return its textual response."""
    if agent_executor is None:
        agent_executor = initialize_agent()
        if agent_executor is None:
            return "Agent initialization failed."

    try:
        print("[Agent] Running query...")
        config = {"configurable": {"thread_id": "farmguide-session"}}
        response_text = ""

        for step in agent_executor.stream(
            {"messages": input_message}, config, stream_mode="values"
        ):
            messages = step.get("messages") if isinstance(step, dict) else getattr(step, "messages", None)
            if not messages:
                continue

            latest = messages[-1]
            role = getattr(latest, "role", None)
            content = getattr(latest, "content", None)

            if role in ("assistant", "ai") and content:
                response_text = content

        response_text = response_text or "No answer produced by agent."
        print(f"[Agent] Response: {response_text[:300]}")
        return response_text

    except Exception as e:
        print(f"[Agent] Execution error: {e}")
        return f"Agent execution error: {e}"


