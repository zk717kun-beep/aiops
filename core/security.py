import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# 飞书管理员白名单 User IDs
ALLOWED_USERS = {"ou_1234567890abcdef", "ou_0987654321fedcba"}

# 危险命令正则黑名单 (可根据需求扩展)
DANGEROUS_PATTERNS = [
    r"\brm\s+.*-r",       # 禁止递归删除
    r">\s*/dev/sd",       # 禁止直接写入块设备
    r"\bmkfs\b",          # 禁止格式化
    r"\b(reboot|shutdown|halt)\b", # 禁止关机
    r"\|\s*(bash|sh)\b",  # 禁止管道直接输入给 shell
    r"\b(nc|netcat)\b\s+-e" # 禁止反弹 shell
]

class SecuritySandbox:
    @staticmethod
    def is_user_allowed(user_id: str) -> bool:
        return user_id in ALLOWED_USERS

    @staticmethod
    def audit_command(command: str) -> Tuple[bool, str]:
        """
        审计命令是否安全
        :return: (is_safe, reason)
        """
        cmd_lower = command.lower()
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                logger.warning(f"Intercepted dangerous command: {command} (Pattern: {pattern})")
                return False, f"触发安全拦截: 包含被禁止的指令模式 ({pattern})"
        
        # 针对 sudo 的特殊处理：只允许白名单内的 sudo 命令
        if command.strip().startswith("sudo"):
            allowed_sudos = ["sudo systemctl restart", "sudo docker", "sudo tail"]
            if not any(command.startswith(allowed) for allowed in allowed_sudos):
                return False, "触发安全拦截: 该 sudo 命令未在提权白名单中"

        return True, "Safe"