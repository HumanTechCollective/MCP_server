"""Client that talks to an MCP server and exposes its tools to an LLM."""

import asyncio

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from src.config import ollama_url, ollama_api_key, ollama_model, system_prompt, mcp_host, mcp_port

mcp_server_url = f"http://{mcp_host}:{mcp_port}/mcp"


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


def mcp_tool_to_schema(tool) -> dict:
    """Convert an MCP tool definition into the dict format bind_tools expects."""
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.inputSchema,
    }


def tool_result_to_string(result) -> str:
    """Stringify the content of a CallToolResult for the LLM."""
    parts = [p.text for p in result.content if hasattr(p, "text")]
    return "\n".join(parts)


async def process_query(session, llm_with_tools, query) -> str:
    """Send a query to the LLM, let it call MCP tools if needed, return the final answer."""
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=query)]

    # Loop: send message, execute tool calls over MCP, repeat until we get a text answer
    while True:
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        # If the LLM didn't request any tool calls, we're done
        if not response.tool_calls:
            return response.content

        # Execute each tool call via MCP and send the results back
        for tool_call in response.tool_calls:
            print(f"Calling tool: {tool_call['name']} with args: {tool_call['args']}")
            result = await session.call_tool(tool_call["name"], tool_call["args"])
            messages.append(ToolMessage(
                content=tool_result_to_string(result),
                tool_call_id=tool_call["id"],
            ))


async def main():
    # Connect to the already-running MCP server over streamable HTTP
    async with (
        streamable_http_client(mcp_server_url) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        await session.initialize()

        # Discover tools from the server and bind them to the LLM
        tools_result = await session.list_tools()
        tool_schemas = [mcp_tool_to_schema(t) for t in tools_result.tools]
        llm_with_tools = create_llm().bind_tools(tool_schemas)

        print("Type your queries or 'quit' to exit.\n")
        while True:
            query = input("Query: ").strip()
            if query.lower() == "quit":
                break
            answer = await process_query(session, llm_with_tools, query)
            print(f"\n{answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
