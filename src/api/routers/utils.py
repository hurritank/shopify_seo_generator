"""
Utility endpoints
"""
import logging
from fastapi import APIRouter, HTTPException

from ...core.classifiers import ProductTypeClassifier
from ...core.keyword_finder import TrendingKeywordFinder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/seo/v1", tags=["Utilities"])


@router.post("/classify-product")
async def classify_product(title: str, description: str):
    """
    Phân loại sản phẩm (seasonal/evergreen/hybrid)
    """
    try:
        product_type = ProductTypeClassifier.classify_product_type(title, description)
        return {
            "product_type": product_type,
            "title": title[:50] + "..." if len(title) > 50 else title,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending-keywords")
async def get_trending_keywords(keyword: str):
    """
    Tìm trending keywords cho một keyword
    """
    try:
        logger.info(f"Tìm trending keywords cho: {keyword}")
        result = TrendingKeywordFinder.get_trending_keywords(keyword, keyword)

        return {
            "keyword": keyword,
            "related_searches": result.get("related_searches", []),
            "people_also_ask": result.get("people_also_ask", []),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
