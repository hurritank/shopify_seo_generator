"""
SEO adjustment endpoints
"""
import os
import json
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ...services.adjust_service import AdjustService
from ..models import AdjustSEORequest, AdjustedSEOResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/seo/v1", tags=["SEO Adjustment"])

# Initialize service
adjust_service = AdjustService()


@router.post("/adjust-seo", response_model=AdjustedSEOResponse)
async def adjust_seo(request: AdjustSEORequest):
    """
    🔧 Chỉnh sửa nội dung SEO đã tạo dựa trên yêu cầu của người dùng (non-streaming)
    """
    try:
        # Validate input
        if not request.original_seo_content or not request.original_seo_content.strip():
            raise HTTPException(
                status_code=400, detail="original_seo_content không được để trống"
            )

        if not request.adjustment_requests or len(request.adjustment_requests) == 0:
            raise HTTPException(
                status_code=400,
                detail="adjustment_requests không được để trống, phải có ít nhất 1 yêu cầu chỉnh sửa",
            )

        # Combine adjustment requests
        combined_requests = "\n".join([f"- {req}" for req in request.adjustment_requests])

        if request.user_notes:
            combined_requests += f"\n\nGhi chú thêm: {request.user_notes}"

        logger.info(f"📝 Bắt đầu chỉnh sửa SEO cho product_id={request.product_id}")

        # Use service
        result = adjust_service.adjust_seo_content(
            original_seo_content=request.original_seo_content,
            user_request=combined_requests,
            product_context=request.product_context,
        )

        logger.info(f"✅ Hoàn tất chỉnh sửa SEO cho product_id={request.product_id}")

        return AdjustedSEOResponse(
            product_id=request.product_id,
            original_seo_content=request.original_seo_content,
            adjusted_seo_content=result["adjusted_seo_content"],
            adjustment_requests=request.adjustment_requests,
            product_context=request.product_context,
            model=result["model"],
            adjusted_at=result["adjusted_at"],
        )

    except ValueError as ve:
        logger.error(f"❌ ValueError: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        logger.error(f"❌ Error adjusting SEO: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi chỉnh sửa SEO: {str(e)}")


@router.post("/adjust-seo-stream")
async def adjust_seo_stream(request: AdjustSEORequest):
    """
    🔧 Chỉnh sửa SEO content với STREAMING response (Server-Sent Events)
    """
    try:
        # Validate input
        if not request.original_seo_content or not request.original_seo_content.strip():
            raise HTTPException(
                status_code=400, detail="original_seo_content không được để trống"
            )

        if not request.adjustment_requests or len(request.adjustment_requests) == 0:
            raise HTTPException(
                status_code=400,
                detail="adjustment_requests không được để trống, phải có ít nhất 1 yêu cầu chỉnh sửa",
            )

        # Combine adjustment requests
        combined_requests = "\n".join([f"- {req}" for req in request.adjustment_requests])

        if request.user_notes:
            combined_requests += f"\n\nGhi chú thêm: {request.user_notes}"

        logger.info(
            f"📝 Bắt đầu STREAMING chỉnh sửa SEO cho product_id={request.product_id}"
        )

        # Streaming generator function
        async def generate_stream():
            # Send initial metadata
            metadata = {
                "status": "started",
                "product_id": request.product_id,
                "adjustment_requests": request.adjustment_requests,
                "adjustment_count": len(request.adjustment_requests),
            }
            yield f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"

            # Stream header
            header = f"""
╔════════════════════════════════════════════════════════════════╗
║ ✅ SEO CONTENT ADJUSTING (STREAMING) ║
╠════════════════════════════════════════════════════════════════╣

📝 ADJUSTMENT DETAILS:
• Product ID: {request.product_id}
• Số yêu cầu chỉnh sửa: {len(request.adjustment_requests)}
• Các yêu cầu:
{chr(10).join([f"  {i + 1}. {req}" for i, req in enumerate(request.adjustment_requests)])}

"""
            if request.product_context:
                header += "📊 PRODUCT CONTEXT:\n"
                for k, v in request.product_context.items():
                    if v is not None:
                        header += f"• {k}: {v}\n"

            header += """
════════════════════════════════════════════════════════════════

ADJUSTED SEO CONTENT (Streaming in real-time):

"""
            yield header

            # Stream from service
            accumulated_output = ""
            for chunk in adjust_service.adjust_seo_content_streaming(
                original_seo_content=request.original_seo_content,
                user_request=combined_requests,
                product_context=request.product_context,
            ):
                accumulated_output += chunk
                yield chunk

            # Send footer
            footer = f"""

════════════════════════════════════════════════════════════════

💾 Adjusted at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

╚════════════════════════════════════════════════════════════════╝
"""
            yield footer

            # Send final metadata
            final_metadata = {
                "status": "completed",
                "adjusted_at": datetime.now().isoformat(),
                "content_length": len(accumulated_output),
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
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
        logger.error(f"❌ Lỗi streaming adjust SEO: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi khi chỉnh sửa SEO: {str(e)}")
