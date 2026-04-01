import threading
from fastapi import FastAPI
from utils.feishu_bot import ws_client

app = FastAPI()


# main.py 底部添加
def start():
    print("🚀 启动飞书机器人长连接...")
    threading.Thread(target=ws_client.start, daemon=True).start()  # 启动长连接线程

    print("🚀 启动 FastAPI 服务...")
    import uvicorn
    # 这里确保 "main" 是你的文件名，app 是 FastAPI 实例名
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start()