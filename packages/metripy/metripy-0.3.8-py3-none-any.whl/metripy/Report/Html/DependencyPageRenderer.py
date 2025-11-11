import json

from metripy.Dependency.Dependency import Dependency
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class DependencyPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def render(self, metrics: ProjectMetrics):
        dependencies = metrics.dependencies if metrics.dependencies is not None else []
        license_by_type = Dependency.get_lisence_distribution(dependencies)

        self.render_template(
            "dependencies.html",
            {
                "has_dependencies_data": bool(metrics.dependencies),
                "dependencies": [d.to_dict() for d in dependencies],
                "license_distribution_json": json.dumps(license_by_type, indent=2),
            },
        )
