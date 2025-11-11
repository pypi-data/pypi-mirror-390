import os
import pathlib

from metripy.Application.Config.File.ConfigFileReaderInterface import (
    ConfigFileReaderInterface,
)
from metripy.Application.Config.File.JsonConfigFileReader import JsonConfigFileReader
from metripy.Application.Config.File.YamlConfigFileReader import YamlConfigFileReader


class ConfigFileReaderFactory:
    @staticmethod
    def createFromFileName(filename: str) -> ConfigFileReaderInterface:
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"File {filename} does not exist")

        extension = pathlib.Path(filename).suffix
        if extension == ".json":
            return JsonConfigFileReader(filename)
        elif extension == ".yaml" or extension == ".yml":
            return YamlConfigFileReader(filename)
        elif extension == ".xml":
            raise NotImplementedError("XML support is not implemented yet")
        else:
            raise NotImplementedError(f"Unsupported file type: {extension}")
