from importlib.metadata import metadata, version

import toml


class Info:
    def __init__(self):
        self.version = self._get_version()
        self.url = self._get_homepage_url()

    def _get_pyproject_data(self) -> dict:
        with open("pyproject.toml", "r") as file:
            data = toml.load(file)
        return data

    def _get_version(self) -> str:
        """Get version from installed package metadata"""
        try:
            return version("metripy")
        except Exception:
            # Fallback for development if not installed
            return self._get_pyproject_data()["project"]["version"]

    def _get_homepage_url(self) -> str:
        """Get homepage URL from installed package metadata"""
        try:
            meta = metadata("metripy")
            # Try to get Home-Page from metadata
            homepage = meta.get("Home-Page")
            if not homepage:
                # Try Project-URL field
                for line in meta.get_all("Project-URL") or []:
                    if line.startswith("Homepage"):
                        homepage = line.split(",", 1)[1].strip()
                        break
            return homepage or "no homepage found"
        except Exception:
            # Fallback
            return self._get_pyproject_data()["project"]["urls"]["Homepage"]

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
