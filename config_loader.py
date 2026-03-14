import os
import yaml
import re

def load_yaml_with_env(file_path: str) -> dict:
    """
    加载 YAML 文件并自动解析环境变量占位符 ${ENV:VAR_NAME}
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 正则匹配 ${ENV:XXX} 格式
    pattern = re.compile(r'\$\{ENV:([a-zA-Z0-9_]+)\}')
    
    def replace_env(match):
        env_var = match.group(1)
        # 如果环境变量不存在，可以抛出异常或返回空字符串
        return os.environ.get(env_var, f"<MISSING_ENV_{env_var}>")

    # 替换内容后重新解析为字典
    parsed_content = pattern.sub(replace_env, content)
    return yaml.safe_load(parsed_content)

# 初始化全局配置
# CONFIG = load_yaml_with_env("config.yaml")