import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.settings import config
from src.routes.chatbot_route import router as chatbot_router
from src.routes.chatbot_stream_route import router as chatbot_stream_router
from src.repositories.Database import Database
from src.migrations.create_table import Migration
from src.migrations.seeders import Seeder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("multi-agent-coding-assistant")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Multi-Agent Coding Assistant API",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chatbot_router)
    app.include_router(chatbot_stream_router)

    @app.get("/health", tags=["Health"])
    async def health():
        return {"status": "ok", "service": "multi-agent-coding-assistant"}

    return app


def _bootstrap() -> None:
    db = Database()

    if not db.test_connection():
        logger.error("Database connection failed. Aborting startup.")
        raise SystemExit(1)

    Migration().create_tables()
    logger.info("Tables checked/created.")

    Seeder().seed_data()
    logger.info("Seeding checked/completed.")


app = create_app()
_bootstrap()


if __name__ == "__main__":
    try:
        uvicorn.run(
            "src.main:app",
            host=config.host,
            port=config.port,
            reload=False,
        )
    except Exception as exc:
        logger.error("API failed to start: %s", exc)
        raise SystemExit(1)
