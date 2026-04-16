import json
import os
import subprocess
from pathlib import Path


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


def main() -> None:
    load_env()
    base_url, api_key = get_api_config()

    result = subprocess.run(
        [
            "curl.exe",
            "-sS",
            f"{base_url}/models",
            "-H",
            "Accept: application/json",
            "-H",
            f"x-api-key: {api_key}",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=500,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Request failed")

    cleaned = result.stdout.strip()
    if not cleaned:
        print(json.dumps({"type": "empty_response", "raw": result.stdout}, ensure_ascii=False, indent=2))
        return

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        print(json.dumps({"type": "raw_text", "raw": cleaned}, ensure_ascii=False, indent=2))
        return

    print(json.dumps(parsed, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
