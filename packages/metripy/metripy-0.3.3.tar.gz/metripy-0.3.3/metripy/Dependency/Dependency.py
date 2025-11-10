from typing import Self


class Dependency:
    def __init__(self, name: str, version: str | None):
        self.name = name
        self.version = version
        self.latest: str = ""
        self.status: str = "unknown"
        self.type: str = ""
        self.description: str = ""
        self.repository: str = ""
        self.github_stars: int = 0
        self.downloads_total: int = 0
        self.downloads_monthly: int = 0
        self.downloads_daily: int = 0
        self.license: list[str] = []
        self.homepage: str = ""
        self.zip: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "latest": self.latest,
            "status": self.status,
            "type": self.type,
            "description": self.description,
            "repository": self.repository,
            "github_stars": self.github_stars,
            "downloads_monthly": self.downloads_monthly,
            "licenses": ",".join(self.license),
        }

    @staticmethod
    def get_lisence_distribution(dependencies: list[Self]) -> dict[str, int]:
        license_by_type = {}

        dependency: Dependency
        for dependency in dependencies:
            for license_name in dependency.license:
                if license_name not in license_by_type.keys():
                    license_by_type[license_name] = 0
                license_by_type[license_name] += 1

        return license_by_type
