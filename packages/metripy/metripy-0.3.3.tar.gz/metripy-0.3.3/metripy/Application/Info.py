import toml


class Info:
    def __init__(self):
        data = self._get_data()
        self.version = data["project"]["version"]
        self.url = data["project"]["urls"]["Homepage"]

    def _get_data(self) -> dict:
        with open("pyproject.toml", "r") as file:
            data = toml.load(file)
        return data

    def get_version(self) -> str:
        return self.version

    def get_version_info(self) -> str:
        return f"""
Metripy {self.get_version()}
{self.url}
"""

    def get_help(self) -> str:
        return (
            self.get_version_info()
            + """
Usage: metripy [options]
Options:
 --config=<file>    Use a custom config file
 --version            Show the version and exit
 --help               Show this help message and exit
 --debug              Enable debug mode
 --quiet              Disable output
"""
        )
