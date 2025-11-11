from metripy.Application.Config.ProjectConfig import ProjectConfig


class Config:
    def __init__(self):
        self.project_configs: list[ProjectConfig] = []
        self.quiet: bool = False
        self.version: bool = False
        self.help: bool = False
        self.debug: bool = False

    def to_dict(self) -> dict:
        return {
            "project_configs": [
                project_config.to_dict() for project_config in self.project_configs
            ],
        }

    def set(self, param: str, value: any) -> None:
        if param == "quiet":
            self.quiet = value
        elif param == "version":
            self.version = value
        elif param == "help":
            self.help = value
        elif param == "debug":
            self.debug = value
        elif param.startswith("configs."):
            self._set_project_value(param[len("configs.") :], value)
        else:
            # ignore unknown parameters
            return

    def _set_project_value(self, param: str, value: any) -> None:
        keys = param.split(".")
        project_name = keys[0]
        project_config = next(
            (pc for pc in self.project_configs if pc.name == project_name), None
        )
        if not project_config:
            project_config = ProjectConfig(project_name)
            self.project_configs.append(project_config)
        if len(keys) > 1:
            project_config.set(keys[1:], value)
        else:
            # weird but okay
            return
