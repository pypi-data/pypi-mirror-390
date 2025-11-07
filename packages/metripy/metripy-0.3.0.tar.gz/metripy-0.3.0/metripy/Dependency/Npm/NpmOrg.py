import requests

from metripy.Dependency.Dependency import Dependency


class NpmOrg:
    def get_info(self, dependency: Dependency) -> Dependency | None:
        if not dependency.name:
            return None

        uri = f"https://registry.npmjs.org/{dependency.name}"
        response = requests.get(uri)

        if response.status_code != 200:
            print(f"Package {dependency.name} not found on npm.org")
            return None

        data = response.json()

        # Basic metadata
        dependency.type = "npm"
        dependency.description = data.get("description", "")
        dependency.repository = data.get("repository", {}).get("url", "")
        dependency.homepage = data.get("homepage", "")
        dependency.license = [data.get("license")] if data.get("license") else []

        # Version info
        latest_version = data.get("dist-tags", {}).get("latest", "")
        dependency.latest = latest_version

        # npm doesn't provide download stats in the registry API
        dependency.github_stars = "??"
        dependency.downloads_total = "??"
        dependency.downloads_monthly = "??"
        dependency.downloads_daily = "??"

        # Determine status
        if dependency.version == dependency.latest:
            dependency.status = "latest"
        else:
            dependency.status = "outdated"

        # build zip url
        if latest_version:
            dependency.zip = f"https://registry.npmjs.org/{dependency.name}/-/{dependency.name}-{latest_version}.tgz"

        return dependency
