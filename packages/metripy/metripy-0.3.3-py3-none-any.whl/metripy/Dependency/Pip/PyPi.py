import requests

from metripy.Dependency.Dependency import Dependency


class PyPi:
    def get_info(self, dependency: Dependency) -> Dependency | None:
        uri = f"https://pypi.org/pypi/{dependency.name}/json"
        x = requests.get(uri)
        data = x.json()

        info = data.get("info", {})
        releases = data.get("releases", {})

        if not info:
            print(f"Package '{dependency.name}' has no info section")
            return dependency

        dependency.type = "pip"
        dependency.description = info.get("summary")
        dependency.repository = info.get("project_url") or info.get("home_page")
        if info.get("license"):
            dependency.license = [info.get("license")]
        else:
            dependency.license = []
        dependency.homepage = info.get("home_page")

        # PyPI doesn't provide GitHub stars or download counts directly
        dependency.github_stars = "??"
        dependency.downloads_total = "??"
        dependency.downloads_monthly = "??"
        dependency.downloads_daily = "??"

        # Determine latest version
        latest_version = info.get("version")
        dependency.latest = latest_version

        # Compare with current version
        if dependency.version == latest_version:
            dependency.status = "latest"
        else:
            dependency.status = "outdated"

        # Get distribution URL (e.g., wheel or sdist)
        if latest_version in releases:
            release_files = releases[latest_version]
            if release_files:
                dependency.zip = release_files[0].get("url")

        return dependency
