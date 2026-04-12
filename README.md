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
│   ├── tools.py               # Tool functions, schemas, and execution
│   └── MCP_server.py          # MCP server exposing the agenda tools
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
pip install pytest python-dotenv langchain_core langchain_ollama "mcp[cli]"
```

### LLM setup

Copy `.env.sample` to `.env`:

```bash
cp .env.sample .env
```

You have two options for the LLM backend:

#### Option 1: Ollama Cloud

Create an account at [ollama.com](https://ollama.com) and get an [API key](https://ollama.com/settings/keys).

Fill your `.env`:

```
OLLAMA_URL=https://ollama.com
OLLAMA_API_KEY=<your API key>
```

> **Note:** Other providers (OpenAI, Anthropic, etc.) require small changes in [src/client.py](src/client.py).  
> Check [Langchain documentation for chat models integrations](https://docs.langchain.com/oss/python/integrations/chat).

#### Option 2: Your own Ollama server

Install Ollama and pull a model:

```bash
sudo apt install curl
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4
```

Fill your `.env`:

```
OLLAMA_URL=http://localhost:11434
OLLAMA_API_KEY=
```

> **Note:** You can use a smaller model instead of `gemma4`. Browse the available
> [models with tool support](https://ollama.com/search?c=tools).  
> To use a different model, pull it with `ollama pull <model>` and update the model name in
> [src/config.py](src/config.py).


## Run the MCP server

The MCP server exposes the agenda tools over the Model Context Protocol so any
MCP-compatible client can use them.

Run it from the project root:

```bash
source .venv/bin/activate
python -m src.MCP_server
```

## Try the chatbot
```bash
source .venv/bin/activate
python -m src.client
```
