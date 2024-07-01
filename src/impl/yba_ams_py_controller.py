import json
import select
import socket
import threading
import time
from src.impl.yba_ams_controller import YBAAMSController
from src.utils.log import LOGE, LOGI


class YBAAMSPYController(YBAAMSController):
    """YBA-AMS-Python 版本，用 python 复刻原版，增加内存指令

    Args:
        YBAAMSController (_type_): _description_

    Returns:
        _type_: _description_
    """
    @staticmethod
    def type_name() -> str:
        return "yba_ams_py"

    def __init__(self, ip: str, port: int, channel_count: int):
        super().__init__(ip, port, channel_count)
        self.broken_detect_thread = None

    def connect(self):
        super().connect()
        self.broken_detect_thread = threading.Thread(target=self.recive_loop, name=f"yba-ams-py({self.ip}) recive_loop")
        self.broken_detect_thread.start()
        self.ams_gc()

    def disconnect(self):
        super().disconnect()
        if self.broken_detect_thread:
            try:
                self.broken_detect_thread.join()
            except Exception as e:
                pass
            self.broken_detect_thread = None

    def recive_loop(self):
        while self.is_running:
            time.sleep(0.1)

            if self.sock is None:
                break

            try:
                r, _, _ = select.select([self.sock], [], [])
                do_read = bool(r)
            except socket.error:
                pass
            if do_read:
                try:
                    data = b''
                    while True:
                        if self.sock is None:
                            break
                        packet = self.sock.recv(1024)  # 一次接收1024字节
                        if not packet:
                            break
                        data += packet

                        latest = data[-1:]
                        if latest == b'\x04':
                            break

                    if len(data) != 0:
                        data = str(data[:-1], 'utf-8')
                        try:
                            json_obj = json.loads(data)
                            type = None
                            msg_data = None
                            if 'type' in json_obj:
                                type = json_obj['type']
                            if 'data' in json_obj:
                                msg_data = json_obj['data']

                            if type != None:
                                self.on_recv(type, msg_data)
                        except Exception as e:
                            pass

                except Exception as e:
                    LOGE(f"接收数据失败: {e}")
                    time.sleep(1)
                    pass

    def on_recv(self, type: int, data):

        if type == 0:
            LOGI(f'ESP Info : {data}')
        elif type == 1:
            LOGI(f'ESP Info: {data}')

    def ams_gc(self) -> str:
        self.send_ams(b'\x2f\x2f\xff\xfe\xff')

    def get_system_status(self) -> str:
        self.send_ams(b'\x2f\x2f\xff\xfe\xfe')

    def ams_sync(self):
        ams_sync = b'\x2f\x2f\xff\xfe\x02' + self.channel_total.to_bytes(1, 'big')

        for i in range(self.channel_total):
            ams_sync += self.ch_state[i].to_bytes(1, 'big')

        self.send_ams(ams_sync)

    def heartbeat(self):
        while self.is_running:
            if self.sock is not None:
                self.ams_sync()
            time.sleep(1)
