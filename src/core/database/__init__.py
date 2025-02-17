from abc import ABC, abstractmethod


class BaseConection(ABC):
    @abstractmethod
    def connect(self):
        pass