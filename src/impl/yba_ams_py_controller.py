import time
from src.impl.yba_ams_controller import YBAAMSController
from src.utils.log import LOGI

ams_sync = b'\x2f\x2f\xff\xfe\x02\x04'

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
    
    def connect(self):
        super().connect()
        LOGI(f'ESP32 {self.ams_gc()}')

    def ams_gc(self) -> str:
        self.send_ams( b'\x2f\x2f\xff\xfe\xff')
        return self.get_str_result_from_ams()
        
    def get_system_status(self) -> str:
        self.send_ams(b'\x2f\x2f\xff\xfe\xfe')
        return self.get_str_result_from_ams()
    
    def get_str_result_from_ams(self)-> str:
        data = b''
        while True:
            packet = self.sock.recv(1024)  # 一次接收1024字节
            if not packet:
                break
            data += packet

            latest = data[-1:]
            if latest == b'\x04':
                break

        if len(data) != 0:
            data = str(data, 'utf-8')
            return data

        return ''
    
    def ams_sync(self):
        self.send_ams(ams_sync + bytes([self.ch_state[0],self.ch_state[1],self.ch_state[2],self.ch_state[3]]))

    def heartbeat(self):
        while self.is_running:
            if self.sock is not None:
                self.ams_sync()
            time.sleep(1)