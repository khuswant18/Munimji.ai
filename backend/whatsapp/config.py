import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "my_verify_token")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v16.0")
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/munimji")

# Paths
DOWNLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)