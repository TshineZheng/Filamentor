from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable


class Action(Enum):
    CHANGE_FILAMENT = 0     # 更换通道
    FILAMENT_SWITCH_0 = 1   # 卸载完成
    FILAMENT_SWITCH_1 = 2   # 装载完成

class FilamentState(Enum):
    NO = 0  # 无料
    YES = 1  # 有料
    UNKNOWN = 2 # 未知

class PrinterClient(ABC):
    def __init__(self, on_action: Callable[[Action, Any], None]):
        self.on_action = on_action
        self.filament_state = FilamentState.UNKNOWN

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
    def refresh_status(self):
        pass
    
    def get_filament_state(self)->FilamentState:
        return self.filament_state
    
    def set_filament_state(self, state:FilamentState):
        self.filament_state = state

