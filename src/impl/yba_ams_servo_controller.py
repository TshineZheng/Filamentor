from src.impl.yba_ams_py_controller import YBAAMSPYController


class YBAAMSServoController(YBAAMSPYController):
    @staticmethod
    def type_name() -> str:
        return "yba_ams_servo"
    
    def is_initiative_push(self, channel_index: int) -> bool:
        return False