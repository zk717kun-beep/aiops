from typing import AsyncGenerator
from .base import BaseLLMAdapter

class MultiModelChatEngine:
    def __init__(self, agent_a: BaseLLMAdapter, agent_b: BaseLLMAdapter, max_turns: int = 5):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.max_turns = max_turns

    async def run_conversation(self, initial_topic: str) -> AsyncGenerator[dict, None]:
        history_a = [{"role": "system", "content": "你是架构师。"}, {"role": "user", "content": initial_topic}]
        history_b = [{"role": "system", "content": "你是审核员。"}]

        current_input = initial_topic
        for turn in range(self.max_turns):
            # Agent A 说话
            reply_a = await self.agent_a.generate_reply(history_a)
            yield {"turn": turn+1, "role": "Architect", "content": reply_a}
            
            # Agent B 说话
            history_b.append({"role": "user", "content": reply_a})
            reply_b = await self.agent_b.generate_reply(history_b)
            yield {"turn": turn+1, "role": "Reviewer", "content": reply_b}
            
            # 更新 A 的上下文
            history_a.append({"role": "assistant", "content": reply_a})
            history_a.append({"role": "user", "content": reply_b})