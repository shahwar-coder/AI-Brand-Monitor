from dotenv import load_dotenv
import os

load_dotenv()

class LLMConfig:
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral:7b")

class DatabaseConfig:
    DB_PATH=os.getenv("DB_PATH", "data/brand_monitor.db")

class APIConfig:
    HN_API_BASE = os.getenv(
        "HN_API_BASE",
        "https://hacker-news.firebaseio.com/v0"
    )