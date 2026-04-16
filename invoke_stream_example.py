import json
import os
import subprocess
import time
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
        "stream": True,
        "thinking": {"type": "enabled"},
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }


def main() -> None:
    load_env()
    base_url, api_key = get_api_config()
    payload = build_payload()
    body = json.dumps(payload, ensure_ascii=False)

    print("=== REQUEST JSON ===")
    print(body)

    process = subprocess.Popen(
        [
            "curl.exe",
            "-N",
            "-sS",
            f"{base_url}/messages",
            "-H",
            "Content-Type: application/json",
            "-H",
            "Accept: text/event-stream",
            "-H",
            f"x-api-key: {api_key}",
            "--data-binary",
            "@-",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )

    if process.stdin is None or process.stdout is None:
        raise RuntimeError("Cannot open stream process")

    process.stdin.write(body)
    process.stdin.close()

    thinking_parts = []
    response_parts = []
    thinking_started = False
    response_started = False

    print("=== STREAM ===")
    for raw_line in process.stdout:
        line = raw_line.strip()
        if not line.startswith("data: "):
            continue

        try:
            event_data = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        delta = event_data.get("delta", {})
        if isinstance(delta, dict):
            thinking = delta.get("thinking")
            text = delta.get("text")
            if thinking:
                thinking_parts.append(thinking)
                if not thinking_started:
                    print("thinking: ", end="", flush=True)
                    thinking_started = True
                print(thinking, end="", flush=True)
            if text:
                response_parts.append(text)
                if thinking_started and not response_started:
                    print()
                if not response_started:
                    print("response: ", end="", flush=True)
                    response_started = True
                print(text, end="", flush=True)

        content_block = event_data.get("content_block", {})
        if isinstance(content_block, dict):
            block_type = content_block.get("type")
            if block_type == "thinking" and content_block.get("thinking"):
                thinking = content_block["thinking"]
                thinking_parts.append(thinking)
                if not thinking_started:
                    print("thinking: ", end="", flush=True)
                    thinking_started = True
                print(thinking, end="", flush=True)
            if block_type == "text" and content_block.get("text"):
                text = content_block["text"]
                response_parts.append(text)
                if thinking_started and not response_started:
                    print()
                if not response_started:
                    print("response: ", end="", flush=True)
                    response_started = True
                print(text, end="", flush=True)

        time.sleep(0.02)

    return_code = process.wait(timeout=10)
    if return_code != 0:
        error_text = ""
        if process.stderr is not None:
            error_text = process.stderr.read().strip()
        raise RuntimeError(error_text or "Stream request failed")

    if thinking_started or response_started:
        print()


if __name__ == "__main__":
    main()
