import os

from dotenv import load_dotenv

# Load .env into OS environment
load_dotenv()

database_file = "data/sample_database.db"
ollama_url = os.getenv("OLLAMA_URL", "https://ollama.com")
ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
ollama_model = "gemma4:31b-cloud"

system_prompt = (
    "You are a helpful assistant bot for Codemotion Madrid 2026, "
    "which takes place on the 20th and 21st of April 2026."
)