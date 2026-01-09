"""
SEO generation service
"""
import logging
from typing import Dict, Optional
from datetime import datetime
import os

from ..core.models import Product
from ..core.classifiers import ProductTypeClassifier
from ..core.keyword_finder import TrendingKeywordFinder
from ..core.seo_generator import build_seo_prompt
from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


class SEOService:
    """Service để generate SEO content"""

    def __init__(self, openai_service: OpenAIService = None):
        self.openai = openai_service or OpenAIService()

    def generate_seo(
        self,
        product: Product,
        primary_keyword: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate SEO content cho sản phẩm
        
        Args:
            product: Product object
            primary_keyword: Primary keyword (optional)
            
        Returns:
            SEO content string or None if error
        """
        try:
            # 1. Prepare data
            product_title = product.title
            product_description = product.body_html or ""
            brand = product.vendor or "N/A"
            features = product.features or ", ".join(product.tags) if product.tags else ""
            primary_keyword = primary_keyword or product_title.lower()[:50]

            # 2. Classify product type
            product_type = ProductTypeClassifier.classify_product_type(
                product_title, product_description
            )

            # 3. Find trending keywords
            trending_keywords = {}
            if product_type in ["seasonal", "hybrid"]:
                trending_keywords = TrendingKeywordFinder.get_trending_keywords(
                    product_title, primary_keyword
                )
            else:
                logger.info("Sản phẩm evergreen, bỏ qua trending search")

            # 4. Build prompt
            seo_prompt = build_seo_prompt(
                product_title,
                product_description,
                brand,
                features,
                primary_keyword,
                product_type,
                trending_keywords,
            )

            # 5. Call OpenAI
            seo_content = self.openai.generate(seo_prompt)

            return seo_content

        except Exception as e:
            logger.error(f"Error generating SEO: {e}")
            return None

    def generate_seo_streaming(
        self,
        product: Product,
        primary_keyword: Optional[str] = None,
    ):
        """
        Generate SEO content với streaming
        
        Yields:
            Chunks of SEO content
        """
        try:
            # 1. Prepare data
            product_title = product.title
            product_description = product.body_html or ""
            brand = product.vendor or "N/A"
            features = product.features or ", ".join(product.tags) if product.tags else ""
            primary_keyword = primary_keyword or product_title.lower()[:50]

            # 2. Classify product type
            product_type = ProductTypeClassifier.classify_product_type(
                product_title, product_description
            )

            # 3. Find trending keywords
            trending_keywords = {}
            if product_type in ["seasonal", "hybrid"]:
                trending_keywords = TrendingKeywordFinder.get_trending_keywords(
                    product_title, primary_keyword
                )
            else:
                logger.info("Sản phẩm evergreen, bỏ qua trending search")

            # 4. Build prompt
            seo_prompt = build_seo_prompt(
                product_title,
                product_description,
                brand,
                features,
                primary_keyword,
                product_type,
                trending_keywords,
            )

            # 5. Stream from OpenAI
            for chunk in self.openai.generate_streaming(seo_prompt):
                yield chunk

        except Exception as e:
            logger.error(f"Error generating SEO streaming: {e}")
            yield f"❌ Lỗi: {str(e)}"
