import asyncio
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from config_loader import CONFIG

from pathlib import Path

def load_system_prompt(path: str = "skill/system.md") -> str:
    return Path(path).read_text(encoding="utf-8")

SYSTEM_PROMPT = load_system_prompt()

class LLMClient:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str = "gpt-4o-mini",
        timeout: int = 30,
        max_retries: int = 3,
        system_prompt: str = None,
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self.max_retries = max_retries
        self.system_prompt = system_prompt

    async def achat(
        self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2
    ) -> str:
        messages = []
        final_system = system_prompt or self.system_prompt
        if final_system:
            messages.append({"role": "system", "content": final_system})
        messages.append({"role": "user", "content": prompt})

        resp = await self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=temperature
        )
        return resp.choices[0].message.content.strip()


# =============================
# 初始化 LLM 客户端
# =============================
API_BASE = CONFIG.get("llm_engine", {}).get("nodes", {}).get("minimax-chat", {}).get("api_base", "")
API_KEY = CONFIG.get("llm_engine", {}).get("nodes", {}).get("minimax-chat", {}).get("api_key", "")
API_MODEL = CONFIG.get("llm_engine", {}).get("nodes", {}).get("minimax-chat", {}).get("model_name", "")

_llm_client: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(
            api_key=API_KEY,
            base_url=API_BASE,
            model=API_MODEL,
            system_prompt=SYSTEM_PROMPT,
        )
    return _llm_client


async def aget_llm_client() -> LLMClient:
    return get_llm_client()

