from metripy.Application.Config.Config import Config
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Json.AbstractJsonReporter import AbstractJsonReporter


class JsonReporter(AbstractJsonReporter):
    def __init__(self, config: Config, output: CliOutput):
        self.config = config
        self.output = output

    def generate(self, metrics: ProjectMetrics):
        self.put_data(metrics.to_dict())
        self.output.writeln(
            f"<success>Create json report in {self.config.path}</success>"
        )
