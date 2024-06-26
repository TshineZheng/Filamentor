from src.impl.yba_ams_py_controller import YBAAMSPYController

ams_head = b'\x2f\x2f\xff\xfe\x01\x02'


class YBASingleBufferController(YBAAMSPYController):
    @staticmethod
    def type_name() -> str:
        return "yba_ams_single_buffer"

    def ams_control(self, ch, fx):
        self.send_ams(ams_head + bytes([ch]) + bytes([fx]))
        for i in range(4):
            self.ch_state[i] = 0

        self.ch_state[ch] = fx
