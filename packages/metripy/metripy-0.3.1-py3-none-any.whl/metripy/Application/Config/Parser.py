import re

from metripy.Application.Config.Config import Config
from metripy.Application.Config.File.ConfigFileReaderFactory import (
    ConfigFileReaderFactory,
)


class Parser:
    def parse(self, argv: list[str]) -> Config:
        config = Config()

        if argv[0].endswith("metripy.py") or argv[0].endswith("metripy"):
            argv.pop(0)

        # check for a config file
        key = 0
        while key < len(argv):
            arg = argv[key]
            if matches := re.search(r"^--config=(.+)$", arg):
                fileReader = ConfigFileReaderFactory.createFromFileName(
                    matches.group(1)
                )
                fileReader.read(config)
                argv.pop(key)

            # arguments with options
            elif matches := re.search(r"^--([\w]+(?:\.[\w]+)*)=(.*)$", arg):
                param = matches.group(1)
                value = matches.group(2)
                config.set(param, value)
                argv.pop(key)

            # arguments without options
            elif matches := re.search(r"^--([\w]+(?:\.[\w]+)*)$", arg):
                param = matches.group(1)
                config.set(param, True)
                argv.pop(key)
            else:
                key += 1

        # TODO handle remaining arguments

        return config
