from llm.adapters import OpenAIAdapter, AnthropicAdapter, MiniMaxAdapter # 假设您已完成这些类

class LLMFactory:
    def __init__(self, config_dict: dict):
        self.config = config_dict
        self.nodes = self.config.get("llm_engine", {}).get("nodes", {})

    def create_adapter(self, alias: str):
        """
        根据配置文件中的别名，动态生成对应的适配器实例
        """
        if alias not in self.nodes:
            raise ValueError(f"配置错误: 未找到模型别名 '{alias}'")

        node_cfg = self.nodes[alias]
        provider = node_cfg.get("provider")
        
        # 提取通用参数
        model_name = node_cfg.get("model_name")
        api_base = node_cfg.get("api_base")
        api_key = node_cfg.get("api_key")

        # 根据 provider 路由到具体的实现类
        if provider == "openai" or provider == "vllm":
            return OpenAIAdapter(model_name, api_base, api_key)
        elif provider == "minimax":
            return MiniMaxAdapter(model_name, api_base, api_key)
        elif provider == "anthropic":
            return AnthropicAdapter(model_name, api_base, api_key)
        else:
            raise NotImplementedError(f"暂不支持的 Provider: {provider}")

# 使用示例：
# factory = LLMFactory(CONFIG)
# 业务逻辑中不需要知道底层是什么，只需请求一个用于核心决策的 agent
# ops_agent = factory.create_adapter(CONFIG["llm_engine"]["routing"]["default_ops_agent"])