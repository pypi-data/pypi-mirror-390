from metripy.Metric.Code.SegmentedMetrics import SegmentedMetrics
from metripy.Metric.Trend.AggregatedTrendMetric import AggregatedTrendMetric


class AggregatedMetrics:
    """Used to show aggregated metrics on the index page"""

    def __init__(
        self,
        loc: int = 0,
        avgCcPerFunction: float = 0.0,
        maintainabilityIndex: float = 0.0,
        avgLocPerFunction: float = 0.0,
        num_files: int = 0,
        segmented_loc: SegmentedMetrics = SegmentedMetrics(),
        segmented_complexity: SegmentedMetrics = SegmentedMetrics(),
        segmented_maintainability: SegmentedMetrics = SegmentedMetrics(),
        segmented_method_size: SegmentedMetrics = SegmentedMetrics(),
    ) -> None:
        self.loc = loc
        self.avgCcPerFunction = avgCcPerFunction
        self.maintainabilityIndex = maintainabilityIndex
        self.avgLocPerFunction = avgLocPerFunction
        self.num_files = num_files

        self.segmentation_data = {
            "loc": segmented_loc,
            "complexity": segmented_complexity,
            "maintainability": segmented_maintainability,
            "methodSize": segmented_method_size,
        }

        self.trend: AggregatedTrendMetric | None = None

    def to_dict(self) -> dict:
        return {
            "loc": self.loc,
            "avgCcPerFunction": round(self.avgCcPerFunction, 2),
            "maintainabilityIndex": round(self.maintainabilityIndex, 2),
            "avgLocPerFunction": round(self.avgLocPerFunction, 2),
            "num_files": self.num_files,
            "trend": self.trend.to_dict() if self.trend else None,
            "trend_segmentation": (
                self.trend.to_dict_segmentation() if self.trend else None
            ),
        }

    def to_dict_segmentation(self) -> dict:
        return {k: v.to_dict() for k, v in self.segmentation_data.items()}
