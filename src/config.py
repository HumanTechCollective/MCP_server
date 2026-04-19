import os

from dotenv import load_dotenv

# Load .env into OS environment
load_dotenv()

database_file = "data/sample_database.db"

# MCP Server
mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
mcp_port = int(os.getenv("MCP_PORT", "8000"))
mcp_server_url = os.getenv("MCP_SERVER_URL", f"http://{mcp_host}:{mcp_port}/mcp")

# Ollama
ollama_url = os.getenv("OLLAMA_URL", "https://ollama.com")
ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
ollama_model = os.getenv("LLM_MODEL","gemma4:31b-cloud")

system_prompt = (
    "You are a helpful assistant bot for Codemotion Madrid 2026, "
    "which takes place on the 20th and 21st of April 2026. "
    "Day 1 is 2026-04-20 and day 2 is 2026-04-21. "
    "When calling tools that take a `day` argument, always pass "
    "the date in ISO format (YYYY-MM-DD), e.g. '2026-04-20'. "
    "Only call tools that appear in your tool list. "
    "When the user asks for a list, include every matching item from "
    "the tool result. Do not filter or shorten the list. "
    "When a follow-up question refers to something already mentioned "
    "in the conversation (e.g. 'tell me more about the X one'), "
    "resolve the reference using the previous messages. If the referent is "
    "not in prior messages, call a tool to look it up instead of saying you "
    "don't know. "
    "Only use information returned by tool calls or stated earlier in this "
    "conversation. Never invent details such as room, location, description, "
    "requirements, prerequisites, or any other field. If a field is not "
    "present in the tool result, omit it or say you don't have that information."
)

# Telegram bot
telegram_token = os.getenv("TELEGRAM_TOKEN", "")
bot_greeting = "This is the bot for Codemotion Madrid 2026. You can ask me questions about the agenda."
telegram_error_message = "I'm having trouble connecting. Please try again."
# Max human/assistant pairs kept per user conversation to stop it growing unbounded
max_interactions = 3