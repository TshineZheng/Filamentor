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