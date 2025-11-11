from metripy.Metric.Code.SegmentedMetrics import SegmentedMetrics
from metripy.Metric.Trend.SegmentedTrendMetric import SegmentedTrendMetric


class AggregatedTrendMetric:
    def __init__(
        self,
        historical_loc: int,
        loc: int,
        historical_avgCcPerFunction: float,
        avgCcPerFunction: float,
        historical_maintainabilityIndex: float,
        maintainabilityIndex: float,
        historical_avgLocPerFunction: float,
        avgLocPerFunction: float,
        historical_num_files: int,
        num_files: int,
        historical_segmented_loc: SegmentedMetrics,
        segmented_loc: SegmentedMetrics,
        historical_segmented_complexity: SegmentedMetrics,
        segmented_complexity: SegmentedMetrics,
        historical_segmented_maintainability: SegmentedMetrics,
        segmented_maintainability: SegmentedMetrics,
        historical_segmented_method_size: SegmentedMetrics,
        segmented_method_size: SegmentedMetrics,
    ):
        self.historical_loc = historical_loc
        self.loc_delta = loc - historical_loc
        self.historical_avgCcPerFunction = historical_avgCcPerFunction
        self.avgCcPerFunction_delta = avgCcPerFunction - historical_avgCcPerFunction
        self.historical_maintainabilityIndex = historical_maintainabilityIndex
        self.maintainabilityIndex_delta = (
            maintainabilityIndex - historical_maintainabilityIndex
        )
        self.historical_avgLocPerFunction = historical_avgLocPerFunction
        self.avgLocPerFunction_delta = avgLocPerFunction - historical_avgLocPerFunction
        self.historical_num_files = historical_num_files
        self.num_files_delta = num_files - historical_num_files

        self.historical_segmentation_data = {
            "loc": historical_segmented_loc,
            "complexity": historical_segmented_complexity,
            "maintainability": historical_segmented_maintainability,
            "methodSize": historical_segmented_method_size,
        }

        self.segmentation_data_deltas = {
            "loc": SegmentedTrendMetric(historical_segmented_loc, segmented_loc),
            "complexity": SegmentedTrendMetric(
                historical_segmented_complexity, segmented_complexity
            ),
            "maintainability": SegmentedTrendMetric(
                historical_segmented_maintainability, segmented_maintainability
            ),
            "methodSize": SegmentedTrendMetric(
                historical_segmented_method_size, segmented_method_size
            ),
        }

    def get_trend_type(self, delta: float, up_is_good: bool) -> str:
        if up_is_good:
            return "positive" if delta > 0 else "negative" if delta < 0 else "neutral"
        else:
            return "negative" if delta > 0 else "positive" if delta < 0 else "neutral"

    def get_trend_icon(self, delta: float) -> str:
        return "arrow-up" if delta > 0 else "arrow-down" if delta < 0 else "arrow-right"

    def to_dict(self) -> dict:
        return {
            "loc_delta": round(self.loc_delta, 2),
            "loc_trend_type": self.get_trend_type(self.loc_delta, False),
            "loc_trend_icon": self.get_trend_icon(self.loc_delta),
            "avgCcPerFunction_delta": round(self.avgCcPerFunction_delta, 2),
            "avgCcPerFunction_trend_type": self.get_trend_type(
                self.avgCcPerFunction_delta, False
            ),
            "avgCcPerFunction_trend_icon": self.get_trend_icon(
                self.avgCcPerFunction_delta
            ),
            "maintainabilityIndex_delta": round(self.maintainabilityIndex_delta, 2),
            "maintainabilityIndex_trend_type": self.get_trend_type(
                self.maintainabilityIndex_delta, True
            ),
            "maintainabilityIndex_trend_icon": self.get_trend_icon(
                self.maintainabilityIndex_delta
            ),
            "avgLocPerFunction_delta": round(self.avgLocPerFunction_delta, 2),
            "avgLocPerFunction_trend_type": self.get_trend_type(
                self.avgLocPerFunction_delta, False
            ),
            "avgLocPerFunction_trend_icon": self.get_trend_icon(
                self.avgLocPerFunction_delta
            ),
            "num_files_delta": self.num_files_delta,
            "num_files_trend_type": self.get_trend_type(self.num_files_delta, False),
            "num_files_trend_icon": self.get_trend_icon(self.num_files_delta),
        }

    def to_dict_segmentation(self) -> dict:
        return {k: v.to_dict() for k, v in self.segmentation_data_deltas.items()}
