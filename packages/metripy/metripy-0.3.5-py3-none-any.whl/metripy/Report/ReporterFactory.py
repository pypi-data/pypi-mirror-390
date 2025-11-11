from metripy.Application.Config.ReportConfig import ReportConfig
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Report import ReporterInterface
from metripy.Report.Html.Reporter import Reporter as HtmlReporter
from metripy.Report.Json.GitJsonReporter import GitJsonReporter
from metripy.Report.Json.JsonReporter import JsonReporter


class ReporterFactory:
    @staticmethod
    def create(
        config: ReportConfig, output: CliOutput, project_name: str
    ) -> ReporterInterface:
        if config.type == "html":
            return HtmlReporter(config, output, project_name)
        elif config.type == "json":
            return JsonReporter(config, output)
        elif config.type == "csv":
            raise NotImplementedError
        elif config.type == "cli":
            raise NotImplementedError
        elif config.type == "json-git":
            return GitJsonReporter(config, output)
        else:
            raise ValueError(f"Unsupported report type: {config.type}")
