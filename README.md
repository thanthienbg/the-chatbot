# Hướng dẫn cài đặt và sử dụng Chatbot

## Yêu cầu hệ thống
- Python 3.8+ 
- PIP

## Cài đặt
1. Clone repository:
```
git clone [địa-chỉ-repository]
```
2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```
3. Tạo file .env với API key OpenAI:
```
OPENAI_API_KEY=sk-của-bạn-ở-đây
```

## Sử dụng
Khởi động server:
```bash
uvicorn app.main:app --reload
```

Gửi câu hỏi qua API endpoint `/ask`:
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "Câu hỏi của bạn"}
)
print(response.json())
```

Gửi câu hỏi qua API endpoint `/ask_without_ai`:
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "Câu hỏi của bạn"}
)
print(response.json())
```

## Cấu trúc thư mục
- `/app`: Mã nguồn chính
- `/data`: Chứa dữ liệu CSV
- `.env`: Cấu hình môi trường

## Contributing
Pull requests được chào đón!