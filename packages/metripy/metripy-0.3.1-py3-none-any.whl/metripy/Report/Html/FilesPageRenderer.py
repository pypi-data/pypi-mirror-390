import json

from metripy.Metric.FileTree.FileTreeParser import FileTreeParser
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class FilesPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def render(self, metrics: ProjectMetrics):
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
            },
        )
