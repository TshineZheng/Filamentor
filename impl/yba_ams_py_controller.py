from impl.yba_ams_controller import YBAAMSController
from utils.log import LOGI


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
        ams_mem = b'\x2f\x2f\xff\xfe\xff'
        self.send_ams(ams_mem)
        data = self.sock.recv(1024)
        if len(data) != 0:
            data = str(data, 'utf-8')
            LOGI(data)