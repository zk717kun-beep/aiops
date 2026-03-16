import argparse
import asyncio
import json
import os
import sys
from typing import Any

import aiohttp


DEFAULT_API_BASE = "https://api.minimax.chat"
DEFAULT_MODEL = "abab6.5s-chat"


async def send_minimax_chat(
    api_base: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int,
) -> dict[str, Any]:
    url = f"{api_base.rstrip('/')}/v1/text/chatcompletion_v2"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "stream": False,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    timeout_cfg = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            body = await resp.text()
            if resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status} from {url}: {body}")

    data = json.loads(body)
    reply = data.get("choices", [{}])[0].get("message", {}).get("content")
    if not reply:
        raise RuntimeError(f"No assistant reply in response: {data}")

    return {"model": model, "reply": reply, "raw": data}


async def run_test(args: argparse.Namespace) -> int:
    api_key = args.api_key or os.getenv(args.api_key_env)
    if not api_key:
        print(f"缺少 API Key，请通过 --api-key 或环境变量 {args.api_key_env} 提供", file=sys.stderr)
        return 2

    try:
        result = await send_minimax_chat(
            api_base=args.api_base,
            api_key=api_key,
            model=args.model,
            prompt=args.prompt,
            timeout=args.timeout,
        )
    except Exception as exc:
        print(f"❌ MiniMax 聊天测试失败: {exc}", file=sys.stderr)
        return 1

    print("✅ MiniMax 聊天测试成功")
    print(f"Model: {result['model']}")
    print("Assistant reply:")
    print(result["reply"])

    if args.print_json:
        print("\nRaw response JSON:")
        print(json.dumps(result["raw"], ensure_ascii=False, indent=2))

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="测试 MiniMax 聊天接口连通性")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE, help="MiniMax API 基础地址")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="MiniMax 模型名")
    parser.add_argument("--prompt", default="你好，请回复：MiniMax 连接测试成功", help="测试提示词")
    parser.add_argument("--api-key", help="MiniMax API Key")
    parser.add_argument("--api-key-env", default="MINIMAX_API_KEY", help="读取 API Key 的环境变量")
    parser.add_argument("--timeout", type=int, default=30, help="请求超时时间（秒）")
    parser.add_argument("--print-json", action="store_true", help="打印完整 JSON 响应")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run_test(args)))


if __name__ == "__main__":
    main()
