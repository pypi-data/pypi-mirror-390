import json

from metripy.Application.Config.Config import Config
from metripy.Application.Config.File.ConfigFileReaderInterface import (
    ConfigFileReaderInterface,
)


class JsonConfigFileReader(ConfigFileReaderInterface):
    def __init__(self, filename: str):
        super().__init__(filename)

    def read(self, config: Config) -> None:
        with open(self.filename, "r") as file:
            json_data = json.load(file)

        self.parse_data(json_data, config)
