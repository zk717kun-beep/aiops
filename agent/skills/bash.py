import asyncio

BUILD_PROMPT = """
你是一个专业的系统执行助手（System Executor），专门根据用户问题生成可执行脚本。你的任务是：

要求：
1. 根据用户问题生成可执行的系统脚本（Bash 或 Python），可直接交给执行器运行。
2. 脚本必须能够执行并返回结果，包括标准输出(stdout)和标准错误(stderr)，便于上层系统获取。
3. 仅输出可执行代码，不输出任何解释、分析、注释或额外文字。
4. 如果用户问题涉及系统权限操作或需要管理员权限，请在脚本中使用 sudo。
5. 如果涉及目录或文件操作，脚本应安全可靠，可直接运行。
6. 输出格式必须干净、可解析，代码块用 ```bash 或 ```python 包裹。
7. 只输出一个代码块，保证可以直接执行。

示例：
问题：查看 /home 目录下有多少文件
输出：
```bash
#!/bin/bash
count=$(find /home -type f | wc -l)
echo "$count"

问题：列出当前目录下所有 .txt 文件并统计数量
输出：
```bash
#!/bin/bash
count=$(ls -1 *.txt 2>/dev/null | wc -l)
echo "$count"

现在请根据以下问题生成可执行脚本：

问题：{{ question }}
"""


class RegisterBatchSkill:
    name = "bash"
    description = "执行系统 Bash 命令并返回标准输出或错误信息"
    when_to_use = (
        "当用户需要在系统中执行命令，例如文件操作、目录查询、进程检查、环境查看等"
    )
    argument_hint = "<bash 命令>"
    user_invocable = True
    disable_model_invocation = False

    def __init__(self):
        pass

    # =========================
    # Prompt 构建（可用于 LLM 生成命令）
    # =========================
    async def get_prompt(self, instruction: str) -> str:
        """
        根据用户输入生成完整的 LLM Prompt
        """
        instruction = instruction.strip()
        if not instruction:
            return "请提供需要执行的命令"

        # 替换占位符
        prompt = BUILD_PROMPT.replace("{{ question }}", instruction)
        return prompt

    # =========================
    # 执行逻辑
    # =========================
    async def execute(self, input_text: str) -> str:
        """
        执行 Bash 命令，返回标准输出或标准错误
        """
        command = input_text.strip()

        if not command:
            return "没有提供命令"

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await proc.communicate()

            if stdout:
                return stdout.decode().strip()
            elif stderr:
                return f"错误:\n{stderr.decode().strip()}"
            else:
                return "命令执行完成，但没有输出"

        except Exception as e:
            return f"执行命令失败: {e}"


# =============================
# 示例独立运行
# =============================
async def main():
    bash_skill = RegisterBatchSkill()
    result = await bash_skill.execute("ls -l /tmp")
    print(result)

if __name__ == "__main__":
    print("=== 测试开始 ===")
    asyncio.run(main())