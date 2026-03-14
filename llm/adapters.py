import asyncio
import json

import aiohttp
from llm.base import BaseLLMAdapter
from typing import AsyncGenerator, Dict, List

class OpenAIAdapter(BaseLLMAdapter):
    """适配 OpenAI, DeepSeek, vLLM, Qwen 等"""
    async def generate_reply(self, messages: List[Dict[str, str]]) -> str:
        payload = {"model": self.model_name, "messages": messages, "temperature": 0.7}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/v1/chat/completions", 
                                    headers=self.headers, json=payload) as resp:
                result = await resp.json()
                return result["choices"][0]["message"]["content"]

class AnthropicAdapter(BaseLLMAdapter):
    """适配 Claude 系列 (Anthropic 原生协议适配)"""
    async def generate_reply(self, messages: List[Dict[str, str]]) -> str:
        # 协议转换：提取 system 角色
        system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        
        payload = {
            "model": self.model_name,
            "system": system_msg, # Anthropic 特有字段
            "messages": user_messages,
            "max_tokens": 1024
        }
        # 修改 Header 为 Anthropic 要求
        headers = {**self.headers, "x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/v1/messages", 
                                    headers=headers, json=payload) as resp:
                result = await resp.json()
                return result["content"][0]["text"]


async def generate_minimax_stream(prompt: str) -> AsyncGenerator[str, None]:
    """
    连接 MiniMax API 并以 SSE 格式流式 yield 数据
    """
    # 采用 MiniMax 最新一代 V2 接口
    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # MiniMax V2 接口的 Payload 格式
    payload = {
        "model": "abab6.5s-chat", # 或者 abab6.5-chat
        "stream": True,           # 开启流式输出
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status != 200:
                    error_msg = await response.text()
                    yield f"data: {json.dumps({'error': f'API Error {response.status}: {error_msg}'})}\n\n"
                    return

                # 逐行读取流式响应内容
                async for line in response.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        
                        # SSE 协议的标准格式是 "data: {...}"
                        if line_str.startswith("data: "):
                            data_str = line_str[6:] # 去除 "data: " 前缀
                            
                            # 结束标志
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                data_json = json.loads(data_str)
                                # 提取 MiniMax 返回的增量文本 (Delta)
                                delta_content = data_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                
                                if delta_content:
                                    # 将增量内容重新包装为前端易于解析的 JSON 格式，并遵循 SSE 规范 (以 \n\n 结尾)
                                    output = {"chunk": delta_content}
                                    yield f"data: {json.dumps(output)}\n\n"
                                    
                            except json.JSONDecodeError:
                                # 忽略解析错误的脏数据片段
                                continue
        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'error': '请求 MiniMax 超时'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"