"""
Trending keywords finder
"""
import os
import requests
import logging
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Trending Keywords API Options
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
USE_PYTRENDS = os.getenv("USE_PYTRENDS", "False").lower() == "true"


class TrendingKeywordFinder:
    """
    Class tìm kiếm trending keywords từ Google Trends real-time
    """

    @staticmethod
    def search_trending_keywords_serpapi(keyword: str, location: str = "US") -> Dict:
        """Sử dụng SERPAPI để tìm trending keywords"""
        if not SERPAPI_KEY:
            logger.warning("SERPAPI_KEY không được cấu hình")
            return {}

        try:
            # Try different import methods for serpapi compatibility
            try:
                from serpapi.google_search import GoogleSearch
            except ImportError:
                try:
                    from serpapi import GoogleSearch
                except ImportError:
                    # Fallback: use google-search-results package
                    from serpapi.serp_api_client import GoogleSearch

            params = {
                "engine": "google",
                "q": keyword,
                "api_key": SERPAPI_KEY,
                "location": location,
                "hl": "en",
            }

            logger.info(f"Tìm kiếm trending keywords bằng SERPAPI: {keyword}")
            search = GoogleSearch(params)
            results = search.get_dict()

            trending_data = {
                "related_searches": [],
                "people_also_ask": [],
                "source": "SERPAPI",
            }

            if "related_searches" in results:
                trending_data["related_searches"] = [
                    item.get("query") for item in results["related_searches"][:5]
                ]

            if "people_also_ask" in results:
                trending_data["people_also_ask"] = [
                    item.get("question") for item in results["people_also_ask"][:3]
                ]

            logger.info(
                f"Tìm thấy {len(trending_data['related_searches'])} related searches"
            )
            return trending_data

        except Exception as e:
            logger.error(f"SERPAPI Error: {e}")
            return {}

    @staticmethod
    def search_trending_keywords_apify(keyword: str) -> Dict:
        """Sử dụng Apify Google Trends API"""
        if not APIFY_TOKEN:
            logger.warning("APIFY_TOKEN không được cấu hình")
            return {}

        try:
            url = "https://api.apify.com/v2/acts/emastra~google-trends-scraper/run-sync-get-dataset-items"
            headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
            body = {"searchTerms": [keyword], "timeRange": "now 1-m", "maxItems": 10}

            logger.info(f"Tìm kiếm trending keywords bằng Apify: {keyword}")
            response = requests.post(url, json=body, headers=headers, timeout=30)

            if response.status_code == 200:
                logger.info("Apify API thành công")
                return response.json()
            else:
                logger.error(f"Apify API error: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"Apify Error: {e}")
            return {}

    @staticmethod
    def search_trending_keywords_pytrends(keyword: str) -> Dict:
        """Sử dụng Pytrends (miễn phí, không cần API key)"""
        try:
            from pytrends.request import TrendReq

            logger.info(f"Tìm kiếm trending keywords bằng Pytrends: {keyword}")
            pytrends = TrendReq(hl="en-US", tz=360)
            pytrends.build_payload([keyword], timeframe="today 1-m")

            related_topics = pytrends.related_topics()
            related_queries = pytrends.related_queries()

            logger.info("Pytrends API thành công")
            return {
                "related_topics": related_topics,
                "related_queries": related_queries,
                "source": "PYTRENDS",
            }

        except Exception as e:
            logger.error(f"Pytrends Error: {e}")
            return {}

    @staticmethod
    def get_trending_keywords(product_title: str, primary_keyword: str) -> Dict:
        """Tìm kiếm trending keywords từ multiple sources"""
        logger.info(f"Bắt đầu tìm kiếm trending keywords cho: {primary_keyword}")

        trending_data = {}

        if SERPAPI_KEY:
            logger.info("Ưu tiên sử dụng SERPAPI")
            trending_data = TrendingKeywordFinder.search_trending_keywords_serpapi(
                primary_keyword
            )

        elif APIFY_TOKEN:
            logger.info("Sử dụng Apify Google Trends")
            trending_data = TrendingKeywordFinder.search_trending_keywords_apify(
                primary_keyword
            )

        elif USE_PYTRENDS:
            logger.info("Sử dụng Pytrends")
            trending_data = TrendingKeywordFinder.search_trending_keywords_pytrends(
                primary_keyword
            )

        else:
            logger.warning(
                "Không có API key nào được cấu hình, sử dụng evergreen keywords"
            )
            trending_data = {"related_searches": [], "people_also_ask": []}

        return trending_data
