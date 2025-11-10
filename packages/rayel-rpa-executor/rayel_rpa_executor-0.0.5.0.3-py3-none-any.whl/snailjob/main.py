import threading
import time

from .cfg import SNAIL_HOST_PORT
from .exec import ExecutorManager
from .grpc import run_grpc_server
from .rpc import send_heartbeat


class HeartbeatTask:
    """心跳发送任务"""

    def __init__(self) -> None:
        self._thread = threading.Thread(target=self._send_heartbeats, daemon=True)
        self.event = threading.Event()

    def _send_heartbeats(self):
        while not self.event.is_set():
            send_heartbeat()
            time.sleep(28)

    def run(self):
        self._thread.start()

def client_main():
    """客户端主函数"""
    heartbeat_task = HeartbeatTask()
    heartbeat_task.run()
    # 注册执行器
    ExecutorManager.register_executors_to_server()
    # 尝试注册元信息,失败了服务端会来拉取
    ExecutorManager.registry_node_metadata_to_server()
    run_grpc_server(SNAIL_HOST_PORT)

