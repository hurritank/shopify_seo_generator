"""
Production entry point để chạy API server
Sử dụng cho production deployment (không có auto-reload)
"""
import uvicorn
import logging
import os

from src.api.main import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Production settings
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 4))  # Số worker processes
    
    logger.info("🚀 Starting SEO Generator API Server (Production Mode)...")
    logger.info(f"📍 Host: {host}")
    logger.info(f"📍 Port: {port}")
    logger.info(f"📍 Workers: {workers}")
    logger.info("📍 API docs: http://localhost:8000/docs")
    logger.info("📍 API redoc: http://localhost:8000/redoc")

    # Production: không có reload, có workers
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        workers=workers,  # Multiple workers cho production
        reload=False,     # Không reload trong production
        log_level="info",
        access_log=True,  # Log access requests
    )
