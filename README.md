# API Test Guide

Project này dùng endpoint tương thích Anthropic:

- Base URL: `https://claude.zunef.com/v1/ai`
- Models: `https://claude.zunef.com/v1/ai/models`
- Messages: `https://claude.zunef.com/v1/ai/messages`

Auth hiện tại dùng `x-api-key`.

## 1. Cấu hình `.env`

Ví dụ:

```env
ANTHROPIC_AUTH_TOKEN=your_api_key
ANTHROPIC_BASE_URL=https://claude.zunef.com/v1/ai
ANTHROPIC_MODEL=claude-sonnet-4.5
MAX_TOKENS=1024
TEST_PROMPT=Hello, please reply with a short API test message.
```

Ý nghĩa các biến:

- `ANTHROPIC_AUTH_TOKEN`: API key
- `ANTHROPIC_BASE_URL`: base URL của API
- `ANTHROPIC_MODEL`: model dùng để gọi `messages`
- `MAX_TOKENS`: số token output tối đa
- `TEST_PROMPT`: prompt test

## 2. Các file example

Ba file example là ba file độc lập, không dùng helper chung. Mỗi file tự xử lý:

- load `.env`
- đọc config
- tạo request
- gọi `curl.exe`
- in kết quả

Danh sách file:

- [model_list_example.py](/d:/Python/azure/model_list_example.py): gọi `GET /models` và in response
- [invoke_example.py](/d:/Python/azure/invoke_example.py): gọi `POST /messages` một lần với `stream: false`, payload có `thinking`, và in ra raw response gốc
- [invoke_stream_example.py](/d:/Python/azure/invoke_stream_example.py): gọi `POST /messages` một lần với `stream: true` và in text stream ra terminal
- [test.py](/d:/Python/azure/test.py): chạy lần lượt 3 file trên trong cùng một process Python

## 3. Cách chạy

Chạy từng file:

```powershell
python .\model_list_example.py
python .\invoke_example.py
python .\invoke_stream_example.py
```

Chạy tổng hợp:

```powershell
python .\test.py
```

## 4. Kết quả mong đợi

- `model_list_example.py`: in JSON model list nếu server trả JSON; nếu không, file sẽ in raw response
- `invoke_example.py`: in `=== REQUEST JSON ===` và sau đó in `=== RESPONSE ===` với response gốc từ API
- `invoke_stream_example.py`: in request JSON trước, sau đó in text stream khi server đẩy dữ liệu

## 5. Lưu ý

- Các file đang gọi API qua `curl.exe`.
- `invoke_example.py` không parse response nữa; mục tiêu là để nhìn trực tiếp raw response, bao gồm cả phần `thinking` nếu API trả về.
- `invoke_stream_example.py` đang đọc SSE và in ra text delta trong stream.
- Nếu bạn muốn test riêng model list, hãy chạy `model_list_example.py` trước.
