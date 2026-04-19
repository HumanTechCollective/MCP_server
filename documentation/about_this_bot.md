# About this project

This document explains what this Telegram bot is, how it is built, and where its
code lives. It is intended as a reference the bot itself can consult when users
ask about its implementation.

## What it is

A chatbot that answers questions about an event agenda. Users talk to it through
Telegram, and behind the scenes it uses a Large Language Model (LLM) connected
to a Model Context Protocol (MCP) server that exposes the agenda data.

The same codebase also works as a reusable template for building other MCP
servers with Python.

## Open source

This is an open source project. The source code is published on GitHub:

**Repository:** https://github.com/HumanTechCollective/MCP_server

Anyone can read the code, run it locally, adapt it, or contribute.

## Workshop at Codemotion Madrid 2026

A hands-on workshop that walks through how this bot is built step by step will
be given at **Codemotion Madrid 2026** on **April 21st, 2026 at 13:00**.

The full workshop material is in [workshop.md](workshop.md). It covers:

1. Writing plain Python tool functions that query the agenda database.
2. Connecting those tools to an LLM through a client.
3. Wrapping the tools in an MCP server so any MCP-compatible app can use them.
4. Writing an MCP client that discovers tools at runtime.

## How it works

The project is organized in layers, each one building on the previous:

### 1. Tools

Python functions that query the agenda database (a SQLite file):

- `get_all_talks()` — returns every talk in the agenda.
- `get_talks_by_day(day)` — returns talks for a given day.
- `get_talk_details(title)` — returns the details of a specific talk.

The LLM does not run these functions directly. It decides *when* to call one,
and the client executes it and sends the result back.

### 2. MCP server

The tools are exposed through an MCP server built with `FastMCP`. Each tool is
registered with a `@mcp.tool()` decorator, and `FastMCP` generates the schema
that MCP clients use to discover the tools.

The server runs over HTTP (`streamable-http` transport) so clients can connect
remotely.

### 3. MCP client

The client opens a session with the MCP server, asks it *"what tools do you
have?"* (`session.list_tools()`), and hands those tools to the LLM. When the
LLM decides to use one, the client runs it through `session.call_tool(name, args)`
and feeds the result back to the LLM.

The client never imports the tool code directly — it only speaks MCP. That
means the same client could talk to any other MCP server without changes.

### 4. Telegram bot

A thin layer on top of the MCP client that:

- Listens for Telegram messages.
- Keeps a separate conversation history per user.
- Forwards each question to the MCP client and sends the LLM's answer back to
  the user.

## Tech stack

- **Python 3.10+** for everything.
- **FastMCP** (from the MCP SDK) to build the MCP server.
- **LangChain** (`langchain_core`, `langchain_ollama`) to talk to the LLM.
- **Ollama** as the LLM backend — either Ollama Cloud or a self-hosted server.
- **python-telegram-bot** for the Telegram integration.
- **SQLite** for the agenda database.
- **pytest** for testing.

## Project philosophy

The project is designed to be understood, not just used. Every piece of code is
meant to be readable and explainable, and the workshop follows the same
principle: build small, working pieces one at a time, and understand each one
before moving on.
