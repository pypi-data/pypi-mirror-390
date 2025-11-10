import json

from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class IndexPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def render(self, metrics: ProjectMetrics):
        git_stats_data = {}
        if metrics.git_metrics:
            git_stats_data = metrics.git_metrics.get_commit_stats_per_month()

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
            },
        )
