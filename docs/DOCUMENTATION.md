# 📚 SEO Generator - Tài liệu Tổng hợp

> Tài liệu tổng hợp tất cả thông tin về project SEO Generator - Tự động tạo nội dung SEO cho sản phẩm bằng OpenAI LLM

---

## 📋 Mục lục

1. [Giới thiệu](#giới-thiệu)
2. [Cài đặt & Setup](#cài-đặt--setup)
3. [Cấu trúc Project](#cấu-trúc-project)
4. [Cách sử dụng](#cách-sử-dụng)
5. [API Documentation](#api-documentation)
6. [Streaming Responses](#streaming-responses)
7. [Troubleshooting](#troubleshooting)
8. [Refactoring & Migration](#refactoring--migration)
9. [Cleanup Summary](#cleanup-summary)

---

## 🎯 Giới thiệu

### Tổng quan

SEO Generator là ứng dụng tự động tạo nội dung SEO cho sản phẩm bằng OpenAI LLM, tích hợp tìm kiếm trending keywords real-time.

### Tính năng chính

- ✅ **Phân loại sản phẩm tự động** - Seasonal, Evergreen, Hybrid
- ✅ **Tìm kiếm Trending Keywords Real-time** - Hỗ trợ SERPAPI, Apify, Pytrends
- ✅ **Tạo nội dung SEO chuẩn** - Meta Title, Meta Description, Product Description, FAQ, Alt Text
- ✅ **Batch Processing** - Xử lý nhiều sản phẩm cùng lúc
- ✅ **Streaming Responses** - Real-time feedback khi generate SEO
- ✅ **API & UI** - FastAPI server và Gradio web interface

---

## 🚀 Cài đặt & Setup

### Bước 1: Cài đặt Dependencies

```bash
# Tạo virtual environment
python3 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt
```

Hoặc dùng setup script tự động:

```bash
# Linux/macOS
bash setup.sh

# Windows
setup.bat
```

### Bước 2: Cấu hình API Keys

Tạo file `.env` trong root directory:

```bash
# Bắt buộc
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx

# Tùy chọn - Trending Keywords (chọn ít nhất 1)
SERPAPI_KEY=xxxxxxx              # Recommended (100 queries/tháng free)
APIFY_TOKEN=xxxxxxx              # Fallback 1
USE_PYTRENDS=True                # Fallback 2 (Free, không cần API key)
```

### Bước 3: Chạy ứng dụng

#### Option 1: Gradio UI (Khuyến nghị)
```bash
python run_gradio.py
```
→ Mở http://localhost:7860

#### Option 2: API Server
```bash
python run_api.py
```
→ API docs: http://localhost:8000/docs

---

## 📁 Cấu trúc Project

### Cấu trúc hiện tại (Sau refactoring)

```
seo_generator/
│
├── src/                    # Source code chính
│   ├── core/               # Core business logic
│   │   ├── models.py      # Product model
│   │   ├── classifiers.py # ProductTypeClassifier
│   │   ├── keyword_finder.py # TrendingKeywordFinder
│   │   └── seo_generator.py # SEO prompt & generation
│   │
│   ├── services/          # Service layer (tránh duplicate)
│   │   ├── openai_service.py # OpenAI API wrapper
│   │   ├── seo_service.py    # SEO generation service
│   │   └── adjust_service.py # SEO adjustment service
│   │
│   ├── api/               # API layer
│   │   ├── main.py        # FastAPI app
│   │   ├── models.py      # Pydantic models
│   │   └── routers/
│   │       ├── seo.py     # SEO endpoints
│   │       ├── adjust.py   # Adjust endpoints
│   │       └── utils.py   # Utility endpoints
│   │
│   ├── ui/                # UI layer
│   │   └── gradio_app.py  # Gradio interface
│   │
│   └── utils/             # Utilities
│       └── config.py      # Configuration
│
├── run_api.py             # Entry point cho API server
├── run_gradio.py          # Entry point cho Gradio UI
│
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── .gitignore             # Git ignore rules
│
├── outputs/               # Output files
├── tests/                 # Tests (sẽ thêm sau)
└── docs/                  # Documentation
```

### So sánh Trước/Sau Refactoring

| Aspect | Trước | Sau |
|--------|-------|-----|
| **main.py size** | 599 dòng | Tách thành 4 modules |
| **Code duplication** | Có (streaming logic) | Không (service layer) |
| **API Endpoints** | Tất cả trong 1 file | Tách thành routers |
| **Testability** | Khó | Dễ |
| **Maintainability** | Trung bình | Tốt |

---

## 🎯 Cách sử dụng

### 1. Sử dụng Gradio UI

```bash
python run_gradio.py
```

**Tính năng:**
- Generate SEO cho sản phẩm
- Adjust SEO content
- Batch processing
- Streaming responses (real-time)

### 2. Sử dụng API

```bash
python run_api.py
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Ví dụ sử dụng

#### Generate SEO cho 1 sản phẩm

**Input:**
```json
{
    "product_id": 1,
    "title": "Áo Thun Nam Cotton Mùa Hè",
    "description": "Áo thun nam chất lượng cao với vải cotton 100% tự nhiên...",
    "brand": "FashionBrand",
    "features": "Cotton 100%, Thoát mồ hôi nhanh",
    "tags": ["cotton", "mùa hè", "áo thun"],
    "price": 199000
}
```

**Output:**
```
[META TITLE]
Áo Thun Nam Cotton Mùa Hè - Thoát Mồ Hôi Nhanh

[META DESCRIPTION]
Áo thun nam cotton 100%, thoát mồ hôi nhanh, mát mẻ...

[PRODUCT DESCRIPTION]
Hè đến rồi, đó là lúc bạn cần một chiếc áo thun nam cotton...

[FAQ]
Q: Áo có thoát mồ hôi không?
A: Có, áo được làm từ cotton 100%...
```

---

## 📡 API Documentation

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "ok",
    "message": "SEO Generator API is running",
    "openai_configured": true,
    "timestamp": "2025-01-08T12:00:00.000000"
}
```

#### 2. Generate SEO (Non-Streaming)
```http
POST /seo/v1/generate
Content-Type: application/json
```

**Request Body:**
```json
{
    "product_id": 1,
    "title": "Áo Thun Nam Cotton Mùa Hè",
    "description": "Áo thun nam chất lượng cao...",
    "brand": "FashionBrand",
    "features": "Cotton 100%",
    "tags": ["cotton", "mùa hè"],
    "price": 199000,
    "images": ["image1.jpg"],
    "primary_keyword": "áo thun nam cotton"
}
```

**Response:**
```json
{
    "product_id": 1,
    "product_title": "Áo Thun Nam Cotton Mùa Hè",
    "product_type": "seasonal",
    "trending_keywords": ["áo thun nam", "áo cotton mùa hè"],
    "seo_content": "[META TITLE]\n...",
    "meta_title": "Áo Thun Nam Cotton Mùa Hè - Thoát Mồ Hôi Nhanh",
    "meta_description": "Áo thun nam cotton 100%...",
    "generated_at": "2025-01-08T12:00:00.000000"
}
```

#### 3. Generate SEO (Streaming) ⚡
```http
POST /seo/v1/generate-stream
Content-Type: application/json
```

**Request Body:** (Giống như endpoint Generate SEO)

**Response Headers:**
```
Content-Type: text/event-stream
Transfer-Encoding: chunked
```

**Response Body:** Text xuất hiện từng phần real-time

#### 4. Adjust SEO (Non-Streaming)
```http
POST /seo/v1/adjust-seo
Content-Type: application/json
```

**Request Body:**
```json
{
    "product_id": 1,
    "original_seo_content": "[META TITLE]\n...",
    "adjustment_requests": [
        "Rút ngắn meta title dưới 60 ký tự",
        "Thêm CTA mạnh hơn"
    ],
    "user_notes": "Khách hàng muốn thấy rõ hơn các lợi ích",
    "product_context": {
        "title": "Áo Thun Nam Cotton",
        "brand": "FashionBrand",
        "price": 199000
    }
}
```

#### 5. Adjust SEO (Streaming) ⚡
```http
POST /seo/v1/adjust-seo-stream
Content-Type: application/json
```

**Request Body:** (Giống như endpoint Adjust SEO)

**Response:** Streaming text real-time

#### 6. Generate SEO Batch
```http
POST /seo/v1/generate-batch
Content-Type: application/json
```

**Request Body:** Array of products
```json
[
    {
        "product_id": 1,
        "title": "Áo Thun Nam Cotton",
        ...
    },
    {
        "product_id": 2,
        "title": "Quần Short Nam",
        ...
    }
]
```

#### 7. Classify Product
```http
POST /seo/v1/classify-product?title=Áo Thun Nam&description=...
```

**Response:**
```json
{
    "product_type": "seasonal",
    "title": "Áo Thun Nam"
}
```

#### 8. Get Trending Keywords
```http
GET /seo/v1/trending-keywords?keyword=áo thun nam
```

**Response:**
```json
{
    "keyword": "áo thun nam",
    "related_searches": ["áo thun nam cotton", "áo thun nam giá rẻ"],
    "people_also_ask": ["Áo thun nam nào tốt?"]
}
```

---

## ⚡ Streaming Responses

### Cách nhận biết Streaming

#### ✅ Dấu hiệu Streaming hoạt động:

1. **Response Headers:**
   ```
   Content-Type: text/event-stream
   Transfer-Encoding: chunked
   ```

2. **Response Body:**
   - Text xuất hiện từng phần một
   - Có thể thấy text đang được viết từng chữ
   - Không cần đợi hết mới thấy

3. **Response Time:**
   - Response time tăng dần
   - Size tăng dần theo thời gian

#### ❌ Dấu hiệu KHÔNG có Streaming:

1. **Response Headers:**
   ```
   Content-Type: application/json
   Content-Length: 1234
   ```

2. **Response Body:**
   - Phải đợi vài giây
   - Sau đó mới thấy toàn bộ JSON cùng lúc

### Test Streaming với cURL

```bash
# Test streaming endpoint
curl -N -X POST http://localhost:8000/seo/v1/generate-stream \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "title": "Test Product",
    "description": "Test description",
    "brand": "TestBrand"
  }'
```

**Lưu ý:** Flag `-N` (--no-buffer) rất quan trọng để xem streaming real-time!

### Test Streaming với Postman

1. Gửi request đến endpoint streaming
2. Xem tab **Headers** trong Response
3. Tìm `Content-Type: text/event-stream`
4. Scroll xuống **Response Body** để xem text đang được stream

---

## 🐛 Troubleshooting

### ❌ "Module not found: openai"
```bash
# Kiểm tra venv có activate không
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows

# Cài lại dependencies
pip install -r requirements.txt
```

### ❌ "OPENAI_API_KEY not found"
```bash
# Kiểm tra .env file
cat .env  # Linux/macOS
type .env # Windows

# Đảm bảo format đúng: OPENAI_API_KEY=sk-xxxxx (không có quotes)
```

### ❌ "OpenAI API error: 401 Unauthorized"
- API key sai hoặc expired
- Tạo API key mới từ https://platform.openai.com
- Update `.env` và thử lại

### ❌ "SERPAPI Error: cannot import name 'GoogleSearch'"
**Giải pháp:**
```bash
# Gỡ package cũ
pip uninstall serpapi -y

# Cài package đúng
pip install google-search-results>=2.4.2
```

**Đã fix trong code:** Code đã có fallback import để tương thích với nhiều version.

### ❌ "SERPAPI rate limit exceeded"
- Vượt 100 queries/tháng (free tier)
- **Giải pháp:**
  1. Nâng cấp plan SERPAPI, hoặc
  2. Dùng Apify thay thế, hoặc
  3. Dùng Pytrends (miễn phí)

### ❌ "Connection refused" (API)
- API server chưa chạy
- **Giải pháp:** Chạy `python run_api.py` trước

### ❌ "422 Unprocessable Entity"
- Body JSON không đúng format
- **Giải pháp:** Kiểm tra lại JSON body, đảm bảo đúng cấu trúc

### ❌ "500 Internal Server Error"
- Lỗi từ OpenAI API hoặc thiếu API key
- **Giải pháp:**
  - Kiểm tra file `.env` có `OPENAI_API_KEY`
  - Kiểm tra log file `api_server.log`

---

## 🔄 Refactoring & Migration

### Cấu trúc mới

Project đã được tái cấu trúc hoàn toàn với cấu trúc mới trong folder `src/`.

### Thay đổi Imports

#### Trước (Old):
```python
from main import Product, TrendingKeywordFinder, ProductTypeClassifier
from adjust_seo_generator import adjust_seo_content
```

#### Sau (New):
```python
# Option 1: Import từ __init__.py (Recommended)
from src.core import Product, TrendingKeywordFinder, ProductTypeClassifier

# Option 2: Import trực tiếp từ modules
from src.core.models import Product
from src.core.keyword_finder import TrendingKeywordFinder
from src.core.classifiers import ProductTypeClassifier

# Services
from src.services.seo_service import SEOService
from src.services.adjust_service import AdjustService
```

### Sử dụng Service Layer

#### Trước (Old):
```python
# Duplicate code trong nhiều files
response = openai.ChatCompletion.create(...)
for chunk in response:
    yield chunk.content
```

#### Sau (New):
```python
from src.services.openai_service import OpenAIService

openai_service = OpenAIService()

# Non-streaming
content = openai_service.generate(prompt)

# Streaming
for chunk in openai_service.generate_streaming(prompt):
    yield chunk
```

### Entry Points mới

**Trước đây:**
- `python app_gradio.py` → **Bây giờ:** `python run_gradio.py`
- `python api_server.py` → **Bây giờ:** `python run_api.py`

### Lợi ích của Cấu trúc Mới

1. ✅ **Separation of Concerns** - Mỗi module có trách nhiệm rõ ràng
2. ✅ **Code Reusability** - Service layer dùng chung cho API và UI
3. ✅ **Testability** - Dễ test từng module riêng
4. ✅ **Scalability** - Dễ thêm features mới
5. ✅ **Maintainability** - Code organized, dễ tìm và sửa

---

## 🗑️ Cleanup Summary

### Files đã xóa (9 files)

#### 1. Files không được sử dụng:
- ✅ `config.py` - Không được import ở đâu
- ✅ `utils.py` - Không được import ở đâu  
- ✅ `prompts.py` - Chỉ có 1 dòng, không dùng

#### 2. Files cũ đã được refactor:
- ✅ `app_gradio.py` - Đã refactor thành `src/ui/gradio_app.py`
- ✅ `api_server.py` - Đã refactor thành `src/api/main.py`
- ✅ `adjust_endpoint.py` - Đã merge vào `src/api/routers/adjust.py`
- ✅ `adjust_seo_generator.py` - Đã merge vào `src/services/adjust_service.py`
- ✅ `main.py` - Đã refactor, không còn cần thiết (đã xóa)

#### 3. Files đã fix:
- ✅ `gitignore` - Đã xóa (có `.gitignore` mới đúng tên)

### Cấu trúc hiện tại

```
seo_generator/
│
├── src/                    # Cấu trúc mới ⭐
│   ├── core/
│   ├── services/
│   ├── api/
│   ├── ui/
│   └── utils/
│
├── run_api.py             # Entry point API
├── run_gradio.py          # Entry point Gradio
│
├── requirements.txt
├── .env
├── .gitignore
│
└── docs/                  # Documentation files
```

---

## 📚 Tài liệu tham khảo

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### External APIs
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [SERPAPI Docs](https://serpapi.com/docs)
- [Apify Docs](https://docs.apify.com)
- [Pytrends GitHub](https://github.com/GeneralMills/pytrends)

### Testing Tools
- **Postman Collection:** `postman_collection.json`
- **cURL Commands:** Xem file `CURL_COMMANDS.md` (đã được tổng hợp trong tài liệu này)

---

## 💡 Tips & Best Practices

### 1. Testing trước khi batch
```python
# Thử 1 sản phẩm trước
optimize_product_seo(123456789)

# Kiểm tra output file
# Rồi chạy batch nếu OK
optimize_products_batch(product_ids)
```

### 2. Giữ logs lâu dài
```bash
# Archive log cũ
mv seo_generator.log seo_generator_$(date +%Y%m%d).log

# Tiếp tục ghi log mới
python run_gradio.py
```

### 3. Backup outputs
```bash
# Backup thư mục outputs
cp -r outputs outputs_backup_$(date +%Y%m%d)

# Hoặc zip
zip -r outputs_backup_$(date +%Y%m%d).zip outputs/
```

### 4. Sử dụng Postman Variables
- Tạo variable `base_url` = `http://localhost:8000`
- Dùng `{{base_url}}/seo/v1/generate` trong URL

### 5. Monitor Performance
```bash
# Xem log realtime
tail -f seo_generator.log

# Đếm số lần gọi API
grep "openai" seo_generator.log | wc -l

# Xem lỗi
grep "ERROR" seo_generator.log
```

---

## 📊 Chi phí & Giới hạn

| API | Per Request | Giới hạn Free | Chi phí/tháng (1000 requests) |
|-----|------------|---------------|------|
| **OpenAI (GPT-4)** | $0.05 | N/A | ~$50 |
| **Shopify** | $29-299/tháng | Unlimited API | Fixed |
| **SERPAPI** | $0.002 | 100/tháng | $0 (nếu < 100) |
| **Apify** | Free tier | Có sẵn | $0 |
| **Pytrends** | Free | N/A | $0 |

---

## ✅ Checklist trước khi deploy

- [ ] Tất cả API keys được cấu hình đúng
- [ ] Thử chạy thành công cho 1 sản phẩm
- [ ] Output files được tạo đúng
- [ ] Log file được ghi đúng
- [ ] Batch processing hoạt động (nếu cần)
- [ ] Error handling test
- [ ] README & documentation cập nhật
- [ ] .gitignore bao gồm .env & logs/
- [ ] requirements.txt updated
- [ ] Test streaming endpoints
- [ ] Test non-streaming endpoints

---

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra log file: `seo_generator.log` hoặc `api_server.log`
2. Xem troubleshooting section trên
3. Kiểm tra API status pages
4. Tạo issue trên GitHub (nếu có)

---

## 📄 License

MIT License - Tự do sử dụng & modify

---

**Version:** 2.0.0  
**Last Updated:** 2025-01-08  
**Status:** ✅ Production Ready

---

**Lưu ý:** Hãy kiểm tra SEO content trước khi publish trên store để đảm bảo chất lượng!
