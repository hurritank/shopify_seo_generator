"""
Gradio UI application - Refactored to use service layer
"""
import gradio as gr
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import csv

from ..core.models import Product
from ..core.classifiers import ProductTypeClassifier
from ..core.keyword_finder import TrendingKeywordFinder
from ..services.seo_service import SEOService
from ..services.adjust_service import AdjustService

# Load environment
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Initialize services
seo_service = SEOService()
adjust_service = AdjustService()


# ============================================================================
# CORE FUNCTIONS FOR GRADIO
# ============================================================================

def check_api_configuration():
    """Kiểm tra API configuration"""
    status = {
        "OpenAI": "✅" if OPENAI_API_KEY else "❌",
        "SERPAPI": "✅" if SERPAPI_KEY else "⚠️ (Optional)",
    }
    return status


def generate_seo_for_product(
    product_id: str,
    product_title: str,
    product_description: str,
    brand: str = "N/A",
    features: str = "",
    primary_keyword: str = "",
    tags: str = "",
    price: str = "0",
):
    """
    Generate SEO content cho sản phẩm (dữ liệu từ form) - WITH STREAMING
    Sử dụng SEOService để tránh code duplication
    """
    if not product_title or not product_description:
        yield "❌ Lỗi: Vui lòng điền đầy đủ Tên sản phẩm và Mô tả"
        return

    try:
        # Validate product_id
        try:
            pid = int(product_id) if product_id else 1
        except:
            pid = 1

        # Convert tags string to list
        tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        # Convert price
        try:
            price_val = float(price) if price else 0
        except:
            price_val = 0

        # Tạo Product object
        product = Product(
            product_id=pid,
            title=product_title,
            description=product_description,
            vendor=brand,
            price=price_val,
            tags=tags_list,
            features=features,
        )

        logger.info(f"Tạo Product object: ID={product.id}, Title={product.title}")

        # Get product type and trending keywords for display
        product_type = ProductTypeClassifier.classify_product_type(
            product.title, product.body_html
        )

        trending_keywords = {}
        if product_type in ["seasonal", "hybrid"]:
            if not primary_keyword:
                primary_keyword = product.title.lower()[:50]
            trending_keywords = TrendingKeywordFinder.get_trending_keywords(
                product.title, primary_keyword
            )
        else:
            logger.info("Sản phẩm evergreen, bỏ qua trending search")
            trending_keywords = {}

        # Format output header
        output_header = f"""
╔════════════════════════════════════════════════════════════════╗
║ ✅ SEO CONTENT GENERATED ║
╠════════════════════════════════════════════════════════════════╣

📊 PRODUCT INFORMATION:
• Product ID: {product.id}
• Title: {product.title}
• Brand: {brand}
• Price: {price_val:,.0f}
• Tags: {', '.join(tags_list) if tags_list else 'None'}
• Type: {product_type.upper()}
• Trending Keywords: {', '.join(trending_keywords.get('related_searches', [])[:3]) if trending_keywords.get('related_searches') else 'N/A'}

════════════════════════════════════════════════════════════════

FULL SEO CONTENT (Streaming in real-time):

"""
        yield output_header

        # Stream from service
        logger.info(f"Gọi SEO Service tạo SEO content (STREAMING)...")
        accumulated_output = ""
        primary_kw = primary_keyword or product.title.lower()[:50]

        for chunk in seo_service.generate_seo_streaming(product, primary_kw):
            accumulated_output += chunk
            yield output_header + accumulated_output

        # Footer
        footer = f"""
{accumulated_output}

════════════════════════════════════════════════════════════════

💾 Output saved to: outputs/seo_output_{product.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt

╚════════════════════════════════════════════════════════════════╝
"""
        yield output_header + accumulated_output + footer

        # Save to file
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/seo_output_{product.id}_{timestamp}.txt"
        full_output = output_header + accumulated_output + footer
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_output)
        logger.info(f"✅ Đã lưu vào {filename}")

    except Exception as e:
        logger.error(f"Lỗi: {e}")
        import traceback

        traceback.print_exc()
        yield f"❌ Lỗi: {str(e)}"


