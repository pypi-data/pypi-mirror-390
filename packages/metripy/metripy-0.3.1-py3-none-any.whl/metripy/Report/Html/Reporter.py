import os
import shutil
from datetime import datetime


from metripy.Application.Config.ReportConfig import ReportConfig
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRendererFactory import PageRendererFactory
from metripy.Report.ReporterInterface import ReporterInterface


class Reporter(ReporterInterface):
    def __init__(
        self, config: ReportConfig, output: CliOutput, project_name: str = "foobar"
    ):
        self.config: ReportConfig = config
        self.output = output
        self.template_dir = os.path.join(os.getcwd(), "templates/html_report")
        self.project_name = project_name

        self.page_renderer_factory = PageRendererFactory(
            self.template_dir, self.config.path, self.project_name
        )

        self.global_template_args = {
            "project_name": project_name,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def generate(self, metrics: ProjectMetrics):

        self.output.writeln("<info>Generating HTML report...</info>")

        # copy sources
        if not os.path.exists(os.path.join(self.config.path, "js")):
            os.makedirs(os.path.join(self.config.path, "js"))
        if not os.path.exists(os.path.join(self.config.path, "css")):
            os.makedirs(os.path.join(self.config.path, "css"))
        if not os.path.exists(os.path.join(self.config.path, "images")):
            os.makedirs(os.path.join(self.config.path, "images"))
        if not os.path.exists(os.path.join(self.config.path, "fonts")):
            os.makedirs(os.path.join(self.config.path, "fonts"))
        if not os.path.exists(os.path.join(self.config.path, "data")):
            os.makedirs(os.path.join(self.config.path, "data"))

        # shutil.copy(os.path.join(self.template_dir, "favicon.ico"), os.path.join(self.config.path, "favicon.ico"))

        shutil.copytree(
            os.path.join(self.template_dir, "js"),
            os.path.join(self.config.path, "js"),
            dirs_exist_ok=True,
        )
        shutil.copytree(
            os.path.join(self.template_dir, "css"),
            os.path.join(self.config.path, "css"),
            dirs_exist_ok=True,
        )
        shutil.copytree(
            os.path.join(self.template_dir, "images"),
            os.path.join(self.config.path, "images"),
            dirs_exist_ok=True,
        )
        # shutil.copytree(os.path.join(self.template_dir, "fonts"), os.path.join(self.config.path, "fonts"), dirs_exist_ok=True)

        # copy logo, lies 2 down from the templates directory
        shutil.copy(
            os.path.join(self.template_dir, "../..", "logo.svg"),
            os.path.join(self.config.path, "images", "logo.svg"),
        )

        # Render main pages
        self.render_index_page(metrics)
        self.render_files_page(metrics)
        self.render_top_offenders_page(metrics)
        self.render_git_analysis_page(metrics)
        self.render_dependencies_page(metrics)
        self.render_trends_page(metrics)

        self.output.writeln(
            f"<success>HTML report generated in {self.config.path} directory</success>"
        )
        self.output.writeln(
            f"<success>Open HTML report: {self.config.path}/index.html</success>"
        )

    def render_index_page(self, metrics: ProjectMetrics):
        self.output.writeln("<info>Rendering index page</info>")
        self.page_renderer_factory.create_index_page_renderer().render(metrics)
        self.output.writeln("<success>Done rendering index page</success>")

    def render_files_page(self, metrics: ProjectMetrics):
        """Render the files page with file details and analysis"""
        self.output.writeln("<info>Rendering files page</info>")
        self.page_renderer_factory.create_files_page_renderer().render(metrics)
        self.output.writeln("<success>Files page generated successfully</success>")

    def render_top_offenders_page(self, metrics: ProjectMetrics):
        self.output.writeln("<info>Rendering top offenders page</info>")
        self.page_renderer_factory.create_top_offenders_page_renderer().render(metrics)
        self.output.writeln(
            "<success>Top offenders page generated successfully</success>"
        )

    def render_git_analysis_page(self, metrics: ProjectMetrics):
        """Render the git analysis page with comprehensive git data"""
        self.output.writeln("<info>Rendering git analysis page</info>")
        self.page_renderer_factory.create_git_analysis_page_renderer().render(metrics)
        self.output.writeln(
            "<success>Git analysis page generated successfully</success>"
        )

    def render_dependencies_page(self, metrics: ProjectMetrics):
        """Render the dependencies page with dependency details and stats"""
        self.output.writeln("<info>Rendering dependencies page</info>")
        self.page_renderer_factory.create_dependency_page_renderer().render(metrics)
        self.output.writeln(
            "<success>Dependencies page generated successfully</success>"
        )

    def render_trends_page(self, metrics: ProjectMetrics):
        self.output.writeln("<info>Rendering trends page</info>")
        self.page_renderer_factory.create_trends_page_renderer().render(metrics)
        self.output.writeln("<success>Trends page generated successfully</success>")
