# 🚀 SEO Generator - Tự động tạo nội dung SEO cho sản phẩm

Ứng dụng tự động tạo nội dung SEO cho sản phẩm bằng OpenAI LLM, tích hợp tìm kiếm trending keywords real-time.

## ⚡ Quick Start

### 1. Cài đặt
```bash
# Setup tự động
bash setup.sh        # Linux/macOS
setup.bat           # Windows

# Hoặc thủ công
pip install -r requirements.txt
```

### 2. Cấu hình
Tạo file `.env`:
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx
SERPAPI_KEY=xxxxxxx              # Optional
APIFY_TOKEN=xxxxxxx              # Optional
USE_PYTRENDS=True                # Optional (Free)
```

### 3. Chạy ứng dụng
```bash
# Gradio UI (Khuyến nghị)
python run_gradio.py
# → http://localhost:7860

# API Server
python run_api.py
# → http://localhost:8000/docs
```

## 📋 Tính năng

- ✅ Phân loại sản phẩm tự động (Seasonal/Evergreen)
- ✅ Tìm kiếm Trending Keywords Real-time
- ✅ Tạo nội dung SEO chuẩn (Meta Title, Description, FAQ, Alt Text)
- ✅ Batch Processing
- ✅ Streaming Responses (Real-time feedback)
- ✅ API & UI (FastAPI + Gradio)

## 📚 Tài liệu đầy đủ

👉 **Xem [DOCUMENTATION.md](DOCUMENTATION.md) để biết chi tiết:**
- Cài đặt & Setup chi tiết
- Cấu trúc Project
- API Documentation (Tất cả endpoints)
- Streaming Responses
- Troubleshooting
- Refactoring & Migration
- Tips & Best Practices

## 🔑 API Keys

| API | Chi phí | Setup |
|-----|---------|-------|
| **OpenAI** | $0.03-0.06 / 1K tokens | [Setup](https://platform.openai.com) |
| **SERPAPI** | 100 queries/tháng free | [Setup](https://serpapi.com) |
| **Apify** | Free tier | [Setup](https://apify.com) |
| **Pytrends** | Free | Không cần setup |

## 📁 Cấu trúc Project

```
seo_generator/
├── src/                    # Source code
│   ├── core/              # Business logic
│   ├── services/          # Service layer
│   ├── api/               # API endpoints
│   ├── ui/                # Gradio UI
│   └── utils/             # Utilities
│
├── run_api.py            # Chạy API server
├── run_gradio.py         # Chạy Gradio UI
│
├── requirements.txt
├── .env
└── DOCUMENTATION.md      # Tài liệu đầy đủ
```

## 🐛 Troubleshooting

### Lỗi thường gặp:
- **"Module not found"** → Chạy `pip install -r requirements.txt`
- **"OPENAI_API_KEY not found"** → Kiểm tra file `.env`
- **"SERPAPI Error"** → Xem [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting)

👉 **Xem chi tiết trong [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting)**

## 📞 Support

Nếu gặp vấn đề:
1. Xem [DOCUMENTATION.md](DOCUMENTATION.md)
2. Kiểm tra log file: `seo_generator.log` hoặc `api_server.log`
3. Tạo issue trên GitHub (nếu có)

## 📄 License

MIT License - Tự do sử dụng & modify

---

**Version:** 2.0.0  
**Last Updated:** 2025-01-08  
**Status:** ✅ Production Ready

**Lưu ý:** Hãy kiểm tra SEO content trước khi publish trên store để đảm bảo chất lượng!
