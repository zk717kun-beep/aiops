import asyncio
import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import CreateMessageRequest, CreateMessageRequestBody, P2ImMessageReceiveV1, ReplyMessageRequest, ReplyMessageRequestBody
from config_loader import CONFIG
from utils.llm_client import get_llm_client

# =============================
# 配置
# =============================
# APP_ID = "cli_a92511780ab9dbdf"     # 替换为你的 APP_ID
# APP_SECRET = "21ei8Lq6cGSv6jVNm7llBh5WsWvco4cz"      # 替换为你的 APP_SECRET

APP_ID = CONFIG.get("feishu", {}).get("app_id", "")
APP_SECRET = CONFIG.get("feishu", {}).get("app_secret", "")

print("飞书机器人配置:", APP_ID, APP_SECRET)

# 创建 OpenAI 客户端
llm_client = get_llm_client()
# =============================
# 飞书客户端
# =============================
client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()


# =============================
# 消息处理
# =============================
async def handle_message_async(data: P2ImMessageReceiveV1):
    msg = data.event.message
    if msg.chat_type is None:
        return

    if msg.message_type != "text":
        reply_text = "请发送文本消息"
    else:
        user_text = json.loads(msg.content)["text"]
        print("用户输入:", user_text)
        # ✅ 直接 async 调用 LLM
        reply_text = await llm_client.achat(user_text)

    content = json.dumps({"text": reply_text})

    if msg.chat_type == "p2p":
        req = CreateMessageRequest.builder().receive_id_type("chat_id").request_body(
            CreateMessageRequestBody.builder().receive_id(msg.chat_id).msg_type("text").content(content).build()
        ).build()
        resp = client.im.v1.message.create(req)
    else:
        req = ReplyMessageRequest.builder().message_id(msg.message_id).request_body(
            ReplyMessageRequestBody.builder().content(content).msg_type("text").build()
        ).build()
        resp = client.im.v1.message.reply(req)

    if not resp.success():
        print("发送失败:", resp.code, resp.msg)


def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1):
    # ✅ 用线程安全方式调 async
    loop = asyncio.get_event_loop()
    asyncio.run_coroutine_threadsafe(handle_message_async(data), loop)


# =============================
# 注册事件
# =============================
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
    .build()
)

# =============================
# WebSocket 长连接
# =============================
ws_client = lark.ws.Client(APP_ID, APP_SECRET, event_handler=event_handler, log_level=lark.LogLevel.INFO)

