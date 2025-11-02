# app/agent.py
"""
Agent stubs for FarmGuide
These are placeholders for AI agent functions to make main.py run.
Replace with real AI agent logic (LangChain, OpenAI, or other model) as needed.
"""

import time

# ---------- Agent Executor Stub ----------
class AgentExecutor:
    """
    Mimics an agent executor with a simple streaming interface.
    Yields messages in the format expected by main.py.
    """
    def stream(self, data, config=None, stream_mode=None):
        """
        Simple generator to simulate streaming responses.
        """
        # Simulate a delay for streaming
        time.sleep(0.5)
        # Yield one message as if from the AI
        yield {"messages": [{"role": "assistant", "content": "Based on the OCR and farmer query, this is a safe organic fertilizer. Apply bi-weekly as instructed."}]}

# ---------- Initialize Agent ----------
def initialize_agent():
    """
    Stub function to 'initialize' the AI agent.
    Returns an AgentExecutor instance.
    """
    print("[Agent] Initializing agent executor...")
    return AgentExecutor()

# ---------- Chat Completion Stub ----------
def chat_completion(user_input):
    """
    Converts user input string to a messages list.
    """
    return [{"role": "user", "content": user_input}]

# ---------- Run Query Stub ----------
def run_query(input_message, agent_executor=None):
    """
    Simulates running a query through the agent.
    Returns a response string.
    """
    if not agent_executor:
        agent_executor = initialize_agent()
    for step in agent_executor.stream({"messages": chat_completion(input_message)}):
        messages = step.get("messages", [])
        if messages:
            latest_msg = messages[-1]
            if isinstance(latest_msg, dict):
                return latest_msg.get("content", "")
    return "No response available."

# ---------- Web Search Tool Stub ----------
def web_search_tool(query):
    """
    Placeholder for a web search function.
    Returns a canned response.
    """
    print(f"[WebSearch] Query: {query}")
    return f"Simulated search result for: {query}"
