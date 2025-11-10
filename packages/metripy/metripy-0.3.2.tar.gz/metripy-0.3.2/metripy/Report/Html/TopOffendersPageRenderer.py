from metripy.Metric.Code.Segmentor import Segmentor
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class TopOffendersPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def render(self, metrics: ProjectMetrics):
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
            },
        )
