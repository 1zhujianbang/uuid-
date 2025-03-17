from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    @abstractmethod
    def process_file(self):
        pass