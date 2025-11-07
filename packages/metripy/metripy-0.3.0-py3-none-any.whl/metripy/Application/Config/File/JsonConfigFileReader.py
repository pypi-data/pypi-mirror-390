import json
import os

from metripy.Application.Config.Config import Config
from metripy.Application.Config.File.ConfigFileReaderInterface import (
    ConfigFileReaderInterface,
)
from metripy.Application.Config.GitConfig import GitConfig
from metripy.Application.Config.ProjectConfig import ProjectConfig
from metripy.Application.Config.ReportConfig import ReportConfig


class JsonConfigFileReader(ConfigFileReaderInterface):
    def __init__(self, filename: str):
        self.filename = filename

    def read(self, config: Config) -> None:
        with open(self.filename, "r") as file:
            json_data = json.load(file)

        self.parse_json(json_data, config)

    def resolve_path(self, path: str) -> str:
        return os.path.join(os.path.dirname(self.filename), path)

    def parse_json(self, json_data: dict, config: Config) -> None:

        # configs
        if configs := json_data.get("configs"):
            for project_name, project_config in configs.items():
                project_config = self.parse_config_json(project_name, project_config)
                config.project_configs.append(project_config)

    def parse_config_json(self, project_name: str, json_data: dict) -> ProjectConfig:
        project_config = ProjectConfig(project_name)

        # extensions
        if base_path := json_data.get("base_path"):
            project_config.base_path = base_path

        # includes
        if includes := json_data.get("includes"):
            files = []
            # with config file, includes are relative to the config file
            for include in includes:
                include = self.resolve_path(include)
                files.append(include)

            project_config.includes = files

        # extensions
        if extensions := json_data.get("extensions"):
            project_config.extensions = extensions

        # excludes
        if excludes := json_data.get("excludes"):
            project_config.excludes = excludes

        # reports
        if reports := json_data.get("reports"):
            for report_type, path in reports.items():
                path = self.resolve_path(path)
                project_config.reports.append(ReportConfig(report_type, path))

        # git
        if git := json_data.get("git"):
            project_config.git = GitConfig()
            project_config.git.repo = project_config.base_path
            project_config.git.branch = git.get("branch", project_config.git.branch)

        # composer
        if composer := json_data.get("composer"):
            project_config.composer = composer

        # pip
        if pip := json_data.get("pip"):
            project_config.pip = pip

        # npm
        if npm := json_data.get("npm"):
            project_config.npm = npm

        # trends
        if history_path := json_data.get("trends"):
            project_config.history_path = self.resolve_path(history_path)

        return project_config
