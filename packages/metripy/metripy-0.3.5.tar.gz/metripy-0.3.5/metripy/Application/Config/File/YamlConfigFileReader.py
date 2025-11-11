import yaml

from metripy.Application.Config.Config import Config
from metripy.Application.Config.File.ConfigFileReaderInterface import (
    ConfigFileReaderInterface,
)


class YamlConfigFileReader(ConfigFileReaderInterface):
    def __init__(self, filename: str):
        super().__init__(filename)

    def read(self, config: Config) -> None:
        with open(self.filename, "r") as file:
            yaml_data = yaml.safe_load(file)

        self.parse_data(yaml_data, config)
