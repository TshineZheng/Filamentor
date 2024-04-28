from abc import ABC, abstractmethod

class FilamentBrokenDetect(ABC):
    def __init__(self):
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

    def safeTime(self) -> float:
        # 返回一个秒数，用于退料安全距离，默认为 0 s
        return 0