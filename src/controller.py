from abc import abstractmethod
from enum import Enum
from typing import List

from src.base_unit import BaseUnit
from src.broken_detect import BrokenDetect
from src.utils.log import LOGE


class ChannelAction(Enum):
    """控制类型
    """
    PUSH = 1  # 送
    PULL = 2  # 退
    STOP = 0  # 停（也可以是松）


class Controller(BaseUnit):
    """料架控制器
    """

    @staticmethod
    def generate_controller(type: str, info: dict) -> 'Controller':
        """生成控制器

        Args:
            type (str): 控制器类型
            info (dict): 控制器信息

        Returns:
            Controller: 返回控制器
        Exceptions:
            ControllerInfoError: 控制器信息错误

            ControllerTypeNotMatch: 控制器类型不支持
        """
        from src.web.controller.exceptions import ControllerInfoError, ControllerTypeNotMatch
        from src.impl.yba_ams_controller import YBAAMSController
        from src.impl.yba_ams_py_controller import YBAAMSPYController
        from src.impl.yba_ams_servo_controller import YBAAMSServoController
        from src.impl.yba_single_buffer_controller import YBASingleBufferController
        try:
            if type == YBAAMSController.type_name():
                return YBAAMSController.from_dict(info)
            elif type == YBAAMSPYController.type_name():
                return YBAAMSPYController.from_dict(info)
            elif type == YBAAMSServoController.type_name():
                return YBAAMSServoController.from_dict(info)
            elif type == YBASingleBufferController.type_name():
                return YBASingleBufferController.from_dict(info)
        except:
            raise ControllerInfoError()

        raise ControllerTypeNotMatch()

    @staticmethod
    @abstractmethod
    def type_name() -> str:
        pass

    def __init__(self, channel_total: int):
        """构造

        Args:
            channel_total (int): 通道数量
        """
        self.channel_total = channel_total
        super().__init__()

    @abstractmethod
    def start(self):
        """启动控制器
        """
        super().start()

    @abstractmethod
    def stop(self):
        """停止控制器
        """
        super().stop()

    @abstractmethod
    def control(self, channel_index: int, action: ChannelAction) -> bool:
        """控制通道

        Args:
            channel_index (int): 通道序号,  0 <= channel_index < channel_count
            action (ChannelAction): 控制类型
        """
        if channel_index < 0 or channel_index >= self.channel_total:
            LOGE(f'通道序号 {channel_index} 超出范围')
            return False

        return True

    @abstractmethod
    def to_dict(self) -> dict:
        """保存配置
        """
        pass

    @abstractmethod
    def is_initiative_push(self, channel_index: int) -> bool:
        """是否主动送料

        Returns:
            bool: 是否主动送料
        """
        pass

    @abstractmethod
    def get_channel_states(self) -> List[int]:
        """获取通道状态

        Returns:
            List[int]: 通道状态
        """
        pass

    def get_broken_detect(self) -> 'BrokenDetect':
        return None
