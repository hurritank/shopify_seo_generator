"""
Pydantic models for API
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ProductInput(BaseModel):
    """Model nhận dữ liệu sản phẩm từ client"""

    product_id: int
    title: str
    description: str
    brand: str = "N/A"
    features: str = ""
    tags: Optional[List[str]] = None
    price: float = 0
    images: Optional[List[str]] = None
    primary_keyword: Optional[str] = None


class SEOOutput(BaseModel):
    """Model trả về SEO content"""

    product_id: int
    product_title: str
    product_type: str  # seasonal/evergreen/hybrid
    trending_keywords: List[str]
    seo_content: str
    meta_title: str
    meta_description: str
    generated_at: str


class ErrorResponse(BaseModel):
    """Model trả về lỗi"""

    error: str
    details: Optional[str] = None


class AdjustSEORequest(BaseModel):
    """Model cho request Adjust SEO"""

    product_id: int
    original_seo_content: str
    adjustment_requests: List[str]
    user_notes: Optional[str] = None
    product_context: Optional[Dict[str, Any]] = None


class AdjustedSEOResponse(BaseModel):
    """Model cho response Adjust SEO"""

    product_id: int
    original_seo_content: str
    adjusted_seo_content: str
    adjustment_requests: List[str]
    product_context: Optional[Dict[str, Any]] = None
    model: str
    adjusted_at: str
