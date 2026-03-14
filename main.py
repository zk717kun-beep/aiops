from fastapi import FastAPI, BackgroundTasks
from llm.adapters import OpenAIAdapter, AnthropicAdapter
from llm.engine import MultiModelChatEngine
from utils.feishu_bot import FeishuBot

app = FastAPI()
bot = FeishuBot(tenant_access_token="...")

@app.post("/webhook/feishu")
async def handle_feishu(payload: dict, background_tasks: BackgroundTasks):
    # 省略签名校验和 UserID 过滤...
    
    # 模拟场景：用户发送“分析架构”，触发 GPT-4 与 Claude 的对话
    if "分析架构" in payload.get("text", ""):
        background_tasks.add_task(start_llm_battle, payload["open_id"])
    
    return {"status": "ok"}

async def start_llm_battle(user_id: str):
    # 1. 动态初始化两个不同的适配器
    gpt = OpenAIAdapter("gpt-4o", "https://api.openai.com")
    claude = AnthropicAdapter("claude-3-5-sonnet-20240620", "https://api.anthropic.com", "key_xxx")
    
    engine = MultiModelChatEngine(gpt, claude)
    
    async for msg in engine.run_conversation("讨论 AIOps 安全边界"):
        # 实时推送到飞书
        text = f"【第{msg['turn']}轮 - {msg['role']}】\n{msg['content']}"
        await bot.send_message(user_id, text)


# main.py 底部添加
def start():
    import uvicorn
    # 这里确保 "main" 是你的文件名，app 是 FastAPI 实例名
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()