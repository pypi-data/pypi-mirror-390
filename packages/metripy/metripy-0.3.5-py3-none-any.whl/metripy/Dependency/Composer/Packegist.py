import re

import requests
from packaging import version

from metripy.Dependency.Dependency import Dependency


class Packegist:
    def get_info(self, dependency: Dependency) -> Dependency | None:
        if "/" not in dependency.name:
            return None
        [user, name] = dependency.name.split("/", 2)
        uri = f"https://packagist.org/packages/{user}/{name}.json"

        x = requests.get(uri)
        d = x.json()

        package_info = d.get("package", None)
        if package_info is None:
            print(f"package of {dependency.name} has no package info")
            return dependency

        dependency.type = package_info["type"]
        dependency.description = package_info["description"]
        dependency.repository = package_info["repository"]
        dependency.github_stars = package_info["github_stars"]
        dependency.downloads_total = package_info["downloads"]["total"]
        dependency.downloads_monthly = package_info["downloads"]["monthly"]
        dependency.downloads_daily = package_info["downloads"]["daily"]

        latest = version.parse("0.0.0")
        versions = package_info["versions"]
        for ver_str, datas in versions.items():
            # Strip leading 'v' if present
            if ver_str.startswith("v"):
                ver_str = ver_str[1:]

            # Skip non-semver strings
            if not re.match(r"^[\d.]+$", ver_str):
                continue

            current_version = version.parse(ver_str)
            if current_version > latest:
                latest = current_version
                dependency.latest = ver_str
                dependency.license = datas.get("license", [])
                dependency.homepage = datas.get("homepage")
                dependency.zip = datas.get("dist", {}).get("url")

        if dependency.version == dependency.latest:
            dependency.status = "latest"
        else:
            dependency.status = "outdated"
        return dependency
