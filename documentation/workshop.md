# Build an MCP server with Python

Also available in: [Español](workshop_es.md)

> Hands-on workshop where we'll build step by step a chatbot that answers questions
> about a talks agenda. We'll start by connecting tools to an LLM and finish by
> wrapping them in a reusable Model Context Protocol (MCP) server.

## What we'll build

A Model Context Protocol (MCP) server that lets an AI assistant answer questions
about the stored data.

## Prerequisites

- Python 3.10 or higher
- A text editor or IDE
- Basic Python knowledge
- Basic understanding of Large Language Models (LLMs) — what they are and what they do


## 0. Setup

Clone the repository and install the dependencies:

```bash
git clone https://github.com/HumanTechCollective/MCP_server.git
cd MCP_server
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pytest python-dotenv langchain_core langchain_ollama
```

Create an account at [ollama.com](https://ollama.com) and get an API key (https://ollama.com/settings/keys).

Copy `.env.sample` to `.env` and fill in your Ollama Cloud URL, API key, and model:

```bash
cp .env.sample .env
```

## 1. Tools

Tools are functions that you make available to an LLM. The LLM can't run them — it
can only ask your client to run them.

The tool use flow works like this: you describe each tool (name, what it does, what
inputs it needs). When the LLM decides it needs one, it sends back a request. Your
code executes the function and sends the result back. The LLM then uses that result
to answer the user.

More info in: `documentation/tools.md`

### Tool functions

Open `src/tools.py` and read through it. The file has three sections:

**Tool functions** — Python functions that query a database with agenda data.
Each function has a clear input and output:

- `get_all_talks()` — returns all talks in the agenda.
- `get_talks_by_day(day)` — returns talks for a specific day.
- `get_talk_details(title)` — returns details of a talk matching the given title.

**Tool schema** — a list of dictionaries that describe each tool to the LLM: its name,
what it does, and what parameters it expects. This is what the LLM reads to decide
which tool to call.

**Tool mapping and execution** — a dictionary that connects tool names (strings from the
LLM) to the actual Python functions, and an `execute_tool` function that looks up
the function by name, calls it, and returns the result as a string.

Run the tests to verify everything works:

```bash
python -m pytest tests/test_tools.py -v
```

## 2. The client (v1)

To invoke the tools we need an LLM client. The client is the piece that sits between
the user and the LLM, handling the back-and-forth of tool calls.

Open `src/client.py` and read through it. The client connects the LLM to the tools:

- `create_llm()` — creates a connection to an Ollama server using the configuration
  in `src/config.py`.
- `process_query(query)` — the core loop:
  1. Sends your query and the tool schemas to the LLM.
  2. If the LLM responds with a tool call → executes it → sends the result back.
  3. If the LLM responds with text → returns it (done).

Run the tests:

```bash
python -m pytest tests/test_client.py -v
```

Run the client interactively:

```bash
python -m src.client
```

Try some queries:

- "What talks are on 2026-04-20?"
- "Tell me about the Vibe Coding talk"
- "What talks are there?"

Notice how the LLM decides which tool to call based on your question — you don't
tell it which tool to use.

Type `quit` to exit.
