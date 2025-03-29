import os
import asyncio
import websockets
import logging

# ================ 配置部分 ================
HOST = "0.0.0.0"  # 必须绑定到 0.0.0.0
PORT = int(os.environ.get("PORT", 8000))  # 读取 Railway 环境变量

# ================ 日志配置 ================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ================ WebSocket 服务 ================
class WebSocketServer:
    def __init__(self):
        self.clients = set()

    async def handler(self, websocket, path):
        """处理客户端连接"""
        self.clients.add(websocket)
        client_ip = websocket.remote_address[0]
        logging.info(f"🌐 新连接来自 {client_ip} (当前连接数: {len(self.clients)})")

        try:
            async for message in websocket:
                logging.info(f"📥 收到消息: {message[:50]}...")  # 截断长消息
                await self.broadcast(message)
        except websockets.ConnectionClosed:
            logging.info(f"❌ 连接关闭: {client_ip}")
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, message):
        """广播消息给所有客户端"""
        if len(self.clients) == 0:
            logging.warning("⚠️ 无可用的客户端连接")
            return

        for client in self.clients.copy():  # 使用副本避免迭代时修改
            try:
                await client.send(message)
                logging.debug(f"📤 消息已发送至 {client.remote_address[0]}")
            except:
                logging.warning(f"⛔ 发送失败: {client.remote_address[0]}")
                self.clients.discard(client)

async def main():
    server = WebSocketServer()
    async with websockets.serve(
        server.handler,
        HOST,
        PORT,
        ping_interval=30,  # 保持连接活跃
        ping_timeout=60
    ):
        logging.info(f"🚀 服务已启动: ws://{HOST}:{PORT}")
        logging.info(f"📡 公网访问地址: wss://your-app.up.railway.app")  # 需替换实际域名
        await asyncio.Future()  # 永久运行

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"💥 服务启动失败: {str(e)}")
    except KeyboardInterrupt:
        logging.info("👋 服务已正常关闭")