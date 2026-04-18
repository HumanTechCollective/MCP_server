import os

from dotenv import load_dotenv

# Load .env into OS environment
load_dotenv()

database_file = "data/sample_database.db"
mcp_host = "127.0.0.1"
mcp_port = 8000
mcp_server_url = f"http://{mcp_host}:{mcp_port}/mcp"
ollama_url = os.getenv("OLLAMA_URL", "https://ollama.com")
ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
ollama_model = "gemma4:31b-cloud"

system_prompt = (
    "You are a helpful assistant bot for Codemotion Madrid 2026, "
    "which takes place on the 20th and 21st of April 2026. "
    "Day 1 is 2026-04-20 and day 2 is 2026-04-21. "
    "When calling tools that take a `day` argument, always pass "
    "the date in ISO format (YYYY-MM-DD), e.g. '2026-04-20'."
)

telegram_token = os.getenv("TELEGRAM_TOKEN", "")
bot_greeting = "This is the bot for Codemotion Madrid 2026. You can ask me questions about the agenda."
telegram_error_message = "I'm having trouble connecting. Please try again."