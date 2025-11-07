from typing import Self

from metripy.Metric.Code.Segmentor import Segmentor
from metripy.Metric.Trend.ClassTrendMetric import ClassTrendMetric
from metripy.Tree.FunctionNode import FunctionNode


class ClassNode:
    def __init__(
        self,
        full_name: str,
        name: str,
        lineno: int,
        col_offset: int,
        real_complexity: int,
    ):
        self.full_name = full_name
        self.name = name
        self.lineno = lineno
        self.col_offset = col_offset
        self.real_complexity = real_complexity
        self.functions: list[FunctionNode] = []

        self.trend: ClassTrendMetric | None = None

    def to_dict(self) -> dict:
        """Convert ClassNode to a dictionary for JSON serialization."""
        return {
            "full_name": self.full_name,
            "name": self.name,
            "lineno": self.lineno,
            "col_offset": self.col_offset,
            "real_complexity": self.real_complexity,
            "complexity_segment": Segmentor.get_complexity_segment(
                self.real_complexity
            ),
            "functions": [func.to_dict() for func in self.functions],
        }

    def __dict__(self) -> dict:
        return self.to_dict()

    @staticmethod
    def from_dict(data: dict) -> Self:
        node = ClassNode(
            full_name=data["full_name"],
            name=data["name"],
            lineno=data["lineno"],
            col_offset=data["col_offset"],
            real_complexity=data["real_complexity"],
        )
        node.functions = [FunctionNode.from_dict(d) for d in data["functions"]]
        return node
