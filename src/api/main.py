"""
FastAPI application main file
"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .routers import seo, adjust, utils

# Load .env
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("api_server.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SEO Generator API",
    description="API để tự động tạo SEO content cho sản phẩm",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(seo.router)
app.include_router(adjust.router)
app.include_router(utils.router)

logger.info("✅ FastAPI App initialized")


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Kiểm tra xem API server có hoạt động không
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    return {
        "status": "ok",
        "message": "SEO Generator API is running",
        "openai_configured": bool(openai_key),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint - Thông tin về API"""
    return {
        "name": "SEO Generator API",
        "version": "2.0.0",
        "description": "Tự động tạo SEO content cho sản phẩm bằng OpenAI LLM",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "generate_seo": "POST /seo/v1/generate",
            "generate_seo_stream": "POST /seo/v1/generate-stream",
            "generate_seo_batch": "POST /seo/v1/generate-batch",
            "classify": "POST /seo/v1/classify-product",
            "trending_keywords": "GET /seo/v1/trending-keywords",
            "adjust_seo": "POST /seo/v1/adjust-seo",
            "adjust_seo_stream": "POST /seo/v1/adjust-seo-stream",
        },
    }
