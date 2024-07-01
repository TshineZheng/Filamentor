from src.broken_detect import BrokenDetect
from src.impl.yba_ams_py_controller import YBAAMSPYController
from src.utils.log import LOGI

ams_head = b'\x2f\x2f\xff\xfe\x01\x02'


class YBASingleBufferController(YBAAMSPYController):

    @staticmethod
    def type_name() -> str:
        return "yba_ams_single_buffer"

    def __init__(self, ip: str, port: int, channel_count: int, safe_time: int):
        super().__init__(ip, port, channel_count)
        self.fila_broken_safe_time = safe_time
        self.fbd = YBABrokenDetect(self)
        self.is_fila_broken = False

    def ams_control(self, ch, fx):
        for i in range(self.channel_total):
            self.ch_state[i] = 0

        self.ch_state[ch] = fx
        self.send_ams(ams_head + bytes([ch]) + bytes([fx]))

    def on_recv(self, type: int, data):
        super().on_recv(type, data)

        if type == 2:
            self.is_fila_broken = data == '0'

    def get_broken_detect(self) -> BrokenDetect:
        if self.fila_broken_safe_time <= 0:
            return None
        return self.fbd

    def connect(self):
        super().connect()
        self.send_ams(b'\x2f\x2f\xff\xfe\xfd')

    def to_dict(self) -> dict:
        d = super().to_dict()
        d['fila_broken_safe_time'] = self.fila_broken_safe_time
        return d

    @classmethod
    def from_dict(cls, json_data: dict):
        return cls(
            json_data["ip"],
            json_data["port"],
            json_data["channel_total"],
            json_data["fila_broken_safe_time"]
        )


class YBABrokenDetect(BrokenDetect):

    def __init__(self, parent: YBASingleBufferController):
        super().__init__()
        self.parent = parent

    @staticmethod
    def type_name() -> str:
        return 'yba_ams_single_buffer_broken_detect'

    def get_safe_time(self) -> int:
        return self.parent.fila_broken_safe_time

    def is_filament_broken(self) -> bool:
        return self.parent.is_fila_broken

    def to_dict(self) -> dict:
        return super().to_dict()

    def start(self):
        pass

    def stop(self):
        pass
