from abc import abstractmethod
from enum import Enum
from typing import Any, Callable
from src.base_unit import BaseUnit
from src.broken_detect import BrokenDetect


class Action(Enum):
    CHANGE_FILAMENT = 0  # 更换通道
    FILAMENT_SWITCH = 1  # 打印机断料检测器状态改变
    TASK_START = 2  # 接到任务
    TASK_PREPARE = 3  # 准备开始
    TASK_FINISH = 4  # 打印完成
    TASK_FAILED = 5  # 打印失败


class FilamentState(Enum):
    NO = 0  # 无料
    YES = 1  # 有料
    UNKNOWN = 2  # 未知


class PrinterClient(BaseUnit):
    def __init__(self):
        super().__init__()
        # action 回调列表
        self.action_callbacks: list[Callable[[Action, Any], None]] = []

    @staticmethod
    @abstractmethod
    def type_name() -> str:
        """打印机类型

        Returns:
            str: 返回打印机的类型
        """
        pass

    @abstractmethod
    def start(self):
        """启动打印机连接
        """
        super().start()

    @abstractmethod
    def stop(self):
        """关闭打印机连接
        """
        super().stop()

    @abstractmethod
    def resume(self):
        """打印机恢复打印，主要用于暂停换料后
        """
        pass

    @abstractmethod
    def on_unload(self, pre_tem: int = 255):
        """卸载时回调

        Args:
            pre_tem (int, optional): 可用于卸载时提前升温，加快换色速度. Defaults to 255.
        """
        pass

    @abstractmethod
    def change_filament(self, ams, next_fila: int, change_temp: int = 255):
        """打印机退料

        Args:
            ams (AMSCore): ams控制，在打印机退料时，可能需要控制ams动作，比如说回抽，送料等等
            next_fila (int): 下一个通道
            change_temp (int, optional): 换色温度. Defaults to 255.
        """
        pass

    @abstractmethod
    def refresh_status(self):
        """刷新打印机状态，通过 on action 回调数据
        """
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
        """输出打印机的相关配置
        """
        pass

    def add_on_action(self, callback: Callable[[Action, Any], None]):
        """增加 on action 回调

        Args:
            callback (Callable[[Action, Any], None]): 回调函数
        """
        self.action_callbacks.append(callback)

    def remove_on_action(self, callback: Callable[[Action, Any], None]):
        """移除 on action 回调

        Args:
            callback (Callable[[Action, Any], None]): 回调函数
        """
        if callback in self.action_callbacks:
            self.action_callbacks.remove(callback)

    def on_action(self, action: Action, data: Any = None):
        """回调派发, 打印机的信息派发给所有订阅的回调

        Args:
            action (Action): 动作
            data (Any, optional): 动作数据. Defaults to None.
        """
        for callback in self.action_callbacks:
            callback(action, data)
