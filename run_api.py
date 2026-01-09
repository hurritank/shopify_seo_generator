"""
Entry point để chạy API server
"""

import uvicorn
import logging

from src.api.main import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting SEO Generator API Server...")
    logger.info("📍 API docs: http://localhost:8000/docs")
    logger.info("📍 API redoc: http://localhost:8000/redoc")

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
