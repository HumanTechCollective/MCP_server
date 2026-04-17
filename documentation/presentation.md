# Workshop presentation

> This document is a guide to build the slide deck that supports the
> workshop. Each `###` heading below corresponds to one slide, and the
> bullets under it are the content to show on that slide.
>
> The presentation is complementary to [workshop.md](workshop.md): it focuses
> on the concepts — what tools and the Model Context Protocol (MCP) are, why
> they exist, and what they add. The hands-on instructions (setup, code to
> write, commands to run) live in [workshop.md](workshop.md).

### Title slide

- Workshop name: "Building an MCP server with Python"

### Index

- Tools
- Model Context Protocol (MCP)
- References

## Tools

### Section separator

- Title: "Tools"

### What are tools?

- Tools are functions that you make available to an LLM. The LLM can't run them — it
  can only ask your code to run them. You describe each tool (name, what it does, what
  inputs it needs), and when the LLM decides it needs one, it sends back a request
  saying "call this function with these arguments". Your code executes the function
  and sends the result back to the LLM.

### How does tool use work?

- LLMs can only generate text. They can't search databases, call APIs, or read files.
- Tool use is the mechanism that bridges that gap:
  1. You define tools — tell the LLM what functions are available.
  2. The LLM decides — it responds requesting a tool call (it never executes code).
  3. Your code executes — the client runs the actual function.
  4. You send the result back — the client sends the tool result to the LLM.
  5. The LLM responds — now it has real data and can write a natural language answer.
- Diagram idea: show the back-and-forth between User, Client, and LLM with a tool
  call in the middle.

### History of tool use

- OpenAI popularized it first as "function calling". Later renamed to "tool use".
    "These models have been fine-tuned to both detect when a function needs to be called (depending on the user’s input) and to respond with JSON that adheres to the function signature.[..] allow developers to describe functions to the model via JSON Schema" [1]
- Anthropic added tool use to the Claude API (May 2024). [2]
- Google (Gemini), Mistral, Cohere, and others followed with similar features.

### No standard for tool use

- There is no cross-provider standard for tool use. Each Large Language Model (LLM)
  provider has its own API format for defining tools and handling tool calls.
- The JSON schema for describing parameters is similar across providers (they all use
  JSON Schema), but the message format, the way tool results are sent back, and the
  details all differ.
- This is one of the motivations behind MCP — tool use lets an LLM call functions,
  but every provider does it differently. MCP standardizes the layer *above* that.

## Model Context Protocol (MCP)

### Section separator

- Title: "Model Context Protocol (MCP)"

### What is MCP?

- Model Context Protocol (MCP) is an open protocol that standardizes how
  applications provide tools and context to Large Language Models (LLMs).
- Announced by Anthropic in November 2024 [3] and later adopted by other vendors.
- Think of it as a common language between *tool providers* and *LLM clients*.

### Why was MCP created?

- Recap from the previous section: every LLM provider has its own tool-use
  format, and every app that wants to expose tools to an LLM has to
  re-implement the plumbing for each one.
- MCP separates *who provides the tools* from *which LLM consumes them*.
- Tool authors write their integration once; LLM clients implement the
  protocol once; everything else connects through the standard.

### The N×M problem

- Without a standard: N apps that want to expose tools × M LLM clients that
  want to consume them = N×M custom integrations.
- With MCP: N servers + M clients. Each side only needs to speak the protocol.
- Diagram idea: on the left, a tangle of N-to-M arrows between apps and
  clients. On the right, both sides connect through a single MCP box in the
  middle.

### What MCP adds over raw tool use

- **Reusability.** One MCP server works with any MCP-compatible client
  (Claude Desktop, Claude Code, IDE extensions, etc.).
- **Decoupling.** The tool author doesn't need to know which LLM will end up
  using the tools.
- **More than tools.** MCP also standardizes *resources* (read-only data the
  LLM can fetch) and *prompts* (reusable prompt templates) — not just
  function calls.
- **Transport flexibility.** The same protocol runs over stdio (local
  subprocess) or HTTP (remote server).

### MCP server vs MCP client

- **Server** — exposes tools, resources, and prompts. This is what we build
  in the hands-on part: `src/MCP_server.py`.
- **Client** — connects to one or more servers, discovers what they expose,
  and hands that to the LLM. Examples: Claude Code, Claude Desktop, IDE
  integrations.
- In a later step we'll modify the client we already built (the one that
  calls tools directly) to instead receive its tools from the MCP server.

## References

### Documentation and resources

- [1] [OpenAI function calling announcement (June 2023)](https://openai.com/index/function-calling-and-other-api-updates/)
- [2] [Anthropic tool use GA announcement (May 2024)](https://anthropic.com/news/tool-use-ga)
- [3] [Anthropic MCP announcement (November 2024)](https://www.anthropic.com/news/model-context-protocol)
- [OpenAI function calling docs](https://developers.openai.com/api/docs/guides/function-calling)
- [Anthropic tool use course (GitHub)](https://github.com/anthropics/courses/tree/master/tool_use)
- [Claude platform tool use docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [MCP Python SDK (GitHub)](https://github.com/modelcontextprotocol/python-sdk)
- [MCP official docs](https://modelcontextprotocol.io/docs/sdk)
- [DeepLearning.ai course: Build Rich-Context AI Apps with Anthropic](https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic/lesson/dbabg/creating-an-mcp-server)