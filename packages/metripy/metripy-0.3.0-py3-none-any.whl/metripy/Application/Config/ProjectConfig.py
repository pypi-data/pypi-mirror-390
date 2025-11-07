from metripy.Application.Config.GitConfig import GitConfig
from metripy.Application.Config.ReportConfig import ReportConfig


class ProjectConfig:
    def __init__(self, name: str):
        self.name: str = name
        self.base_path: str = "./"
        self.includes: list[str] = []
        self.excludes: list[str] = []
        self.extensions: list[str] = []
        self.git: GitConfig | None = None
        self.composer: bool = False
        self.pip: bool = False
        self.npm: bool = False
        self.reports: list[ReportConfig] = []
        self.history_path: str | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "base_path": self.base_path,
            "includes": self.includes,
            "excludes": self.excludes,
            "extensions": self.extensions,
            "composer": self.composer,
            "pip": self.pip,
            "npm": self.npm,
            "git": self.git.to_dict() if self.git else None,
            "reports": [report.to_dict() for report in self.reports],
            "history_path": self.history_path,
        }

    @staticmethod
    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "yes")

    def set(self, keys: list[str], value: any) -> None:
        if len(keys) == 0:
            return
        primary_key = keys[0]
        print(f"Setting primary {primary_key} to {value}")
        # single value
        if primary_key == "base_path":
            self.base_path = value
        elif primary_key == "pip":
            self.pip = self.str_to_bool(value)
        elif primary_key == "npm":
            self.npm = self.str_to_bool(value)
        elif primary_key == "composer":
            self.composer = self.str_to_bool(value)
        elif primary_key == "trends":
            self.history_path = value
        elif primary_key == "git":
            self.git = GitConfig()
            self.git.repo = self.base_path
            self.git.branch = value

        # list values
        elif primary_key == "includes":
            if value == "":
                self.includes = []
            else:
                self.includes.append(value)
        elif primary_key == "excludes":
            if value == "":
                self.excludes = []
            else:
                self.excludes.append(value)
        elif primary_key == "extensions":
            if value == "":
                self.extensions = []
            else:
                self.extensions.append(value)

        # dict values
        elif primary_key == "reports":
            if len(keys) == 1:
                return
            report_type = keys[1]
            report_path = value
            if value != "":
                self.reports.append(ReportConfig(report_type, report_path))
            else:
                report_config = next((rc for rc in self.reports if rc.type == report_type), None)
                if not report_config:
                    return
                self.reports.remove(report_config)