import asyncio
import logging

logger = logging.getLogger(__name__)

class AsyncCommandExecutor:
    @staticmethod
    async def execute(command: str, timeout: int = 60) -> dict:
        """
        异步执行 shell 命令
        """
        logger.info(f"Executing command: {command}")
        try:
            # 创建异步子进程
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                # 如果需要特定的环境变量，可以在这里传入 env 参数
            )

            # 加上超时控制，防止命令假死
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            
            return {
                "status": "success" if process.returncode == 0 else "error",
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace').strip(),
                "stderr": stderr.decode('utf-8', errors='replace').strip()
            }
            
        except asyncio.TimeoutError:
            process.kill()
            return {
                "status": "timeout",
                "return_code": -1,
                "stdout": "",
                "stderr": f"命令执行超时 (>{timeout}s)，已被强制终止。"
            }
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return {
                "status": "exception",
                "return_code": -1,
                "stdout": "",
                "stderr": str(e)
            }