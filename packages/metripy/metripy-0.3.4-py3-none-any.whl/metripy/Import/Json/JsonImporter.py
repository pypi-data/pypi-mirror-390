import json

from metripy.Component.Output.CliOutput import CliOutput
from metripy.Metric.ProjectMetrics import ProjectMetrics


class JsonImporter:
    def __init__(self, output: CliOutput):
        self.output = output

    def import_data(self, path: str) -> ProjectMetrics:
        self.output.writeln(f"<info>Importing data from {path}...</info>")
        with open(path, "r") as file:
            data = json.load(file)
            project_metrics = ProjectMetrics.from_dict(data)
        self.output.writeln("<success>Data imported successfuly</success>")
        return project_metrics
