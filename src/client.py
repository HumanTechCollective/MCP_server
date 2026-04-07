"""Simple client that sends queries to an LLM with tool access."""

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, ToolMessage

from src.config import ollama_url, ollama_api_key, ollama_model
from src.tools import tools, execute_tool


def create_llm() -> ChatOllama:
    kwargs = {
        "model": ollama_model,
        "base_url": ollama_url,
    }
    if ollama_api_key:
        kwargs["client_kwargs"] = {
            "headers": {"Authorization": f"Bearer {ollama_api_key}"}
        }
    return ChatOllama(**kwargs)


def process_query(query) -> str:
    """Send a query to the LLM, let it call tools if needed, return the final answer."""
    llm = create_llm()

    # Bind our tool schemas so the LLM knows what it can call
    llm_with_tools = llm.bind_tools(tools)

    messages = [HumanMessage(content=query)]

    # Loop: send message, execute tool calls, repeat until we get a text answer
    while True:
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # If the LLM didn't request any tool calls, we're done
        if not response.tool_calls:
            return response.content

        # Execute each tool call and send the results back
        for tool_call in response.tool_calls:
            print(f"Calling tool: {tool_call['name']} with args: {tool_call['args']}")
            result = execute_tool(tool_call["name"], tool_call["args"])
            messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"]))


if __name__ == "__main__":
    print("Type your queries or 'quit' to exit.\n")
    while True:
        query = input("Query: ").strip()
        if query.lower() == "quit":
            break
        answer = process_query(query)
        print(f"\n{answer}\n")
