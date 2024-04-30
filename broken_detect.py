from abc import ABC, abstractmethod


class BrokenDetect(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def type_name() -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """保存配置
        """
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def is_filament_broken(self) -> bool:
        pass

    def safe_time(self) -> float:
        # 返回一个秒数，用于退料安全距离，默认为 0 s
        return 0
