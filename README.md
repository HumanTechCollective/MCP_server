# MCP Server 

A Model Context Protocol (MCP) server built with Python that serves agenda data for an event. 
This project is also a reusable template for building MCP servers.

## Goals

- Learn to build MCP servers with Python.
- Create a template project that can be reused for other MCP servers.
- Provide a step-by-step workshop for the attendees.
- Build a demo MCP server that answers questions about the event agenda.

## Repository layout

```
├── data/
│   ├── sample_database.db     # SQLite database with sample agenda data
│   └── sample_talks.json      # Sample agenda data in JSON
├── documentation/
│   ├── tools.md               # What are tools and how they work
│   ├── workshop.md            # Step-by-step workshop instructions (English)
│   └── workshop_es.md         # Step-by-step workshop instructions (Spanish)
├── src/
│   ├── client.py              # LLM client with tool calling
│   ├── config.py              # Configuration (Ollama URL, model, etc.)
│   └── tools.py               # Tool functions, schemas, and execution
├── tests/
│   ├── test_client.py         # Client tests
│   └── test_tools.py          # Tool function tests
└── .env.sample                # Environment variables template
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pytest python-dotenv langchain_core langchain_ollama
```