def adjust_seo_for_product(
    original_seo_content: str,
    adjustment_request_1: str = "",
    adjustment_request_2: str = "",
    adjustment_request_3: str = "",
    product_title: str = "",
    brand: str = "",
    price: str = "0",
):
    """
    Chỉnh sửa SEO content dựa trên yêu cầu của user - WITH STREAMING
    Sử dụng AdjustService để tránh code duplication
    """
    if not original_seo_content or not original_seo_content.strip():
        yield "❌ Lỗi: Vui lòng nhập nội dung SEO gốc"
        return

    try:
        # Collect adjustment requests
        adjustments = []
        for req in [adjustment_request_1, adjustment_request_2, adjustment_request_3]:
            if req and req.strip():
                adjustments.append(req.strip())

        if not adjustments:
            yield "❌ Lỗi: Phải có ít nhất 1 yêu cầu chỉnh sửa"
            return

        # Build product context
        product_context = {}
        if product_title:
            product_context["title"] = product_title
        if brand:
            product_context["brand"] = brand
        if price and price != "0":
            try:
                product_context["price"] = float(price)
            except:
                pass

        # Combine adjustment requests
        combined_requests = "\n".join([f"- {adj}" for adj in adjustments])

        logger.info("🔧 Chỉnh sửa SEO content (STREAMING)...")

        output_header = f"""
╔════════════════════════════════════════════════════════════════╗
║ ✅ SEO CONTENT ADJUSTED ║
╠════════════════════════════════════════════════════════════════╣

📝 ADJUSTMENT DETAILS:
Các yêu cầu được áp dụng:
{chr(10).join([f"{i + 1}. {adj}" for i, adj in enumerate(adjustments)])}

════════════════════════════════════════════════════════════════

ADJUSTED SEO CONTENT (Streaming in real-time):

"""
        yield output_header

        # Stream from service
        accumulated_output = ""
        for chunk in adjust_service.adjust_seo_content_streaming(
            original_seo_content=original_seo_content,
            user_request=combined_requests,
            product_context=product_context if product_context else None,
        ):
            accumulated_output += chunk
            yield output_header + accumulated_output

        # Footer
        footer = f"""
{accumulated_output}

════════════════════════════════════════════════════════════════

💾 Output saved at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

╚════════════════════════════════════════════════════════════════╝
"""
        yield output_header + accumulated_output + footer

        # Save to file
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/seo_adjusted_{timestamp}.txt"
        full_output = output_header + accumulated_output + footer
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_output)
        logger.info(f"✅ Đã lưu vào {filename}")

    except Exception as e:
        logger.error(f"Lỗi chỉnh sửa: {e}")
        import traceback

        traceback.print_exc()
        yield f"❌ Lỗi: {str(e)}"


