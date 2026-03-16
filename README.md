# aiops
## 大模型连通性测试工具

新增了 `llm-chat-test` 命令，用于快速验证大模型聊天接口是否可用。

### 用法示例

```bash
# OpenAI 兼容接口（OpenAI / DeepSeek / vLLM 等）
export OPENAI_API_KEY="your_api_key"
llm-chat-test \
  --provider openai \
  --api-base https://api.openai.com \
  --model gpt-4o-mini \
  --prompt "你好，请回复连接测试成功"

# Anthropic 接口
export ANTHROPIC_API_KEY="your_api_key"
llm-chat-test \
  --provider anthropic \
  --api-base https://api.anthropic.com \
  --api-key-env ANTHROPIC_API_KEY \
  --model claude-3-5-sonnet-20240620

# MiniMax 聊天接口
export MINIMAX_API_KEY="your_api_key"
minimax-chat-test \
  --model abab6.5s-chat \
  --prompt "你好，请回复：MiniMax 连接测试成功"
```

### 关键参数

- `--provider`: `openai` 或 `anthropic`。
- `--api-base`: API 基础地址。
- `--model`: 模型名称（必填）。
- `--api-key` / `--api-key-env`: API Key 直接传入或通过环境变量读取。
- `--print-json`: 输出完整原始响应，便于排障。

### MiniMax 专用脚本

也可以直接运行 Python 脚本：

```bash
export MINIMAX_API_KEY="your_api_key"
python tools/test_minimax_chat.py --print-json
```

默认配置：
- API 地址：`https://api.minimax.chat`
- 接口路径：`/v1/text/chatcompletion_v2`
- 默认模型：`abab6.5s-chat`
