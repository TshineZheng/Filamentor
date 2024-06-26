import threading
import time
from typing import List
from src.controller import ChannelAction, Controller
import socket

from src.utils.log import LOGE, LOGI

ams_head = b'\x2f\x2f\xff\xfe\x01\x02'


class YBAAMSController(Controller):
    @staticmethod
    def type_name() -> str:
        return "yba_ams"

    def __init__(self, ip: str, port: int, channel_count: int):
        super().__init__(channel_count)
        self.ip: str = ip
        self.port: str = port
        self.sock: socket.socket = None
        self.ch_state: List[int] = [0] * channel_count
        self.thread: threading.Thread = None
        self.lock = threading.Lock()

    def __eq__(self, other):
        if isinstance(other, YBAAMSController):
            return self.ip == other.ip
        return False

    def get_channel_states(self) -> List[int]:
        return self.ch_state

    def __str__(self):
        return self.type_name()

    @classmethod
    def from_dict(cls, json_data: dict):
        return cls(
            json_data["ip"],
            json_data["port"],
            json_data["channel_total"]
        )

    def to_dict(self) -> dict:
        return {
            'ip': self.ip,
            'port': self.port,
            'channel_total': self.channel_total
        }

    def start(self):
        super().start()
        self.connect()
        self.thread = threading.Thread(target=self.heartbeat, name=f"yba-ams({self.ip}) heartbeat")
        self.thread.start()

    def stop(self):
        super().stop()
        self.disconnect()
        if self.thread:
            self.thread.join()
            self.sock = None
            self.thread = None

    def connect(self):
        self.disconnect()
        if self.is_running:
            self.sock = self.connect_to_server(self.ip, self.port)

    def disconnect(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
                self.sock = None
            except Exception as e:
                LOGE(f"关闭socket失败: {e}")

    # 向YBA发送指令
    def send_ams(self, data):
        """发送数据到服务器，如果连接断开，自动重新连接并重新发送"""
        if self.sock is None:
            self.connect()

        while True:
            try:
                self.sock.settimeout(3)
                self.sock.sendall(data)
                self.sock.settimeout(None)
                return
            except Exception as e:
                LOGE(f"向YBA发送指令失败: {e}")
                LOGE("尝试重新连接...")
                self.connect()
                LOGE("重新连接成功，尝试再次发送")

    def ams_control(self, ch, fx):
        self.send_ams(ams_head + bytes([ch]) + bytes([fx]))
        self.ch_state[ch] = fx

    def connect_to_server(self, server_ip, server_port):
        """尝试连接到服务器，并返回socket对象"""
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server_ip, server_port))
                LOGI(f"连接到 YBA-AMS ({server_ip})成功")
                return sock
            except Exception as e:
                LOGE(f"连接到 YBA-AMS 失败: {e}")
                LOGE("2秒后尝试重新连接...")
                time.sleep(2)

    def heartbeat(self):
        while self.is_running:
            if self.sock is None:
                time.sleep(1)
            else:
                for t in range(5):
                    for i in self.channel_total:
                        if not self.is_running:
                            break
                        self.ams_control(i, self.ch_state[i])  # 心跳+同步状态 先这样写，后面再改
                        time.sleep(0.3)
                    time.sleep(1)

    def control(self, channel_index: int, action: ChannelAction) -> bool:
        if False == super().control(channel_index, action):
            return False

        if action == ChannelAction.PUSH:
            self.ams_control(channel_index, 1)
        elif action == ChannelAction.PULL:
            self.ams_control(channel_index, 2)
        elif action == ChannelAction.STOP:
            self.ams_control(channel_index, 0)

        return True

    def is_initiative_push(self, channel_index: int) -> bool:
        return True
