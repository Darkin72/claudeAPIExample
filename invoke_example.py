import json
import os
import subprocess
from pathlib import Path
from typing import Any


def load_env(env_path: str = ".env") -> None:
    env_file = Path(env_path)
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_api_config() -> tuple[str, str]:
    base_url = os.getenv("ANTHROPIC_BASE_URL", "").rstrip("/")
    api_key = os.getenv("ANTHROPIC_AUTH_TOKEN", "")

    if not base_url:
        raise ValueError("Missing ANTHROPIC_BASE_URL in .env")
    if not api_key:
        raise ValueError("Missing ANTHROPIC_AUTH_TOKEN in .env")

    return base_url, api_key


def build_payload() -> dict[str, Any]:
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6-20250827")
    max_tokens = int(os.getenv("MAX_TOKENS", "256"))
    prompt = os.getenv("TEST_PROMPT", "Hello from a simple API test.")

    return {
        "model": model,
        "max_tokens": max_tokens,
        "stream": False,
        "thinking": {"type": "enabled"},
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }


def parse_sse_events(raw_text: str) -> list[dict[str, Any]]:
    events = []
    current_event = None
    current_data = None

    for raw_line in raw_text.splitlines():
        line = raw_line.strip()

        if line.startswith("event: "):
            current_event = line[7:]
            continue

        if line.startswith("data: "):
            current_data = line[6:]
            continue

        if not line and current_event and current_data:
            try:
                parsed_data = json.loads(current_data)
            except json.JSONDecodeError:
                parsed_data = current_data

            events.append({"event": current_event, "data": parsed_data})
            current_event = None
            current_data = None

    if current_event and current_data:
        try:
            parsed_data = json.loads(current_data)
        except json.JSONDecodeError:
            parsed_data = current_data

        events.append({"event": current_event, "data": parsed_data})

    return events


def summarize_sse_response(raw_text: str) -> tuple[str, str]:
    events = parse_sse_events(raw_text)
    thinking_parts = []
    text_parts = []

    for item in events:
        data = item.get("data", {})
        if not isinstance(data, dict):
            continue

        delta = data.get("delta", {})
        if isinstance(delta, dict):
            thinking = delta.get("thinking")
            text = delta.get("text")

            if thinking:
                thinking_parts.append(thinking)

            if text:
                text_parts.append(text)

        content_block = data.get("content_block", {})
        if isinstance(content_block, dict):
            block_type = content_block.get("type")
            if block_type == "thinking" and content_block.get("thinking"):
                thinking_parts.append(content_block["thinking"])
            if block_type == "text" and content_block.get("text"):
                text_parts.append(content_block["text"])

    return "".join(thinking_parts).strip(), "".join(text_parts).strip()


def summarize_json_response(raw_text: str) -> tuple[str, str]:
    parsed = json.loads(raw_text)
    content = parsed.get("content", []) if isinstance(parsed, dict) else []
    thinking_parts = []
    text_parts = []

    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue

            block_type = item.get("type")
            if block_type == "thinking" and item.get("thinking"):
                thinking_parts.append(item["thinking"])
            if block_type == "text" and item.get("text"):
                text_parts.append(item["text"])

    return "".join(thinking_parts).strip(), "".join(text_parts).strip()


def print_summary(raw_text: str) -> None:
    cleaned = raw_text.strip()
    if not cleaned:
        print('thinking: ""')
        print('response: ""')
        return

    if "event:" in cleaned and "data:" in cleaned:
        thinking, response = summarize_sse_response(raw_text)
        print(f'thinking: {json.dumps(thinking, ensure_ascii=False)}')
        print(f'response: {json.dumps(response, ensure_ascii=False)}')
        return

    try:
        thinking, response = summarize_json_response(cleaned)
    except json.JSONDecodeError:
        print('thinking: ""')
        print(f"response: {json.dumps(raw_text, ensure_ascii=False)}")
        return

    print(f'thinking: {json.dumps(thinking, ensure_ascii=False)}')
    print(f'response: {json.dumps(response, ensure_ascii=False)}')


def main() -> None:
    load_env()
    base_url, api_key = get_api_config()
    payload = build_payload()
    body = json.dumps(payload, ensure_ascii=False)

    print("=== REQUEST JSON ===")
    print(body)

    result = subprocess.run(
        [
            "curl.exe",
            "-sS",
            f"{base_url}/messages",
            "-H",
            "Content-Type: application/json",
            "-H",
            "Accept: application/json",
            "-H",
            f"x-api-key: {api_key}",
            "--data-binary",
            "@-",
        ],
        input=body,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=500,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Request failed")

    print("=== RESPONSE ===")
    print_summary(result.stdout)


if __name__ == "__main__":
    main()
