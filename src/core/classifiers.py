"""
Product type classification logic
"""
import logging

logger = logging.getLogger(__name__)


class ProductTypeClassifier:
    """Phân loại sản phẩm theo kiểu evergreen hay seasonal/trending"""

    SEASONAL_KEYWORDS = [
        "mùa hè",
        "mùa đông",
        "mùa xuân",
        "mùa thu",
        "summer",
        "winter",
        "spring",
        "fall",
        "black friday",
        "giáng sinh",
        "tết",
        "christmas",
        "new year",
        "valentine",
        "lễ",
        "holiday",
        "trend",
        "trending",
        "viral",
        "mới",
        "2025",
        "2024",
    ]

    EVERGREEN_KEYWORDS = [
        "best",
        "how to",
        "guide",
        "tips",
        "basics",
        "essential",
        "tốt nhất",
        "cách",
        "hướng dẫn",
        "mẹo",
        "căn bản",
    ]

    @staticmethod
    def classify_product_type(product_title: str, product_description: str) -> str:
        """Phân loại sản phẩm"""
        combined_text = (product_title + " " + product_description).lower()

        seasonal_count = sum(
            1 for kw in ProductTypeClassifier.SEASONAL_KEYWORDS if kw in combined_text
        )
        evergreen_count = sum(
            1 for kw in ProductTypeClassifier.EVERGREEN_KEYWORDS if kw in combined_text
        )

        if seasonal_count > evergreen_count and seasonal_count > 0:
            product_type = "seasonal"
        elif evergreen_count >= seasonal_count and evergreen_count > 0:
            product_type = "evergreen"
        else:
            product_type = "hybrid"

        logger.info(f"Phân loại sản phẩm: {product_type}")
        return product_type
