import json
import os

from metripy.Dependency.Dependency import Dependency
from metripy.Dependency.Npm.NpmOrg import NpmOrg


class Npm:
    def get_dependencies(self, path: str) -> list[Dependency]:
        requirements = self._get_requirements(path)

        npm_org = NpmOrg()
        packages = []
        for dependency in requirements:
            package = npm_org.get_info(dependency)
            packages.append(package)

        return [item for item in packages if item is not None]

    def _get_requirements(self, path: str) -> list[Dependency]:
        requirements = []
        with open(os.path.join(path, "package.json"), "r") as file:
            package_json = json.load(file)
            dependencies = package_json.get("dependencies", None)
            if dependencies is None:
                return None
            for name, version in dependencies.items():
                requirements.append(Dependency(name, version))

        return requirements
