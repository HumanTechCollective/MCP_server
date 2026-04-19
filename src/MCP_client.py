"""Client that talks to an MCP server and exposes its tools to an LLM."""

import asyncio

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from src.config import ollama_url, ollama_api_key, ollama_model, system_prompt, mcp_server_url


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


async def fetch_all_resources(session) -> str:
    """Read every resource from the MCP server, formatted for the system prompt."""
    result = await session.list_resources()
    if not result.resources:
        return ""
    sections = ["## Reference resources"]
    for resource in result.resources:
        content = await session.read_resource(resource.uri)
        texts = [c.text for c in content.contents if hasattr(c, "text")]
        sections.append(f"### {resource.name}\n" + "\n".join(texts))
    return "\n\n".join(sections)


async def process_query(session, llm_with_tools, query, system_prompt, conversation=None) -> str:
    """Send a query to the LLM, let it call MCP tools if needed, return the final answer.

    If `conversation` is a list, prior user/assistant turns from it are prepended to
    the LLM input, and the new (user question, final answer) pair is appended in place.
    """
    prior = conversation if conversation is not None else []
    messages = [SystemMessage(content=system_prompt), *prior, HumanMessage(content=query)]

    # Loop: send message, execute tool calls over MCP, repeat until we get a text answer
    while True:
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        # If the LLM didn't request any tool calls, we're done
        if not response.tool_calls:
            if conversation is not None:
                # Store only the clean user/assistant pair — no tool-call scaffolding
                conversation.append(HumanMessage(content=query))
                conversation.append(AIMessage(content=response.content))
            return response.content

        # Execute each tool call via MCP and send the results back
        for tool_call in response.tool_calls:
            print(f"Calling tool: {tool_call['name']} with args: {tool_call['args']}")
            result = await session.call_tool(tool_call["name"], tool_call["args"])
            messages.append(ToolMessage(
                content=tool_result_to_string(result),
                tool_call_id=tool_call["id"],
            ))


async def setup_llm_with_tools(session):
    """Discover tools from the MCP server and bind them to a fresh LLM."""
    tools_result = await session.list_tools()
    tool_schemas = [mcp_tool_to_schema(t) for t in tools_result.tools]
    return create_llm().bind_tools(tool_schemas)


async def main():
    # Connect to the already-running MCP server over streamable HTTP
    async with (
        streamable_http_client(mcp_server_url) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        llm_with_tools = await setup_llm_with_tools(session)
        # Pull resources once at startup and append them to the system prompt,
        # so every turn sees the same reference context without re-reading.
        resources_text = await fetch_all_resources(session)
        augmented_prompt = system_prompt + (f"\n\n{resources_text}" if resources_text else "")

        # Single conversation for this CLI session — grows in place on each query
        conversation = []
        print("Type your queries or 'quit' to exit.\n")
        while True:
            query = input("Query: ").strip()
            if query.lower() == "quit":
                break
            answer = await process_query(session, llm_with_tools, query, augmented_prompt, conversation)
            print(f"\n{answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
