"""
SEO generation endpoints
"""
import os
import json
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ...core.models import Product
from ...core.classifiers import ProductTypeClassifier
from ...core.keyword_finder import TrendingKeywordFinder
from ...core.seo_generator import build_seo_prompt
from ...services.seo_service import SEOService
from ..models import ProductInput, SEOOutput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/seo/v1", tags=["SEO Generation"])

# Initialize service
seo_service = SEOService()


def extract_section(text: str, start_marker: str, end_marker: str) -> str:
    """Extract một phần của text giữa 2 markers"""
    try:
        start_idx = text.find(start_marker)
        if start_idx == -1:
            return ""

        start_idx += len(start_marker)
        end_idx = text.find(end_marker, start_idx)

        if end_idx == -1:
            end_idx = len(text)

        return text[start_idx:end_idx].strip()

    except Exception as e:
        logger.error(f"Error extracting section: {e}")
        return ""


@router.post("/generate", response_model=SEOOutput)
async def generate_seo(product: ProductInput):
    """
    Generate SEO content cho sản phẩm (non-streaming)
    """
    try:
        logger.info(
            f"🔍 Nhận request generate SEO cho product ID: {product.product_id}"
        )

        # Validate
        if not product.title or not product.description:
            raise HTTPException(
                status_code=400, detail="title và description không được trống"
            )

        # Create Product object
        prod = Product(
            product_id=product.product_id,
            title=product.title,
            description=product.description,
            vendor=product.brand,
            price=product.price,
            tags=product.tags or [],
            features=product.features,
            images=product.images or [],
        )

        # Generate SEO using service
        primary_kw = product.primary_keyword or prod.title.lower()[:50]
        seo_content = seo_service.generate_seo(prod, primary_kw)

        if not seo_content:
            raise HTTPException(
                status_code=500, detail="Không thể tạo nội dung từ OpenAI"
            )

        # Parse output
        meta_title = extract_section(seo_content, "[META TITLE]", "[META DESCRIPTION]")
        meta_description = extract_section(
            seo_content, "[META DESCRIPTION]", "[PRODUCT DESCRIPTION]"
        )

        # Get product type and trending keywords for response
        product_type = ProductTypeClassifier.classify_product_type(
            prod.title, prod.body_html
        )
        trending_keywords = []
        if product_type in ["seasonal", "hybrid"]:
            trending_keywords_data = TrendingKeywordFinder.get_trending_keywords(
                prod.title, primary_kw
            )
            trending_keywords = trending_keywords_data.get("related_searches", [])

        logger.info("✅ Generate SEO thành công")
        return SEOOutput(
            product_id=product.product_id,
            product_title=product.title,
            product_type=product_type,
            trending_keywords=trending_keywords,
            seo_content=seo_content,
            meta_title=meta_title.strip(),
            meta_description=meta_description.strip(),
            generated_at=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-stream")
async def generate_seo_stream(product: ProductInput):
    """
    Generate SEO content với STREAMING response (Server-Sent Events)
    """
    try:
        logger.info(
            f"🔍 Nhận STREAMING request generate SEO cho product ID: {product.product_id}"
        )

        # Validate
        if not product.title or not product.description:
            raise HTTPException(
                status_code=400, detail="title và description không được trống"
            )

        # Create Product object
        prod = Product(
            product_id=product.product_id,
            title=product.title,
            description=product.description,
            vendor=product.brand,
            price=product.price,
            tags=product.tags or [],
            features=product.features,
            images=product.images or [],
        )

        # Get product type and trending keywords
        product_type = ProductTypeClassifier.classify_product_type(
            prod.title, prod.body_html
        )
        trending_keywords = []
        if product_type in ["seasonal", "hybrid"]:
            primary_kw = product.primary_keyword or prod.title.lower()[:50]
            trending_keywords_data = TrendingKeywordFinder.get_trending_keywords(
                prod.title, primary_kw
            )
            trending_keywords = trending_keywords_data.get("related_searches", [])

        # Streaming generator function
        async def generate_stream():
            # Send initial metadata
            metadata = {
                "status": "started",
                "product_id": product.product_id,
                "product_title": product.title,
                "product_type": product_type,
                "trending_keywords": trending_keywords,
            }
            yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"

            # Stream header
            header = f"""
╔════════════════════════════════════════════════════════════════╗
║ ✅ SEO CONTENT GENERATING (STREAMING) ║
╠════════════════════════════════════════════════════════════════╣

📊 PRODUCT INFORMATION:
• Product ID: {product.product_id}
• Title: {product.title}
• Brand: {product.brand}
• Type: {product_type.upper()}
• Trending Keywords: {", ".join(trending_keywords[:3]) if trending_keywords else "N/A"}

════════════════════════════════════════════════════════════════

FULL SEO CONTENT (Streaming in real-time):

"""
            yield header

            # Stream from service
            primary_kw = product.primary_keyword or prod.title.lower()[:50]
            accumulated_output = ""
            for chunk in seo_service.generate_seo_streaming(prod, primary_kw):
                accumulated_output += chunk
                yield chunk

            # Send footer
            footer = f"""

════════════════════════════════════════════════════════════════

💾 Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

╚════════════════════════════════════════════════════════════════╝
"""
            yield footer

            # Send final metadata
            final_metadata = {
                "status": "completed",
                "generated_at": datetime.now().isoformat(),
                "content_length": len(accumulated_output),
            }
            yield f"\ndata: {json.dumps(final_metadata, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Lỗi streaming: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-batch")
async def generate_seo_batch(products: List[ProductInput]):
    """
    Generate SEO content cho nhiều sản phẩm cùng lúc
    """
    logger.info(f"📦 Nhận batch request cho {len(products)} sản phẩm")

    results = []
    errors = []

    for idx, product in enumerate(products, 1):
        try:
            logger.info(f"[{idx}/{len(products)}] Xử lý {product.product_id}...")

            result = await generate_seo(product)
            results.append(result)

        except Exception as e:
            logger.error(f"Lỗi khi xử lý product {product.product_id}: {str(e)}")
            errors.append({"product_id": product.product_id, "error": str(e)})

    logger.info(f"✅ Hoàn tất batch: {len(results)} thành công, {len(errors)} lỗi")

    return {
        "total": len(products),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
