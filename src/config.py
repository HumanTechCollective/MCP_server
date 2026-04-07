import os

from dotenv import load_dotenv

# Load .env into OS environment
load_dotenv()

database_file = "data/sample_database.db"
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:26b")
