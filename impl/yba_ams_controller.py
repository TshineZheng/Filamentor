import threading
import time
from typing import List
from controller import ChannelAction, Controller
import socket

CH_MAP = [1, 2, 3, 4]  # 通道映射表
ams_head = b'\x2f\x2f\xff\xfe\x01\x02'

class YBAAMSController(Controller):
    @staticmethod
    def type_name() -> str:
        return "yba_ams"

    def __init__(self, ip: str, port: int, channel_count: int):
        super().__init__(channel_count)
        self.ip:str = ip
        self.port:str = port
        self.sock:socket.socket = None
        self.ch_state:List[int] = [0, 0, 0, 0]
        self.running = False
        self.thread: threading.Thread = None
        self.lock = threading.Lock()

    @classmethod
    def from_dict(cls, json_data: dict):
        return cls(
            json_data["ip"],
            json_data["port"],
            json_data["channel_count"]
        )

    def to_dict(self) -> dict:
        return {
            'ip': self.ip,
            'port': self.port,
            'channel_count': self.channel_count
        }
    
    def start(self):
        super().start()
        self.connect()
        self.running = True
        self.thread = threading.Thread(target=self.heartbeat)
        self.thread.start()
    
    def stop(self):
        super().stop()
        self.disconnect()
        self.running = False
        if self.thread:
            self.thread.join()

    def connect(self):
        self.disconnect()
        self.sock = self.connect_to_server(self.ip, self.port)
        
    def disconnect(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception as e:
                print(f"关闭socket失败: {e}")

    # 向AMS发送指令
    def send_ams(self, data):
        """发送数据到服务器，如果连接断开，自动重新连接并重新发送"""
        if self.sock is None:
            self.connect()

        while True:
            try:
                self.sock.sendall(data)
                return
            except Exception as e:
                print(f"向AMS发送指令失败: {e}")
                print("尝试重新连接...")
                self.connect()
                print("重新连接成功，尝试再次发送")

    def ams_control(self, ch, fx):
        self.send_ams(ams_head + bytes([ch]) + bytes([fx]))
        self.ch_state[ch] = fx

    # 查找耗材对应的通道
    def find_channel(self, filament):
        for i in range(len(CH_MAP)):
            if CH_MAP[i] == filament:
                return i
        return -1

    def connect_to_server(self, server_ip, server_port):
        """尝试连接到服务器，并返回socket对象"""
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server_ip, server_port))
                print("连接到AMS成功")
                return sock
            except Exception as e:
                print(f"连接到AMS失败: {e}")
                print("5秒后尝试重新连接...")
                time.sleep(5)

    def heartbeat(self):
        while self.running:
            if self.sock is None:
                time.sleep(1)
            else:
                for t in range(5):
                    for i in range(4):
                        self.ams_control(i, self.ch_state[i]) # 心跳+同步状态 先这样写，后面再改
                        time.sleep(0.3)
                    time.sleep(1)

    def control(self, channel_index: int, action: ChannelAction) -> bool:
        if channel_index < 0 or channel_index >= self.channel_count:
            return False
        
        if action == ChannelAction.PUSH:
            self.ams_control(channel_index, 1)
        elif action == ChannelAction.PULL:
            self.ams_control(channel_index, 2)
        elif action == ChannelAction.STOP:
            self.ams_control(channel_index, 0)

        return True