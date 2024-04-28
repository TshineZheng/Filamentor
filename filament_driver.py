from enum import Enum
from abc import ABC, abstractmethod

TOPIC = '/openams/filament_driver'

class DriverAction(Enum):
    """控制类型
    """
    PUSH = 1    # 送
    PULL = 2    # 退
    STOP = 0    # 停（也可以是松）
    
class FilamentDriver(ABC):
    """料架驱动基类，负责控制送料和退料
    """

    def control(self, action: DriverAction):
        """控制料架

        Args:
            action (DriverAction): 控制类型
        """
        if action == DriverAction.PUSH:
            self.push()
        elif action == DriverAction.PULL:
            self.pull()
        elif action == DriverAction.STOP:
            self.stop()

    @abstractmethod
    def push(self):
        pass

    @abstractmethod
    def pull(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    