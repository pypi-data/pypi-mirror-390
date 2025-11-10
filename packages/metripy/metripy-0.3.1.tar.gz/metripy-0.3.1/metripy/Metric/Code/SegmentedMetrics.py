from typing import Self

from metripy.Metric.Code.Segmentor import Segmentor


class SegmentedMetrics:
    def __init__(self):
        self.good = 0
        self.ok = 0
        self.warning = 0
        self.critical = 0

    def to_dict(self) -> dict:
        return {
            "good": self.good,
            "ok": self.ok,
            "warning": self.warning,
            "critical": self.critical,
        }

    def to_dict_with_percent(self) -> dict:
        return {
            "good": self.good,
            "good_percent": round(
                self.good / (self.good + self.ok + self.warning + self.critical) * 100,
                2,
            ),
            "ok": self.ok,
            "ok_percent": round(
                self.ok / (self.good + self.ok + self.warning + self.critical) * 100, 2
            ),
            "warning": self.warning,
            "warning_percent": round(
                self.warning
                / (self.good + self.ok + self.warning + self.critical)
                * 100,
                2,
            ),
            "critical": self.critical,
            "critical_percent": round(
                self.critical
                / (self.good + self.ok + self.warning + self.critical)
                * 100,
                2,
            ),
        }

    def _set_values(self, values: dict[str, int]) -> Self:
        self.good = values["good"]
        self.ok = values["ok"]
        self.warning = values["warning"]
        self.critical = values["critical"]
        return self

    def set_loc(self, values: list[int]) -> Self:
        d = {
            "good": self.good,
            "ok": self.ok,
            "warning": self.warning,
            "critical": self.critical,
        }
        for value in values:
            d[Segmentor.get_loc_segment(value)] += 1

        return self._set_values(d)

    def set_complexity(self, values: list[int]) -> Self:
        d = {
            "good": self.good,
            "ok": self.ok,
            "warning": self.warning,
            "critical": self.critical,
        }
        for value in values:
            d[Segmentor.get_complexity_segment(value)] += 1

        return self._set_values(d)

    def set_maintainability(self, values: list[int]) -> Self:
        d = {
            "good": self.good,
            "ok": self.ok,
            "warning": self.warning,
            "critical": self.critical,
        }
        for value in values:
            d[Segmentor.get_maintainability_segment(value)] += 1

        return self._set_values(d)

    def set_method_size(self, values: list[int]) -> Self:
        d = {
            "good": self.good,
            "ok": self.ok,
            "warning": self.warning,
            "critical": self.critical,
        }
        for value in values:
            d[Segmentor.get_method_size_segment(value)] += 1

        return self._set_values(d)
