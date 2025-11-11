from abc import ABC, abstractmethod

from metripy.Application.Config.ReportConfig import ReportConfig
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Metric.ProjectMetrics import ProjectMetrics


class ReporterInterface(ABC):
    def __init__(
        self, config: ReportConfig, output: CliOutput, project_name: str = "foobar"
    ):
        self.config: ReportConfig = config
        self.output = output

    @abstractmethod
    def generate(self, metrics: ProjectMetrics) -> None:
        raise NotImplementedError()
