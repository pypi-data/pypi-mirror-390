import json
import os

from metripy.Dependency.Composer.Packegist import Packegist
from metripy.Dependency.Dependency import Dependency


class Composer:
    def get_composer_dependencies(self, composer_json_path: str):
        requirements = self.get_composer_json_requirements(composer_json_path)

        packegist = Packegist()
        packages = []
        for dependency in requirements:
            package = packegist.get_info(dependency)
            packages.append(package)

        return [item for item in packages if item is not None]

    def get_composer_json_requirements(self, composer_json_path) -> list:
        requirements = []
        with open(os.path.join(composer_json_path, "composer.json"), "r") as file:
            composer_json = json.load(file)
            require = composer_json.get("require", None)
            if require is None:
                return []
            for name, version in require.items():
                requirements.append(Dependency(name, version))

        return requirements
