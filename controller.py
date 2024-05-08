from abc import ABC, abstractmethod
from enum import Enum


class ChannelAction(Enum):
    """控制类型
    """
    PUSH = 1  # 送
    PULL = 2  # 退
    STOP = 0  # 停（也可以是松）


class Controller(ABC):
    """料架控制器
    """

    @staticmethod
    @abstractmethod
    def type_name() -> str:
        pass

    def __init__(self, channel_count: int):
        """构造

        Args:
            channel_count (int): 通道数量
        """
        self.channel_count = channel_count
        self.is_running = False

    @abstractmethod
    def start(self):
        """启动控制器
        """
        self.is_running = True

    @abstractmethod
    def stop(self):
        """停止控制器
        """
        self.is_running = False

    @abstractmethod
    def control(self, channel_index: int, action: ChannelAction) -> bool:
        """控制通道

        Args:
            channel_index (int): 通道序号,  0 <= channel_index < channel_count
            action (ChannelAction): 控制类型
        """
        pass

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
