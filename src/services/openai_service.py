"""
OpenAI API service - Centralized OpenAI calls
"""
import os
import openai
import logging
from typing import Optional, Iterator
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class OpenAIService:
    """Service để gọi OpenAI API - Tránh code duplication"""

    @staticmethod
    def generate(
        prompt: str,
        system_message: str = "Bạn là chuyên gia SEO cho sản phẩm ecommerce. Viết nội dung chuyên nghiệp, tối ưu hóa từ khóa, hấp dẫn khách hàng.",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> Optional[str]:
        """
        Generate content từ OpenAI (non-streaming)
        
        Args:
            prompt: User prompt
            system_message: System message
            model: Model name (default: gpt-4-turbo for non-streaming, gpt-4o-mini for streaming)
            temperature: Temperature
            max_tokens: Max tokens
            
        Returns:
            Generated content or None if error
        """
        model = model or "gpt-4-turbo"
        logger.info(f"Gọi OpenAI generate (non-streaming) với model: {model}")

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response["choices"][0]["message"]["content"]
            logger.info("OpenAI generate thành công")
            return content

        except Exception as e:
            logger.error(f"OpenAI Error: {e}")
            return None

    @staticmethod
    def generate_streaming(
        prompt: str,
        system_message: str = "Bạn là chuyên gia SEO cho sản phẩm ecommerce. Viết nội dung chuyên nghiệp, tối ưu hóa từ khóa, hấp dẫn khách hàng.",
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Iterator[str]:
        """
        Generate content từ OpenAI với streaming
        
        Args:
            prompt: User prompt
            system_message: System message
            model: Model name (default: gpt-4o-mini)
            temperature: Temperature
            max_tokens: Max tokens
            
        Yields:
            Chunks of content as they arrive
        """
        model = model or DEFAULT_MODEL
        logger.info(f"Gọi OpenAI generate (streaming) với model: {model}")

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            for chunk in response:
                try:
                    if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta and hasattr(delta, "content") and delta.content:
                            yield delta.content
                except (AttributeError, IndexError, KeyError) as e:
                    logger.warning(f"Chunk parsing warning: {e}")
                    continue

        except Exception as e:
            logger.error(f"OpenAI Streaming Error: {e}")
            yield f"❌ Lỗi: {str(e)}"
