from typing import List, Dict

class BaseLLMAdapter:
    def __init__(self, model_name: str, api_base: str, api_key: str = None):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    async def generate_reply(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError("子类必须实现 generate_reply 方法")