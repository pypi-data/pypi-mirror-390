import os

import toml

from metripy.Dependency.Dependency import Dependency
from metripy.Dependency.Pip.PyPi import PyPi


class Pip:
    def get_dependencies(self, path: str) -> list[Dependency]:
        try:
            requirements = self.get_from_requirements_txt(path)
        except FileNotFoundError:
            requirements = self.get_from_pyproject_toml(path)

        pypi = PyPi()
        packages = []
        for dependency in requirements:
            package = pypi.get_info(dependency)
            packages.append(package)

        return [item for item in packages if item is not None]

    def get_from_requirements_txt(self, path: str) -> list[Dependency]:
        with open(os.path.join(path, "requirements.txt"), "r") as file:
            lines = file.readlines()
            return self._parse_dependencies(lines)

        return []

    def get_from_pyproject_toml(self, path: str) -> list[Dependency]:
        with open(os.path.join(path, "pyproject.toml"), "r") as f:
            data = toml.load(f)

            # For PEP 621 / setuptools projects
            if "project" in data:
                deps = data["project"].get("dependencies", [])
                return self._parse_dependencies(deps)

        return []

    def _parse_dependencies(self, lines: list[str]) -> list[Dependency]:
        dependencies = []
        for dep in lines:
            dep = dep.strip()
            if not dep or dep.startswith("#"):
                continue
            # dep is a string like "requests>=2.32.5"
            if "==" in dep:
                name, version = dep.split("==")
            elif ">=" in dep:
                name, version = dep.split(">=")
            else:
                name, version = dep, None
            dependencies.append(
                Dependency(name.strip(), version.strip() if version else None)
            )

        return dependencies
