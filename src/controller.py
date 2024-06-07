from abc import  abstractmethod
from enum import Enum
from typing import List

from src.base_unit import BaseUnit
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
    def get_channel_states(self)->List[int]:
        """获取通道状态

        Returns:
            List[int]: 通道状态
        """
        pass
