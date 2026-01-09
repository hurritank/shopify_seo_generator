"""
SEO adjustment service
"""
import logging
from typing import Optional, Dict, Any, Iterator
from datetime import datetime

from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


def build_adjust_seo_prompt(
    original_seo_content: str,
    user_request: str,
    product_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Tạo prompt cho LLM để chỉnh sửa lại bài SEO theo yêu cầu người dùng
    """
    context_text = ""
    if product_context:
        ctx_lines = []
        for k, v in product_context.items():
            if v is None:
                continue
            ctx_lines.append(f"- {k}: {v}")
        if ctx_lines:
            context_text = "Thông tin thêm về sản phẩm:\n" + "\n".join(ctx_lines)

    prompt = f"""
Bạn là một chuyên gia **SEO content** cho sản phẩm trên Shopify / sàn thương mại điện tử.
Nhiệm vụ của bạn là **CHỈNH SỬA** lại bài SEO đã có, dựa trên yêu cầu chỉnh sửa của người dùng, 
nhưng vẫn phải đảm bảo:
- Giữ nguyên fact quan trọng về sản phẩm (tên, đặc tính, lợi ích chính).
- Giữ hoặc cải thiện chất lượng SEO (từ khóa, khả năng đọc, CTA).
- Cấu trúc rõ ràng, dễ copy-paste vào Shopify: Meta Title, Meta Description, Product Description, Bullet Points (nếu cần), FAQ (nếu có).
- Ngôn ngữ: tiếng Việt, tự nhiên, thuyết phục, phù hợp thương mại.

[YÊU CẦU CHỈNH SỬA CỦA USER]
{user_request}

[BÀI SEO GỐC]
{original_seo_content}

{context_text}

[HƯỚNG DẪN ĐỊNH DẠNG OUTPUT]
Hãy trả kết quả theo đúng cấu trúc sau (giữ nguyên các label):

[META TITLE]
...

[META DESCRIPTION]
...

[PRODUCT DESCRIPTION]
...

[BULLET POINTS]
- ...

[FAQ]
Q1: ...
A1: ...
Q2: ...
A2: ...

Nếu phần nào không có nội dung phù hợp thì để trống phần đó nhưng vẫn giữ label.
"""
    return prompt.strip()


class AdjustService:
    """Service để adjust SEO content"""

    def __init__(self, openai_service: OpenAIService = None):
        self.openai = openai_service or OpenAIService()

    def adjust_seo_content(
        self,
        original_seo_content: str,
        user_request: str,
        product_context: Optional[Dict[str, Any]] = None,
        model: str = "gpt-4o",
    ) -> Dict[str, Any]:
        """
        Adjust SEO content (non-streaming)
        
        Returns:
            Dict với adjusted_seo_content và metadata
        """
        if not original_seo_content or not original_seo_content.strip():
            raise ValueError("original_seo_content không được để trống")

        if not user_request or not user_request.strip():
            raise ValueError("user_request không được để trống")

        prompt = build_adjust_seo_prompt(
            original_seo_content=original_seo_content,
            user_request=user_request,
            product_context=product_context,
        )

        system_message = (
            "Bạn là chuyên gia SEO cho sản phẩm thương mại điện tử. "
            "Bạn luôn viết nội dung rõ ràng, dễ đọc, chuẩn SEO, "
            "và bám sát yêu cầu chỉnh sửa của người dùng."
        )

        adjusted = self.openai.generate(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=0.5,
        )

        return {
            "original_seo_content": original_seo_content,
            "user_request": user_request,
            "product_context": product_context or {},
            "adjusted_seo_content": adjusted or "",
            "model": model,
            "adjusted_at": datetime.utcnow().isoformat(),
        }

    def adjust_seo_content_streaming(
        self,
        original_seo_content: str,
        user_request: str,
        product_context: Optional[Dict[str, Any]] = None,
        model: str = "gpt-4o-mini",
    ) -> Iterator[str]:
        """
        Adjust SEO content với streaming
        
        Yields:
            Chunks of adjusted SEO content
        """
        if not original_seo_content or not original_seo_content.strip():
            yield "❌ Lỗi: original_seo_content không được để trống"
            return

        if not user_request or not user_request.strip():
            yield "❌ Lỗi: user_request không được để trống"
            return

        try:
            prompt = build_adjust_seo_prompt(
                original_seo_content=original_seo_content,
                user_request=user_request,
                product_context=product_context,
            )

            system_message = (
                "Bạn là chuyên gia SEO cho sản phẩm thương mại điện tử. "
                "Bạn luôn viết nội dung rõ ràng, dễ đọc, chuẩn SEO, "
                "và bám sát yêu cầu chỉnh sửa của người dùng."
            )

            for chunk in self.openai.generate_streaming(
                prompt=prompt,
                system_message=system_message,
                model=model,
                temperature=0.5,
                max_tokens=2500,
            ):
                yield chunk

        except Exception as e:
            logger.error(f"Error adjusting SEO streaming: {e}")
            yield f"❌ Lỗi: {str(e)}"
