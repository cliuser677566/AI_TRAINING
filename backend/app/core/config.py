import os

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATABASE_PATH = os.path.join(BASE_DIR, "database", "drinkoo.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Security
SECRET_KEY = os.environ.get("DRNKOO_SECRET", "dev-secret-nonprod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
