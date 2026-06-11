import os

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "drinkoo.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Security
SECRET_KEY = os.environ.get("DRNKOO_SECRET", "dev-secret-nonprod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Chatbot/OpenRouter
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemma-2-9b-it")

# Chatbot SQL debug (admin-only)
CHATBOT_SQL_DEBUG_ENABLED = os.environ.get("CHATBOT_SQL_DEBUG_ENABLED", "0") == "1"
CHATBOT_SQL_DEBUG_TOKEN = os.environ.get("CHATBOT_SQL_DEBUG_TOKEN", "")
