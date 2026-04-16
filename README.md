# API Test Guide

Project nay dung endpoint Anthropic-compatible:

- Base URL: `https://claude.zunef.com/v1/ai`
- Models: `https://claude.zunef.com/v1/ai/models`
- Messages: `https://claude.zunef.com/v1/ai/messages`

Auth hien tai dung `x-api-key`.

## 1. Cau hinh `.env`

Vi du:

```env
ANTHROPIC_AUTH_TOKEN=your_api_key
ANTHROPIC_BASE_URL=https://claude.zunef.com/v1/ai
ANTHROPIC_MODEL=claude-sonnet-4.5
MAX_TOKENS=1024
TEST_PROMPT=Hello, please reply with a short API test message.
```

Y nghia cac bien:

- `ANTHROPIC_AUTH_TOKEN`: API key
- `ANTHROPIC_BASE_URL`: base URL cua API
- `ANTHROPIC_MODEL`: model dung de goi `messages`
- `MAX_TOKENS`: so token output toi da
- `TEST_PROMPT`: prompt test

## 2. Cac file example

Ba file example la ba file doc lap, khong dung helper chung. Moi file tu xu ly:

- load `.env`
- doc config
- tao request
- goi `curl.exe`
- in ket qua

Danh sach file:

- [model_list_example.py](/d:/Python/azure/model_list_example.py): goi `GET /models` va in response
- [invoke_example.py](/d:/Python/azure/invoke_example.py): goi `POST /messages` mot lan voi `stream: false`, payload co `thinking`, va in ra raw response goc
- [invoke_stream_example.py](/d:/Python/azure/invoke_stream_example.py): goi `POST /messages` mot lan voi `stream: true` va in text stream ra terminal
- [test.py](/d:/Python/azure/test.py): chay lan luot 3 file tren trong cung mot process Python

## 3. Cach chay

Chay tung file:

```powershell
python .\model_list_example.py
python .\invoke_example.py
python .\invoke_stream_example.py
```

Chay tong hop:

```powershell
python .\test.py
```

## 4. Ket qua mong doi

- `model_list_example.py`: in JSON model list neu server tra JSON; neu khong, file se in raw response
- `invoke_example.py`: in `=== REQUEST JSON ===` va sau do in `=== RESPONSE ===` voi response goc tu API
- `invoke_stream_example.py`: in request JSON truoc, sau do in text stream khi server day du lieu

## 5. Luu y

- Cac file dang goi API qua `curl.exe`.
- `invoke_example.py` khong parse response nua; muc tieu la de nhin truc tiep raw response, bao gom ca phan `thinking` neu API tra ve.
- `invoke_stream_example.py` dang doc SSE va in ra text delta trong stream.
- Neu ban muon test rieng model list, hay chay `model_list_example.py` truoc.
