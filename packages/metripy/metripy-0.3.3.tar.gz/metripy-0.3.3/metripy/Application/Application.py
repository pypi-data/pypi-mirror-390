import json

from metripy.Application.Analyzer import Analyzer
from metripy.Application.Config.Parser import Parser
from metripy.Application.Info import Info
from metripy.Component.Debug.Debugger import Debugger
from metripy.Component.File.Finder import Finder
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Report.ReporterFactory import ReporterFactory
from metripy.Report.ReporterInterface import ReporterInterface


class Application:
    def run(self, argv) -> None:
        output = CliOutput()

        # issues and debug
        debugger = Debugger(output)

        config = Parser().parse(argv)
        if config.debug:
            debugger.enable()

        if config.version:
            output.writeln(Info().get_version_info())
            return

        if config.help:
            output.writeln(Info().get_help())
            return

        if config.quiet:
            output.set_quiet(True)

        finder = Finder()
        files = finder.fetch(config.project_configs)

        for project_config in config.project_configs:
            debugger.debug(project_config.name)
            project_files = files[project_config.name]
            debugger.debug(f"Found {len(project_files)} files")
            debugger.debug(json.dumps(project_files))

            output.writeln(f"<info>Analying Project {project_config.name}...</info>")
            project_metrics = Analyzer(project_config, output, debugger).run(
                project_files
            )
            output.writeln(
                f"<success>Done analying Project {project_config.name}</success>"
            )

            if not project_config.reports:
                output.writeln(
                    f"<success>Skipping reports of {project_config.name}!</success>"
                )
                continue

            output.writeln(
                f"<info>Generating reports for {project_config.name}...</info>"
            )
            for report_config in project_config.reports:
                reporter: ReporterInterface = ReporterFactory.create(
                    report_config, output, project_config.name
                )
                reporter.generate(project_metrics)
            output.writeln(
                f"<success>Reports generated for {project_config.name}</success>"
            )
