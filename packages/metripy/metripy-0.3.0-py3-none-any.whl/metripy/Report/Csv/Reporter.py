from metripy.Application.Config.Config import Config
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Metric.ProjectMetrics import ProjectMetrics


class Reporter:
    def __init__(self, config: Config, output: CliOutput):
        self.config = config
        self.output = output

    def generate(self, metrics: ProjectMetrics):
        raise NotImplementedError("CSV metrics report is not yet implemented")
