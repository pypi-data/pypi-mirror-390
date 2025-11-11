from metripy.Metric.Code.SegmentedMetrics import SegmentedMetrics


class SegmentedTrendMetric:
    def __init__(
        self,
        historical_segmentation: SegmentedMetrics,
        segmentation: SegmentedMetrics,
    ):
        self.historical_good = historical_segmentation.good
        self.good_delta = segmentation.good - historical_segmentation.good
        self.historical_ok = historical_segmentation.ok
        self.ok_delta = segmentation.ok - historical_segmentation.ok
        self.historical_warning = historical_segmentation.warning
        self.warning_delta = segmentation.warning - historical_segmentation.warning
        self.historical_critical = historical_segmentation.critical
        self.critical_delta = segmentation.critical - historical_segmentation.critical

    def to_dict(self) -> dict:
        return {
            "historical_good": self.historical_good,
            "good_delta": self.good_delta,
            "historical_ok": self.historical_ok,
            "ok_delta": self.ok_delta,
            "historical_warning": self.historical_warning,
            "warning_delta": self.warning_delta,
            "historical_critical": self.historical_critical,
            "critical_delta": self.critical_delta,
        }
