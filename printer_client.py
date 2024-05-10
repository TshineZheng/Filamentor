from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable

from broken_detect import BrokenDetect


class Action(Enum):
    CHANGE_FILAMENT = 0  # 更换通道
    FILAMENT_SWITCH_0 = 1  # 卸载完成
    FILAMENT_SWITCH_1 = 2  # 装载完成
    PREPARE = 3  # 准备开始
    FINISH = 4  # 打印完成
    FAILED = 5  # 打印失败
    FIRST_FILAMENT = 6  # 第一次颜色


class FilamentState(Enum):
    NO = 0  # 无料
    YES = 1  # 有料
    UNKNOWN = 2  # 未知


class PrinterClient(ABC):
    def __init__(self):
        self.filament_state = FilamentState.UNKNOWN
        # action 回调列表
        self.action_callbacks: list[Callable[[Action, Any], None]] = []

    @staticmethod
    @abstractmethod
    def type_name() -> str:
        pass

    def add_on_action(self, callback: Callable[[Action, Any], None]):
        self.action_callbacks.append(callback)

    def remove_on_action(self, callback: Callable[[Action, Any], None]):
        self.action_callbacks.remove(callback)

    def on_action(self, action: Action, data: Any):
        for callback in self.action_callbacks:
            callback(action, data)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def on_unload(self, pre_tem: int = 255):
        """卸载时回调

        Args:
            pre_tem (int, optional): 可用于卸载时提前升温，加快换色速度. Defaults to 255.
        """
        pass

    @abstractmethod
    def change_filament(self, next_fila: int):
        """主动调用换色

        Args:
            next_fila (int): 下一个颜色通道序号
        """
        pass

    @abstractmethod
    def refresh_status(self):
        pass

    @abstractmethod
    def filament_broken_detect(self) -> BrokenDetect:
        """返回打印自己的断料检测器

        Returns:
            BrokenDetect: 检测器对象
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """保存配置
        """
        pass

    def get_filament_state(self) -> FilamentState:
        return self.filament_state

    def set_filament_state(self, state: FilamentState):
        self.filament_state = state
