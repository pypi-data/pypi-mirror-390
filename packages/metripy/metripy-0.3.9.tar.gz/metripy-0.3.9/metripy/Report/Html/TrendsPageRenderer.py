from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Report.Html.PageRenderer import PageRenderer


class TrendsPageRenderer(PageRenderer):
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        super().__init__(template_dir, output_dir, project_name)

    def _compile_trend_item(self, file: FileMetrics) -> dict:
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
            "maintainability_delta": round(file.trend.maintainabilityIndex_delta, 2),
        }

    def render(self, metrics: ProjectMetrics):
        if metrics.total_code_metrics.trend is None:
            self.render_template(
                "trends.html",
                {
                    "has_trend_data": False,
                    "trend_data": {
                        "top_improved_complexity": [],
                        "top_improved_maintainability": [],
                        "top_worsened_complexity": [],
                        "top_worsened_maintainability": [],
                        "loc_segments_current": {},
                        "loc_segments_prev": {},
                        "complexity_segments_current": {},
                        "complexity_segments_prev": {},
                        "maintainability_segments_current": {},
                        "maintainability_segments_prev": {},
                        "method_size_segments_current": {},
                        "method_size_segments_prev": {},
                    },
                },
            )
            return

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
            "top_improved_complexity": [
                self._compile_trend_item(x) for x in top_improved_complexity
            ],
            "top_improved_maintainability": [
                self._compile_trend_item(x) for x in top_improved_maintainability
            ],
            "top_worsened_complexity": [
                self._compile_trend_item(x) for x in top_worsened_complexity
            ],
            "top_worsened_maintainability": [
                self._compile_trend_item(x) for x in top_worsened_maintainability
            ],
        }

        self.render_template(
            "trends.html",
            {
                "has_trend_data": metrics.total_code_metrics.trend is not None,
                "trend_data": trend_data,
            },
        )
