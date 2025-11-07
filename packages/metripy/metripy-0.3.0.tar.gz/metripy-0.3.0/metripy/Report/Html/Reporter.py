import json
import os
import shutil
from datetime import datetime

from py_template_engine import TemplateEngine

from metripy.Application.Config.ReportConfig import ReportConfig
from metripy.Component.Output.CliOutput import CliOutput
from metripy.Dependency.Dependency import Dependency
from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Metric.Code.Segmentor import Segmentor
from metripy.Metric.FileTree.FileTreeParser import FileTreeParser
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.ReporterInterface import ReporterInterface


class Reporter(ReporterInterface):
    def __init__(
        self, config: ReportConfig, output: CliOutput, project_name: str = "foobar"
    ):
        self.config: ReportConfig = config
        self.output = output
        self.template_dir = os.path.join(os.getcwd(), "templates/html_report")

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
        shutil.copy(os.path.join(self.template_dir, "../..", "logo.svg"), os.path.join(self.config.path, "images", "logo.svg"))

        # Render main pages
        self.render_index_page(metrics)
        self.render_files_page(metrics)
        self.render_git_analysis_page(metrics)
        self.render_dependencies_page(metrics)
        self.render_top_offenders_page(metrics)
        self.render_trends_page(metrics)

        self.output.writeln(
            f"<success>HTML report generated in {self.config.path} directory</success>"
        )

    def render_template(self, template_name: str, data: dict) -> str:
        engine = TemplateEngine(os.path.join(self.template_dir, template_name))
        content = engine.render(**data)
        with open(os.path.join(self.config.path, template_name), "w") as file:
            file.write(content)

    def render_trends_page(self, metrics: ProjectMetrics):
        def compile(file: FileMetrics) -> dict:
            return {
                "name": file.full_name,
                "path": file.full_name,
                "complexity_current": file.totalCc,
                "complexity_prev": round(file.trend.historical_totalCc, 2),
                "complexity_delta": round(file.trend.totalCc_delta, 2),
                "maintainability_current": round(file.maintainabilityIndex, 2),
                "maintainability_prev": round(
                    file.trend.historical_maintainabilityIndex, 2
                ),
                "maintainability_delta": round(
                    file.trend.maintainabilityIndex_delta, 2
                ),
            }

        # Top improved complexity (complexity went down - negative delta)
        top_improved_complexity = [
            x
            for x in metrics.file_metrics
            if x.trend is not None and x.trend.totalCc_delta < 0
        ]
        top_improved_complexity = sorted(
            top_improved_complexity, key=lambda x: x.trend.totalCc_delta
        )[:10]

        # Top worsened complexity (complexity went up - positive delta)
        top_worsened_complexity = [
            x
            for x in metrics.file_metrics
            if x.trend is not None and x.trend.totalCc_delta > 0
        ]
        top_worsened_complexity = sorted(
            top_worsened_complexity, key=lambda x: x.trend.totalCc_delta, reverse=True
        )[:10]

        # Top improved maintainability (maintainability went up - positive delta)
        top_improved_maintainability = [
            x
            for x in metrics.file_metrics
            if x.trend is not None and round(x.trend.maintainabilityIndex_delta, 2) > 0
        ]
        top_improved_maintainability = sorted(
            top_improved_maintainability,
            key=lambda x: x.trend.maintainabilityIndex_delta,
            reverse=True,
        )[:10]

        # Top worsened maintainability (maintainability went down - negative delta)
        top_worsened_maintainability = [
            x
            for x in metrics.file_metrics
            if x.trend is not None and round(x.trend.maintainabilityIndex_delta, 2) < 0
        ]
        top_worsened_maintainability = sorted(
            top_worsened_maintainability,
            key=lambda x: x.trend.maintainabilityIndex_delta,
        )[:10]

        trend_data = {
            # Segment distributions for each metric
            "loc_segments_current": metrics.total_code_metrics.segmentation_data[
                "loc"
            ].to_dict_with_percent(),
            "loc_segments_prev": metrics.total_code_metrics.trend.historical_segmentation_data[
                "loc"
            ].to_dict_with_percent(),
            "complexity_segments_current": metrics.total_code_metrics.segmentation_data[
                "complexity"
            ].to_dict_with_percent(),
            "complexity_segments_prev": metrics.total_code_metrics.trend.historical_segmentation_data[
                "complexity"
            ].to_dict_with_percent(),
            "maintainability_segments_current": metrics.total_code_metrics.segmentation_data[
                "maintainability"
            ].to_dict_with_percent(),
            "maintainability_segments_prev": metrics.total_code_metrics.trend.historical_segmentation_data[
                "maintainability"
            ].to_dict_with_percent(),
            "method_size_segments_current": metrics.total_code_metrics.segmentation_data[
                "methodSize"
            ].to_dict_with_percent(),
            "method_size_segments_prev": metrics.total_code_metrics.trend.historical_segmentation_data[
                "methodSize"
            ].to_dict_with_percent(),
            "top_improved_complexity": [compile(x) for x in top_improved_complexity],
            "top_improved_maintainability": [
                compile(x) for x in top_improved_maintainability
            ],
            "top_worsened_complexity": [compile(x) for x in top_worsened_complexity],
            "top_worsened_maintainability": [
                compile(x) for x in top_worsened_maintainability
            ],
        }

        self.output.writeln("<info>Rendering trends page</info>")
        self.render_template(
            "trends.html",
            {
                "has_trend_data": metrics.total_code_metrics.trend is not None,
                "trend_data": trend_data,
                "project_name": "Metripy",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "author": "Metripy",
                "version": "1.0.0",
            },
        )

    def render_index_page(self, metrics: ProjectMetrics):
        git_stats_data = {}
        if metrics.git_metrics:
            git_stats_data = metrics.git_metrics.get_commit_stats_per_month()

        self.output.writeln("<info>Rendering index page</info>")
        self.render_template(
            "index.html",
            {
                "git_stats_data": json.dumps(git_stats_data, indent=4),
                "total_code_metrics": metrics.total_code_metrics.to_dict(),
                "has_total_code_metrics_trend": metrics.total_code_metrics.trend
                is not None,
                "total_code_metrics_trend": (
                    metrics.total_code_metrics.trend.to_dict()
                    if metrics.total_code_metrics.trend
                    else None
                ),
                "segmentation_data": json.dumps(
                    metrics.total_code_metrics.to_dict_segmentation(), indent=4
                ),
                "segmentation_data_trend": (
                    json.dumps(
                        metrics.total_code_metrics.trend.to_dict_segmentation(),
                        indent=4,
                    )
                    if metrics.total_code_metrics.trend
                    else None
                ),
                "project_name": "Metripy",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "author": "Metripy",
                "version": "1.0.0",
            },
        )
        self.output.writeln("<success>Done rendering index page</success>")

    def render_top_offenders_page(self, metrics: ProjectMetrics):
        self.output.writeln("<info>Rendering top offenders page</info>")

        orderedByTotalCc = sorted(
            metrics.file_metrics, key=lambda x: x.totalCc, reverse=True
        )[:10]
        orderedByMI = sorted(
            metrics.file_metrics, key=lambda x: x.maintainabilityIndex, reverse=False
        )[:10]
        orderedByLoc = sorted(metrics.file_metrics, key=lambda x: x.loc, reverse=True)[
            :10
        ]

        all_functions: list = []
        for fm in metrics.file_metrics:
            all_functions.extend(fm.function_nodes)

        functionsOrderedByCc = sorted(
            all_functions, key=lambda x: x.complexity, reverse=True
        )[:10]
        functionsOrderedByMi = sorted(
            all_functions, key=lambda x: x.maintainability_index, reverse=False
        )[:10]
        functionsOrderedByLoc = sorted(
            all_functions, key=lambda x: x.get_loc(), reverse=True
        )[:10]

        # TODO maintainability index per function, we dont calc yet

        self.render_template(
            "top_offenders.html",
            Reporter._stringify_values(
                {
                    "file_loc_offenders": [
                        {**e.to_dict(), "status": Segmentor.get_loc_segment(e.loc)}
                        for e in orderedByLoc
                    ],
                    "file_cc_offenders": [
                        {
                            **e.to_dict(),
                            "status": Segmentor.get_complexity_segment(e.totalCc),
                        }
                        for e in orderedByTotalCc
                    ],
                    "file_mi_offenders": [
                        {
                            **e.to_dict(),
                            "status": Segmentor.get_maintainability_segment(
                                e.maintainabilityIndex
                            ),
                        }
                        for e in orderedByMI
                    ],
                    "function_size_offenders": [
                        {
                            **e.to_dict(),
                            "status": Segmentor.get_method_size_segment(e.get_loc()),
                        }
                        for e in functionsOrderedByLoc
                    ],
                    "function_cc_offenders": [
                        {
                            **e.to_dict(),
                            "status": Segmentor.get_complexity_segment(e.complexity),
                        }
                        for e in functionsOrderedByCc
                    ],
                    "function_mi_offenders": [
                        {
                            **e.to_dict(),
                            "status": Segmentor.get_maintainability_segment(
                                e.maintainability_index
                            ),
                        }
                        for e in functionsOrderedByMi
                    ],
                    "project_name": "Metripy",
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ),
        )
        self.output.writeln(
            "<success>Top offenders page generated successfully</success>"
        )

    def render_dependencies_page(self, metrics: ProjectMetrics):
        """Render the dependencies page with dependency details and stats"""
        if not metrics.dependencies:
            self.output.writeln("<success>No dependencies to render</success>")
            return

        self.output.writeln("<info>Rendering dependencies page</info>")

        dependencies = metrics.dependencies if metrics.dependencies is not None else []

        license_by_type = Dependency.get_lisence_distribution(dependencies)

        self.render_template(
            "dependencies.html",
            {
                "dependencies": [d.to_dict() for d in dependencies],
                "project_name": "Metripy",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        self.output.writeln(
            "<success>Dependencies page generated successfully</success>"
        )

    def render_files_page(self, metrics: ProjectMetrics):
        """Render the files page with file details and analysis"""
        self.output.writeln("<info>Rendering files page</info>")

        file_names = []
        file_details = {}
        for file_metrics in metrics.file_metrics:
            file_name = file_metrics.full_name
            file_details[file_name] = file_metrics.to_dict()
            file_names.append(file_name)

        filetree = FileTreeParser.parse(file_names, shorten=True)

        self.render_template(
            "files.html",
            {
                "filetree": json.dumps(filetree.to_dict()),
                "file_details": json.dumps(file_details),
                "project_name": "Metripy",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        self.output.writeln("<success>Files page generated successfully</success>")

    @staticmethod
    def _stringify_values(obj):
        if isinstance(obj, dict):
            return {
                key: Reporter._stringify_values(value) for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [Reporter._stringify_values(item) for item in obj]
        else:
            return str(obj)

    def render_git_analysis_page(self, metrics: ProjectMetrics):
        """Render the git analysis page with comprehensive git data"""
        if not metrics.git_metrics:
            self.output.writeln("<success>No git metrics to render</success>")
            return

        self.output.writeln("<info>Rendering git analysis page</info>")
        try:
            # Render git analysis template
            self.render_template(
                "git_analysis.html",
                Reporter._stringify_values(
                    {
                        "git_analysis": metrics.git_metrics.to_dict(),
                        "git_analysis_json": json.dumps(
                            metrics.git_metrics.get_contributors_dict(), indent=4
                        ),
                        "git_stats_data": json.dumps(
                            metrics.git_metrics.get_commit_stats_per_month(), indent=4
                        ),  # git commit graph
                        "git_churn_data": json.dumps(
                            metrics.git_metrics.get_churn_per_month(), indent=4
                        ),  # git chrun graph
                        "git_silos_data": metrics.git_metrics.get_silos_list()[
                            :10
                        ],  # silos list
                        "git_contributors": metrics.git_metrics.get_contributors_list()[
                            :10
                        ],  # contributors list
                        "git_hotspots_data": metrics.git_metrics.get_hotspots_list()[
                            :10
                        ],  # hotspots list
                        "project_name": "Metripy",
                        "last_updated": metrics.git_metrics.get_analysis_start_date(),
                    }
                ),
            )

            self.output.writeln(
                "<success>Git analysis page generated successfully</success>"
            )
        except Exception as e:
            raise e
            self.output.writeln(
                f"<error>Error generating git analysis page: {e}</error>"
            )
