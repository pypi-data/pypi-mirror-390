import math
from typing import Self

from metripy.Metric.Code.Segmentor import Segmentor
from metripy.Metric.Trend.FunctionTrendMetric import FunctionTrendMetric


class FunctionNode:
    def __init__(
        self, full_name: str, name: str, lineno: int, col_offset: int, complexity: int
    ):
        self.full_name = full_name
        self.name = name
        self.lineno = lineno
        self.line_end = 0
        self.col_offset = col_offset
        self.complexity = complexity
        self.h1 = 0
        self.h2 = 0
        self.N1 = 0
        self.N2 = 0
        self.vocabulary = 0
        self.length = 0
        self.calculated_length = 0
        self.volume = 0
        self.difficulty = 0
        self.effort = 0
        self.time = 0
        self.bugs = 0
        self.maintainability_index = 0
        self.trend: FunctionTrendMetric | None = None

    def get_loc(self) -> int:
        if self.name == "safeSanitizeArray":
            print("line_end", self.line_end)
            print("lineno", self.lineno)
            print("get_loc", self.line_end - self.lineno)
            print("--------------------------------")
        return self.line_end - self.lineno

    def calc_mi(self) -> None:

        total_volume = self.volume
        total_complexity = self.complexity
        total_length = self.length

        if total_volume == 0 or total_length == 0:
            self.maintainability_index = 100.0
            return

        # PHP maintainability index calculation
        mi_base = max(
            (
                171
                - 5.2 * math.log(total_volume)
                - 0.23 * total_complexity
                - 16.2 * math.log(total_length)
            )
            * 100
            / 171,
            0,
        )

        # no comment weight
        self.maintainability_index = mi_base

    def to_dict(self) -> dict:
        """Convert FunctionNode to a dictionary for JSON serialization."""
        return {
            "full_name": self.full_name,
            "name": self.name,
            "lineno": self.lineno,
            "line_end": self.line_end,
            "loc": self.get_loc(),
            "loc_segment": Segmentor.get_loc_segment(self.get_loc()),
            "col_offset": self.col_offset,
            "complexity": self.complexity,
            "complexity_segment": Segmentor.get_complexity_segment(self.complexity),
            "h1": self.h1,
            "h2": self.h2,
            "N1": self.N1,
            "N2": self.N2,
            "vocabulary": self.vocabulary,
            "length": self.length,
            "calculated_length": self.calculated_length,
            "volume": self.volume,
            "difficulty": self.difficulty,
            "effort": self.effort,
            "time": self.time,
            "bugs": self.bugs,
            "maintainability_index": round(self.maintainability_index, 2),
            "maintainability_segment": Segmentor.get_maintainability_segment(
                self.maintainability_index
            ),
        }

    def __dict__(self) -> dict:
        return self.to_dict()

    @staticmethod
    def from_dict(data: dict) -> Self:
        node = FunctionNode(
            full_name=data["full_name"],
            name=data["name"],
            lineno=data["lineno"],
            col_offset=data["col_offset"],
            complexity=data["complexity"],
        )
        node.line_end = data["line_end"]
        node.vocabulary = data["vocabulary"]
        node.length = data["length"]
        node.calculated_length = data["calculated_length"]
        node.volume = data["volume"]
        node.difficulty = data["difficulty"]
        node.effort = data["effort"]
        node.time = data["time"]
        node.bugs = data["bugs"]
        node.maintainability_index = data["maintainability_index"]

        return node
