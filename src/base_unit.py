from abc import ABC, abstractmethod


class BaseUnit(ABC):
    def __init__(self):
        self.is_running = False

    @abstractmethod
    def start(self):
        self.is_running = True

    @abstractmethod
    def stop(self):
        self.is_running = False

    def get_sync_info(self) -> dict:
        """同步时返回的信息

        Returns:
            dict: 同步内容
        """
        return {}
