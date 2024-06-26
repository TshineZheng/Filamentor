from abc import abstractmethod

from src.base_unit import BaseUnit


class BrokenDetect(BaseUnit):
    def __init__(self):
        super().__init__()

    @staticmethod
    @abstractmethod
    def type_name() -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """保存配置
        """
        return {
            'safe_time': self.get_safe_time(),
        }

    @abstractmethod
    def start(self):
        super().start()

    @abstractmethod
    def stop(self):
        super().stop()

    @abstractmethod
    def is_filament_broken(self) -> bool:
        pass

    def get_safe_time(self) -> float:
        # 返回一个秒数，用于退料安全距离，默认为 0 s
        return 0