def process_csv_batch(csv_file):
    """Xử lý batch từ CSV file"""
    try:
        if not csv_file:
            return "❌ Vui lòng upload file CSV"

        results = []
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            products = list(reader)
            total = len(products)

        for idx, row in enumerate(products, 1):
            product = Product(
                product_id=int(row.get("id", idx)),
                title=row.get("title", ""),
                description=row.get("description", ""),
                vendor=row.get("brand", "N/A"),
                features=row.get("features", ""),
                tags=row.get("tags", "").split(";") if row.get("tags") else [],
                price=float(row.get("price", 0)),
            )

            primary_kw = row.get("keyword", "") or product.title.lower()[:50]
            seo_content = seo_service.generate_seo(product, primary_kw)

            if seo_content:
                results.append(f"[{idx}/{total}] {row.get('title', 'Unknown')}\n✅ Processed\n")
            else:
                results.append(f"[{idx}/{total}] {row.get('title', 'Unknown')}\n❌ Failed\n")

        return f"✅ Đã xử lý {total} sản phẩm thành công!\n\n" + "\n".join(results)

    except Exception as e:
        return f"❌ Lỗi xử lý CSV: {str(e)}"


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_gradio_interface():
    """Tạo Gradio interface"""
    with gr.Blocks(
        title="Shopify SEO Generator (No Shopify API)", theme=gr.themes.Soft()
    ) as demo:
        # Header
        gr.Markdown(
            """
# 🚀 Shopify SEO Generator (No Shopify API Required)

Tự động tạo & chỉnh sửa SEO tối ưu cho sản phẩm bằng OpenAI LLM

**Không cần kết nối Shopify - Streaming real-time output! ⚡**

---
"""
        )

        # Tabs
        with gr.Tabs():
            # ===== TAB 1: DASHBOARD =====
            with gr.Tab("📊 Dashboard"):
                gr.Markdown("### System Status")

                with gr.Row():
                    status_output = gr.Textbox(
                        label="API Configuration Status", interactive=False, lines=4
                    )
                    status_btn = gr.Button("🔍 Check Status", variant="primary")

                def show_status():
                    status = check_api_configuration()
                    text = "API Status:\n"
                    for api, status_val in status.items():
                        text += f"{api}: {status_val}\n"
                    return text

                status_btn.click(show_status, outputs=status_output)

                gr.Markdown(
                    """
---

### Hướng dẫn sử dụng:

1. ✓ Kiểm tra API Configuration (OpenAI bắt buộc)
2. Chuyển sang tab "Generate SEO"
3. Nhập thông tin sản phẩm
4. Nhấn Generate
5. Xem kết quả SEO được tạo **STREAMING** ngay lập tức ⚡

### Lưu ý:

- Không cần Shopify API
- Không cần kết nối database
- Chỉ cần OpenAI API key
- Output STREAMING real-time ⚡
"""
                )

            # ===== TAB 2: GENERATE SEO (MAIN) =====
            with gr.Tab("✨ Generate SEO"):
                gr.Markdown("### Nhập thông tin sản phẩm để tạo SEO")

                with gr.Row():
                    product_id = gr.Textbox(
                        label="Product ID (tùy chọn)",
                        placeholder="Ví dụ: 123456",
                        lines=1,
                        value="1",
                    )
                    product_title = gr.Textbox(
                        label="Product Title *",
                        placeholder="Ví dụ: Áo Thun Nam Cotton Tự Nhiên",
                        lines=1,
                    )

                with gr.Row():
                    brand = gr.Textbox(
                        label="Brand",
                        placeholder="Ví dụ: FashionBrand",
                        lines=1,
                        value="N/A",
                    )
                    price = gr.Textbox(
                        label="Price (tùy chọn)",
                        placeholder="Ví dụ: 199000",
                        lines=1,
                        value="0",
                    )

                product_description = gr.Textbox(
                    label="Product Description *",
                    placeholder="Nhập mô tả chi tiết về sản phẩm...",
                    lines=5,
                )

                with gr.Row():
                    features = gr.Textbox(
                        label="Features (tùy chọn)",
                        placeholder="Ví dụ: Cotton 100%, Thoát mồ hôi nhanh",
                        lines=2,
                    )
                    tags = gr.Textbox(
                        label="Tags (tùy chọn, cách nhau bằng comma)",
                        placeholder="Ví dụ: cotton, mùa hè, áo thun",
                        lines=2,
                    )

                primary_keyword = gr.Textbox(
                    label="Primary Keyword (tùy chọn)",
                    placeholder="Ví dụ: áo thun nam cotton",
                    lines=1,
                )

                # Generate button
                generate_btn = gr.Button(
                    "🚀 Generate SEO (Streaming ⚡)", variant="primary", size="lg"
                )

                # Output
                output_text = gr.Textbox(
                    label="Generated SEO Content (Real-time Streaming)",
                    lines=20,
                    interactive=False,
                    show_copy_button=True,
                )

                generate_btn.click(
                    fn=generate_seo_for_product,
                    inputs=[
                        product_id,
                        product_title,
                        product_description,
                        brand,
                        features,
                        primary_keyword,
                        tags,
                        price,
                    ],
                    outputs=output_text,
                )

            # ===== TAB 3: ADJUST SEO =====
            with gr.Tab("🔧 Adjust SEO"):
                gr.Markdown("### Chỉnh sửa SEO content đã tạo")
                gr.Markdown(
                    "Nhập SEO content gốc và các yêu cầu chỉnh sửa, hệ thống sẽ cải thiện nó"
                )

                original_seo = gr.Textbox(
                    label="Original SEO Content *",
                    placeholder="""[META TITLE]
Tiêu đề tối ưu SEO

[META DESCRIPTION]
Mô tả ngắn gọn

[PRODUCT DESCRIPTION]
Nội dung chi tiết...""",
                    lines=8,
                )

                gr.Markdown("#### Yêu Cầu Chỉnh Sửa (Chọn ít nhất 1)")

                with gr.Row():
                    adj_req_1 = gr.Textbox(
                        label="Yêu cầu 1",
                        placeholder="Ví dụ: Rút ngắn meta title dưới 60 ký tự",
                        lines=2,
                    )
                    adj_req_2 = gr.Textbox(
                        label="Yêu cầu 2",
                        placeholder="Ví dụ: Thêm CTA mạnh hơn",
                        lines=2,
                    )
                    adj_req_3 = gr.Textbox(
                        label="Yêu cầu 3",
                        placeholder="Ví dụ: Thêm thông tin bảo hành",
                        lines=2,
                    )

                gr.Markdown("#### Thông Tin Sản Phẩm (Tùy chọn)")

                with gr.Row():
                    adj_product_title = gr.Textbox(
                        label="Product Title", placeholder="Tên sản phẩm"
                    )
                    adj_brand = gr.Textbox(label="Brand", placeholder="Thương hiệu")
                    adj_price = gr.Textbox(label="Price", placeholder="Giá")

                adjust_btn = gr.Button(
                    "🔧 Chỉnh Sửa SEO (Streaming ⚡)", variant="primary", size="lg"
                )

                adjust_output = gr.Textbox(
                    label="Adjusted SEO Content (Real-time Streaming)",
                    lines=20,
                    interactive=False,
                    show_copy_button=True,
                )

                adjust_btn.click(
                    fn=adjust_seo_for_product,
                    inputs=[
                        original_seo,
                        adj_req_1,
                        adj_req_2,
                        adj_req_3,
                        adj_product_title,
                        adj_brand,
                        adj_price,
                    ],
                    outputs=adjust_output,
                )

            # ===== TAB 4: BATCH PROCESSING =====
            with gr.Tab("⚙️ Batch Processing"):
                gr.Markdown("### Xử lý hàng loạt sản phẩm từ CSV")
                gr.Markdown(
                    """
**CSV Format (mẫu):**

```
id,title,description,brand,features,keyword,tags,price
1,Áo Thun Nam,Mô tả sản phẩm...,Brand1,Cotton 100%,áo thun,cotton;mùa hè,199000
2,Quần Short,Mô tả sản phẩm...,Brand2,Vải jean,quần,jean;mùa hè,299000
```
"""
                )

                csv_input = gr.File(
                    label="Upload CSV File", file_types=[".csv"], type="filepath"
                )
                process_btn = gr.Button("🔄 Process Batch", variant="primary")
                batch_output = gr.Textbox(
                    label="Batch Processing Result", lines=10, interactive=False
                )

                process_btn.click(
                    fn=process_csv_batch, inputs=csv_input, outputs=batch_output
                )

            # ===== TAB 5: SETTINGS =====
            with gr.Tab("⚙️ Settings"):
                gr.Markdown("### Cấu hình ứng dụng")

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**API Keys**")
                        openai_key_display = gr.Textbox(
                            label="OpenAI API Key",
                            value="✓ Configured" if OPENAI_API_KEY else "❌ Not configured",
                            interactive=False,
                        )
                        serpapi_key_display = gr.Textbox(
                            label="SERPAPI Key",
                            value="✓ Configured" if SERPAPI_KEY else "⚠️ Optional",
                            interactive=False,
                        )

                    with gr.Column():
                        gr.Markdown("**SEO Standards**")
                        gr.Textbox(
                            label="Meta Title Max Length",
                            value="65 characters",
                            interactive=False,
                        )
                        gr.Textbox(
                            label="Meta Description Max Length",
                            value="155 characters",
                            interactive=False,
                        )

                gr.Markdown(
                    """
---

### Để cấu hình API Keys:

1. Chỉnh sửa file `.env`
2. Thêm: `OPENAI_API_KEY=sk-...`
3. (Tùy chọn) Thêm: `SERPAPI_KEY=...`
4. Restart ứng dụng

**Tài liệu tham khảo:**

- [OpenAI API Docs](https://platform.openai.com/docs)
- [SERPAPI Docs](https://serpapi.com/docs)
"""
                )

        # Footer
        gr.Markdown(
            """
---

**Shopify SEO Generator v2.0** | No Shopify API Required | With Streaming Output ⚡ (Refactored)

📧 Support: Check logs | 📚 Docs: README.md
"""
        )

        return demo
