"""
Product data model
"""
from typing import List, Dict


class Product:
    """Model đại diện cho sản phẩm"""

    def __init__(
        self,
        product_id: int,
        title: str,
        description: str,
        vendor: str = "N/A",
        images: List[str] = None,
        price: float = 0,
        tags: List[str] = None,
        product_type: str = "",
        options: List[Dict] = None,
        features: str = "",
    ):
        self.id = product_id
        self.title = title
        self.body_html = description  # Để tương thích với code cũ
        self.vendor = vendor
        self.images = images or []
        self.price = price
        self.tags = tags or []
        self.product_type = product_type
        self.options = options or []
        self.features = features

    def to_dict(self) -> dict:
        """Chuyển thành dict để lưu"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.body_html,
            "vendor": self.vendor,
            "images": self.images,
            "price": self.price,
            "tags": self.tags,
            "product_type": self.product_type,
            "options": self.options,
            "features": self.features,
        }

    @staticmethod
    def from_dict(data: dict) -> "Product":
        """Tạo Product từ dict"""
        return Product(
            product_id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            vendor=data.get("vendor", "N/A"),
            images=data.get("images", []),
            price=data.get("price", 0),
            tags=data.get("tags", []),
            product_type=data.get("product_type", ""),
            options=data.get("options", []),
            features=data.get("features", ""),
        )
