"""Tests for the MCP server over an in-memory transport."""

import anyio
from mcp.shared.memory import create_connected_server_and_client_session

from src.MCP_server import mcp

EVENT_DAY = "2026-04-20"


def test_server_exposes_expected_tools():
    async def run():
        async with create_connected_server_and_client_session(mcp) as session:
            result = await session.list_tools()
            return [t.name for t in result.tools]

    tool_names = anyio.run(run)

    assert set(tool_names) == {"get_talks_by_day", "get_all_talks", "get_talk_details"}


def test_call_get_talks_by_day_returns_talks():
    async def run():
        async with create_connected_server_and_client_session(mcp) as session:
            return await session.call_tool("get_talks_by_day", {"day": EVENT_DAY})

    result = anyio.run(run)

    # FastMCP returns list[dict] under structuredContent["result"]
    talks = result.structuredContent["result"]
    assert len(talks) > 0
    for key in ("title", "start_time", "speakers", "topic", "stage", "languages", "type"):
        assert key in talks[0]
