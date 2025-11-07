from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Json.AbstractJsonReporter import AbstractJsonReporter


class GitJsonReporter(AbstractJsonReporter):
    def generate(self, metrics: ProjectMetrics) -> None:
        if not metrics.git_metrics:
            self.output.writeln(
                "<error>Wants git json report, but no git metrics</error>"
            )
            return

        data = {
            "commits_per_month": metrics.git_metrics.get_commit_stats_per_month(),
            "churn_data": metrics.git_metrics.get_churn_per_month(),
            "possible_silos": metrics.git_metrics.get_silos_list()[:10],
            "top_contributors": metrics.git_metrics.get_contributors_list()[:10],
            "top_hotspots": metrics.git_metrics.get_hotspots_list()[:10],
        }

        self.put_data(data)
        self.output.writeln(
            f"<success>Create git json report in {self.config.path}</success>"
        )
