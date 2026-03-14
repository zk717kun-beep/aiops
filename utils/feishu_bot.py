import os
import aiohttp

class FeishuBot:
    def __init__(self, tenant_access_token: str):
        self.token = tenant_access_token
        self.headers = {"Authorization": f"Bearer {self.token}"}

    async def send_message(self, receive_id: str, content: str, msg_type: str = "text"):
        """发送文本或卡片消息"""
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        payload = {
            "receive_id": receive_id,
            "msg_type": msg_type,
            "content": content
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=payload) as resp:
                return await resp.json()

    async def reply_execution_result(self, receive_id: str, cmd: str, result: dict):
        """处理执行结果并回传飞书"""
        out_text = f"【命令】: {cmd}\n【状态】: {result['status']}\n【退出码】: {result['return_code']}\n"
        detail_text = result['stdout'] if result['return_code'] == 0 else result['stderr']
        
        # 飞书消息有长度限制，通常建议单条文本不超过 4000 字
        if len(detail_text) > 2000:
            # 策略：生成临时文件并走文件上传逻辑 (此处用截断示意)
            out_text += f"\n【输出】:\n{detail_text[:2000]}\n\n...(输出过长，已截断。请在服务器查看完整日志)..."
            # TODO: 实际生产中，可以调用飞书上传文件 API (im/v1/files)，然后发送 file 类型的消息
        else:
            out_text += f"\n【输出】:\n{detail_text}"

        # 封装为飞书所需的 JSON 字符串格式
        import json
        await self.send_message(receive_id, json.dumps({"text": out_text}))