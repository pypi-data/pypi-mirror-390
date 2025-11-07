from abc import ABC, abstractmethod

from metripy.Application.Config.Config import Config


class ConfigFileReaderInterface(ABC):

    @abstractmethod
    def __init__(self, filename: str):
        pass

    @abstractmethod
    def read(self, config: Config) -> None:
        pass
