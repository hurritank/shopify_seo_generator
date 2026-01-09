"""
SEO prompt building and content generation
"""
import openai
import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# OpenAI Config
openai.api_key = os.getenv("OPENAI_API_KEY")


def build_seo_prompt(
    product_title: str,
    product_description: str,
    brand: str,
    features: str,
    primary_keyword: str,
    product_type: str,
    trending_keywords: Dict,
) -> str:
    """Build optimized prompt cho OpenAI"""

    trending_keywords_text = ""
    if trending_keywords.get("related_searches"):
        trending_keywords_text += f"\nTrending related keywords: {', '.join(trending_keywords['related_searches'][:5])}"
    if trending_keywords.get("people_also_ask"):
        trending_keywords_text += (
            f"\nCommon questions: {', '.join(trending_keywords['people_also_ask'][:3])}"
        )

    base_prompt = f"""
Bạn là chuyên gia SEO giàu kinh nghiệm với phong cách viết tự nhiên, chuyên nghiệp. 
Hãy tạo nội dung SEO hoàn chỉnh cho sản phẩm dưới đây:

THÔNG TIN SẢN PHẨM:
- Tên: {product_title}
- Thương hiệu: {brand}
- Mô tả gốc: {product_description[:500]}...
- Tính năng: {features}

KEYWORDS:
- Từ khóa mục tiêu chính: {primary_keyword}
- Loại sản phẩm: {product_type} {trending_keywords_text}

YÊU CẦU VIẾT NỘI DUNG SEO:
"""

    if product_type == "seasonal":
        specific_requirements = """
1. Viết mô tả sản phẩm SEO (200-300 từ):
   - Nhấn mạnh tính chất MÙA VỤ của sản phẩm
   - Nhấn mạnh keyword chính + các trending keywords liên quan
   - Nhấn mạnh lợi ích, đặc điểm nổi bật
   - Tạo cảm giác NGAY BÂY GIỜ là thời điểm tốt nhất để mua

2. Meta title (< 65 ký tự): Chứa keyword chính + từ mùa vụ
3. Meta description (< 155 ký tự): Lôi cuốn, có urgency, chứa keyword
4. FAQ (3-4 câu hỏi): Trả lời nghi vấn liên quan đến mùa vụ, thời hạn
5. Alt text cho ảnh: Mô tả chi tiết, chứa keyword
"""
    else:
        specific_requirements = """
1. Viết mô tả sản phẩm SEO (200-300 từ):
   - Giải thích "Sản phẩm là gì", "Tại sao cần có nó", "Lợi ích"
   - Chèn keyword tự nhiên, không stuffing
   - Nhấn mạnh giá trị lâu dài

2. Meta title (< 65 ký tự): Công thức [Brand] + [Keyword] + [USP]
3. Meta description (< 155 ký tự): Tập trung vào giá trị, chất lượng
4. FAQ (3-4 câu hỏi): Câu hỏi phổ biến về sản phẩm
5. Alt text cho ảnh: Mô tả chi tiết
"""
        if trending_keywords.get("related_searches"):
            specific_requirements += (
                "\n- Nếu có trending keywords phù hợp, thêm vào tự nhiên"
            )

    full_prompt = (
        base_prompt
        + specific_requirements
        + """

6. Giữ giọng điệu thương hiệu
7. Định dạng output rõ ràng

OUTPUT FORMAT:
---
[META TITLE]
{Your title here}

[META DESCRIPTION]
{Your description here}

[PRODUCT DESCRIPTION]
{Your description here}

[FAQ]
Q1: ...
A1: ...

Q2: ...
A2: ...

[ALT TEXT SUGGESTIONS]
Image 1: ...
Image 2: ...
---
"""
    )
    return full_prompt


def generate_seo_content(seo_prompt: str) -> Optional[str]:
    """Gọi OpenAI GPT-4 để tạo nội dung SEO"""
    logger.info("Gọi OpenAI tạo nội dung SEO...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là chuyên gia SEO cho sản phẩm ecommerce. Viết nội dung chuyên nghiệp, tối ưu hóa từ khóa, hấp dẫn khách hàng.",
                },
                {"role": "user", "content": seo_prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        seo_content = response["choices"][0]["message"]["content"]
        logger.info("OpenAI đã tạo nội dung SEO thành công")
        return seo_content

    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        return None
