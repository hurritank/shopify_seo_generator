"""
Configuration utilities
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Centralized configuration"""

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Trending Keywords APIs
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
    APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
    USE_PYTRENDS = os.getenv("USE_PYTRENDS", "False").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "seo_generator.log"

    # Output
    OUTPUT_DIR = "./outputs"
