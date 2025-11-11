import os

from metripy.Application.Config.ProjectConfig import ProjectConfig


class Finder:
    def fetch(self, project_configs: list[ProjectConfig]) -> dict[str, list[str]]:
        """returns a list of files per project project_name => [files,...]"""
        project_files = {}
        for project_config in project_configs:
            files = []

            paths = [
                os.path.join(project_config.base_path, inc)
                for inc in project_config.includes
            ]
            for path in paths:
                if os.path.isdir(path):
                    self._search(
                        path, project_config.extensions, project_config.excludes, files
                    )
                elif path not in project_config.excludes and path.endswith(
                    tuple(project_config.extensions)
                ):
                    files.append(path)
            project_files[project_config.name] = files

        return project_files

    def _search(
        self, path: str, extensions: list[str], excludes: list[str], results: list[str]
    ):
        if not os.path.isdir(path):
            if path not in excludes and path.endswith(tuple(extensions)):
                results.append(path)

        for file in os.listdir(path):
            if os.path.isdir(os.path.join(path, file)) and file not in excludes:
                self._search(os.path.join(path, file), extensions, excludes, results)
            elif file not in excludes and file.endswith(tuple(extensions)):
                results.append(os.path.join(path, file))
