import asyncio
import os
import importlib.util
import inspect
import os
from typing import Any, Dict, Callable, Optional
import json

from utils.llm_client import get_llm_client, LLMClient

# 创建 OpenAI 客户端
llm_client = get_llm_client()

class Skill:
    name: str
    description: str

# =============================
# Agent 定义
# =============================

class Agent:
    def __init__(self, llm_client):
        self.skills: Dict[str] = {}
        self.llm_client: LLMClient = llm_client

    def register_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    async def handle(self, user_input: str) -> str:
        # 1️⃣ 调用 LLM 做意图分析
        llm_output = await self.llm_client.achat(user_input)

        print("LLM 原始输出:", llm_output)

        # 2️⃣ 解析 JSON
        try:
            data = json.loads(llm_output)
        except Exception:
            return f"LLM 输出解析失败:\n{llm_output}"

        # 3️⃣ 判断是否需要调用工具
        if not data.get("should_use_agent", False):
            return data.get("final_answer", "没有结果")

        # 4️⃣ 执行 plan（多步骤）
        plan = data.get("plan", [])
        results = []

        for step in plan:
            skill_name = step.get("skill")
            input_text = step.get("input")

            skill = self.skills.get(skill_name)
            if not skill:
                results.append(f"[错误] 未找到技能: {skill_name}")
                continue

            result = await skill.execute(input_text)
            results.append(f"[{skill_name}] -> {result}")

        # 5️⃣ 汇总结果
        return "\n".join(results) if results else "执行完成，但没有结果"


# =============================
# 测试运行
# =============================
async def main():
    agent = Agent(llm_client)
    # 测试输入
    test_inputs = [
        "计算 2 + 3 * 5",
        "读取文件 /tmp/test.txt",
        "你好，Agent！",
    ]

    reply_text = await agent.handle("查看一下")
    print(reply_text)
    # for text in test_inputs:
    #     result = await agent.handle(text)
    #     print(f"> 用户输入: {text}")
    #     print(f"> Agent 输出: {result}\n")

# 全局注册表
SKILL_REGISTRY = {}

def register_skill(skill_instance: Skill):
    """将 Skill 实例注册到全局注册表"""
    SKILL_REGISTRY[skill_instance.name] = skill_instance


def load_and_register_skills(skill_folder: str = "skills"):
    """
    遍历 skill_folder 下的所有 Python 文件，加载类并注册到 agent
    """
    skill_folder = os.path.abspath(skill_folder)

    for root, dirs, files in os.walk(skill_folder):
        for file in files:
            print(file)
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(os.path.basename(file_path))[0]

                # 动态导入模块
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore

                # 遍历模块内所有类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    try:
                        instance = obj()  # 实例化
                        register_skill(instance)
                        print(f"注册 Skill: {instance.name}")
                    except Exception as e:
                        print(f"无法注册 {name}: {e}")


# =========================
# 使用示例
# =========================
if __name__ == "__main__":
    load_and_register_skills("agent/skills")  # 指定 skill 文件夹
    print("已注册的 Skill:", list(SKILL_REGISTRY.keys()))

    # asyncio.run(main())