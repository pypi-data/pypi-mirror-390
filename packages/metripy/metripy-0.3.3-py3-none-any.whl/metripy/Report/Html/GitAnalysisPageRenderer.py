import json

from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class GitAnalysisPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def _render_empty_template(self):
        self.render_template(
            "git_analysis.html",
            {
                "has_git_analysis_data": False,
                "git_analysis": {},
                "git_analysis_json": "{}",
                "git_stats_data": "{}",
                "git_churn_data": "{}",
                "git_silos_data": [],
                "git_contributors": [],
                "git_hotspots_data": [],
            },
        )

    def render(self, metrics: ProjectMetrics):
        if not metrics.git_metrics:
            self._render_empty_template()
            return

        self.render_template(
            "git_analysis.html",
            {
                "has_git_analysis_data": bool(metrics.git_metrics),
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
            },
        )
