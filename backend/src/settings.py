"""
Application settings.
All values are read from environment variables (.env file in local dev,
or real environment variables when deployed to any cloud host).
"""

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


@dataclass
class Config:
    host: str
    port: int
    debug: bool

    # --- Database (SQLite by default - zero setup, file-based) ---
    database_url: str

    # --- Google Gemini Flash (primary - free tier, 1,500 req/day, no card) ---
    google_api_key: str
    google_model_id: str

    # --- Anthropic Claude (fallback 1 - free tier with claude-haiku) ---
    anthropic_api_key: str
    anthropic_model_id: str

    # --- Together AI fallback (fallback 2, free tier, 60 req/min) ---
    together_api_key: str
    together_model_id: str

    # --- Ollama local fallback (always last resort) ---
    ollama_base_url: str
    ollama_model_id: str

    # --- Code review temp file storage ---
    runs_dir: Path
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model_id: str = os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile")

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)
    @property
    def has_google(self) -> bool:
        return bool(self.google_api_key)

    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_together(self) -> bool:
        return bool(self.together_api_key)


def get_config() -> Config:
    runs_dir = Path(os.getenv("RUNS_DIR", str(BASE_DIR / "runs")))
    runs_dir.mkdir(parents=True, exist_ok=True)

    db_path = BASE_DIR / "app.db"
    default_db_url = f"sqlite:///{db_path}"
    database_url = os.getenv("DATABASE_URL", "").strip() or default_db_url

    return Config(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        debug=os.getenv("DEBUG", "false").lower() == "true",

        database_url=database_url,

        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        google_model_id=os.getenv("GOOGLE_MODEL_ID", "gemini-2.5-flash"),

        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        anthropic_model_id=os.getenv("ANTHROPIC_MODEL_ID", "claude-haiku-4-5-20251001"),

        together_api_key=os.getenv("TOGETHER_API_KEY", ""),
        together_model_id=os.getenv("TOGETHER_MODEL_ID", "meta-llama/Llama-3-8b-chat-hf"),

        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model_id=os.getenv("OLLAMA_MODEL_ID", "llama3.1"),

        runs_dir=runs_dir,
    )


config = get_config()
