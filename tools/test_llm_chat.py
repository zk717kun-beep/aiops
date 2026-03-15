import argparse
import asyncio
import json
import os
import sys
from typing import Any

import aiohttp


async def send_openai_compatible_request(
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int,
) -> dict[str, Any]:
    url = f"{api_base.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status} from {url}: {body}")
            data = json.loads(body)

    reply = data.get("choices", [{}])[0].get("message", {}).get("content")
    if not reply:
        raise RuntimeError(f"No assistant reply in response: {data}")
    return {"model": model, "reply": reply, "raw": data}


async def send_anthropic_request(
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int,
) -> dict[str, Any]:
    url = f"{api_base.rstrip('/')}/v1/messages"
    payload = {
        "model": model,
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status} from {url}: {body}")
            data = json.loads(body)

    parts = data.get("content", [])
    reply = "".join(part.get("text", "") for part in parts if isinstance(part, dict)).strip()
    if not reply:
        raise RuntimeError(f"No assistant reply in response: {data}")
    return {"model": model, "reply": reply, "raw": data}


async def run_test(args: argparse.Namespace) -> int:
    api_key = args.api_key or os.getenv(args.api_key_env)
    if not api_key:
        print(
            f"Missing API key. Provide --api-key or set env var {args.api_key_env}",
            file=sys.stderr,
        )
        return 2

    try:
        if args.provider == "anthropic":
            result = await send_anthropic_request(
                args.api_base,
                api_key,
                args.model,
                args.prompt,
                args.timeout,
            )
        else:
            result = await send_openai_compatible_request(
                args.api_base,
                api_key,
                args.model,
                args.prompt,
                args.timeout,
            )
    except Exception as exc:
        print(f"❌ LLM connection test failed: {exc}", file=sys.stderr)
        return 1

    print("✅ LLM connection test succeeded")
    print(f"Provider: {args.provider}")
    print(f"Model: {result['model']}")
    print("Assistant reply:")
    print(result["reply"])

    if args.print_json:
        print("\nRaw response JSON:")
        print(json.dumps(result["raw"], ensure_ascii=False, indent=2))

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Test chat connectivity to a large language model API")
    parser.add_argument("--provider", choices=["openai", "anthropic"], default="openai")
    parser.add_argument("--api-base", default="https://api.openai.com", help="Base URL for LLM API")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--prompt", default="你好，请回复：连接测试成功", help="Prompt for test request")
    parser.add_argument("--api-key", help="API key for provider")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY", help="Environment variable for API key")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--print-json", action="store_true", help="Print full JSON response")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run_test(args)))


if __name__ == "__main__":
    main()
