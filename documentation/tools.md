# Tools

## What is tool use?

Large Language Models (LLMs) can only generate text. They can't search databases,
call APIs, or read files. Tool use is the mechanism that bridges that gap:

1. You define tools — tell the LLM what functions are available.
2. The LLM decides — it responds requesting a tool call (it never executes code).
3. Your code executes — the client runs the actual function.
4. You send the result back — the client sends the tool result to the LLM.
5. The LLM responds — now it has real data and can write a natural language answer.

The key insight: the LLM never runs code. It only *requests* that a tool be called.
The client is always in control.

## History

- OpenAI popularized it first as "function calling" (June 2023, GPT-3.5 and GPT-4).
  Later renamed to "tool use".
- Anthropic added tool use to the Claude API (beta November 2023, generally available
  May 2024).
- Google (Gemini), Mistral, Cohere, and others followed with similar features.

## What's the same across providers

- Both use JSON Schema to describe tool parameters.
- Both support `strict: true` to enforce schema conformance.
- Both follow the same loop: define tools → model requests a call → you execute →
  send result back.
- Both support `tool_choice` to control when the model uses tools.

## Key differences between OpenAI and Anthropic

| Aspect                   | OpenAI                                                        | Anthropic (Claude)                                                 |
|--------------------------|---------------------------------------------------------------|--------------------------------------------------------------------|
| Tool definition wrapper  | `{"type": "function", "name": ..., "parameters": ...}`       | `{"name": ..., "input_schema": ...}` (uses `input_schema`)        |
| Tool call in response    | `function.name` + `function.arguments` (JSON string)         | `tool_use` content block with `name` + `input` (parsed object)    |
| Result message role      | `role: "tool"` with `tool_call_id`                            | `role: "user"` with a `tool_result` content block and `tool_use_id`|
| Arguments format         | JSON-encoded **string**                                       | Already a parsed JSON **object**                                   |
| Server-side tools        | Not a concept                                                 | Built-in server tools (web_search, code_execution) that run on Anthropic's infrastructure |

## Why this matters

There is no cross-provider standard for tool use. The JSON Schema for describing
parameters is similar, but the message format, tool call structure, and result
format all differ.

This is one of the motivations behind Model Context Protocol (MCP) — tool use lets
an LLM call functions, but every provider does it differently. MCP standardizes the
layer *above* that: how tools are discovered, described, and served, regardless of
which LLM is on the other side.

## Sources

- [OpenAI function calling announcement (June 2023)](https://openai.com/index/function-calling-and-other-api-updates/)
- [Anthropic tool use GA announcement (May 2024)](https://anthropic.com/news/tool-use-ga)
- [OpenAI function calling docs](https://developers.openai.com/api/docs/guides/function-calling)
- [Claude platform tool use docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
