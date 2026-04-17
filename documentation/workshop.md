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
> [models with tool support](https://ollama.com/search?c=tools). To use a different
> model, pull it with `ollama pull <model>` and update the model name in
> [src/config.py](src/config.py).


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

Open `src/tools_client.py` and read through it. The client connects the LLM to the tools:

- `create_llm()` — creates a connection to an Ollama server using the configuration
  in `src/config.py`.
- `process_query(query)` — the core loop:
  1. Sends your query and the tool schemas to the LLM.
  2. If the LLM responds with a tool call → executes it → sends the result back.
  3. If the LLM responds with text → returns it (done).

Run the tests:

```bash
python -m pytest tests/test_tools_client.py -v
```

Run the client interactively:

```bash
python -m src.tools_client
```

Try some queries:

- "What talks are on 2026-04-20?"
- "Tell me about the Vibe Coding talk"
- "What talks are there?"

Notice how the LLM decides which tool to call based on your question — you don't
tell it which tool to use.

Type `quit` to exit.


## 3. MCP server

To share our tools with any Model Context Protocol (MCP) compatible app, we wrap them in an MCP server.

Open [src/MCP_server.py](../src/MCP_server.py). It is mostly a copy of
[src/tools.py](../src/tools.py) with a few small changes:

**1. Create the server**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agenda")
```

`FastMCP` is the high-level server class from the MCP SDK. The name (`"agenda"`)
identifies this server to clients.

**2. Register each tool with a decorator**

```python
@mcp.tool()
def get_all_talks() -> list[dict]:
    """Return all talks in the agenda."""
    ...
```

The `@mcp.tool()` decorator registers the function as an MCP tool. 
FastMCP generates the tool schema automatically — so the manual `tools_schema` 
list and `tool_mapping` dictionary from `src/tools.py` are no longer needed.

**3. Run the server**

MCP supports two main transports: **stdio** (simpler, local only) and **HTTP**
(for remote servers). We'll show both.

### 3.1 stdio transport

```python
if __name__ == "__main__":
    mcp.run(transport='stdio')
```

`stdio` means the server talks to its client over standard input/output. The
client launches the server as a subprocess and exchanges MCP messages through
its pipes. This is the simplest transport.

Start the server:

```bash
python -m src.MCP_server
```

It will sit waiting for an MCP client to connect. Press `Ctrl+C` to stop.

#### Optional: connect it to Claude Code

If you use Claude Code, you can let it call these tools directly. Create
`.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "agenda": {
      "command": "${HOME}/MCP_server/.venv/bin/python",
      "args": ["-m", "src.MCP_server"],
      "cwd": "${HOME}/MCP_server"
    }
  }
}
```

Adjust the paths to match where you cloned the repo. Restart Claude Code and ask
it about the agenda — it will launch the server and call the MCP tools to
answer.

### 3.2 HTTP transport

Change the transport:

```python
if __name__ == "__main__":
    mcp.run(transport='streamable-http')
```

With `streamable-http`, the server runs as a standalone web process listening
on `http://127.0.0.1:8000/mcp`, and clients connect over HTTP. This is what
enables *remote* MCP servers (hosted elsewhere, shared across clients).

> **Note:** The host and port are defined in [src/config.py](../src/config.py)
> as `mcp_host` and `mcp_port`, and the full URL is exposed as `mcp_server_url`.
> Change them there if you need a different host or port.

Start the server:

```bash
python -m src.MCP_server
```

> **Note:** Visiting `http://127.0.0.1:8000/mcp` in a browser will return a
> `406 Not Acceptable` error. That is expected — the endpoint requires MCP
> headers (`Accept: application/json, text/event-stream`) that browsers don't
> send. The 406 means the server is running correctly.

#### Optional: connect it to Claude Code

Update `.mcp.json`:

```json
{
  "mcpServers": {
    "agenda": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Make sure the server is running before Claude Code connects.


## 4. The client (v2): MCP client

In section 2 we built a client that imported `tools_schema` and `tool_mapping` from `src/tools.py`.

Now that the tools are in an MCP server, we can write a client that **discovers
the tools at runtime**. It asks the server "what tools do you have?", gets back
the schemas, and hands them to the LLM. The client no longer needs to know
anything about the agenda — it only knows how to speak MCP.

Open [src/mcp_client.py](../src/mcp_client.py). Compared to the v1 client, there are four key differences:

- **Connecting to the server.** `streamable_http_client` + `ClientSession` open
  a connection to the MCP server running on `http://127.0.0.1:8000/mcp`.
- **Discovering tools.** `session.list_tools()` asks the server for its tools
  instead of importing them from a Python module.
- **Adapting the schema.** `mcp_tool_to_schema()` converts each MCP tool
  definition into the dict format that `bind_tools` expects.
- **Calling tools.** `session.call_tool(name, args)` runs the tool on the
  server over MCP — the client never imports or executes the Python function
  itself.

### Run it

You need **two terminals**: one for the server, one for the client.

In the first terminal, start the MCP server with HTTP (from section 3.2):

```bash
python -m src.MCP_server
```

In the second terminal, start the client:

```bash
python -m src.mcp_client
```
