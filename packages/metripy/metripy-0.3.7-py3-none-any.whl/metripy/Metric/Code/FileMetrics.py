from typing import Self

from metripy.Metric.Code.Segmentor import Segmentor
from metripy.Metric.Trend.FileTrendMetric import FileTrendMetric
from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode


class FileMetrics:
    def __init__(
        self,
        full_name: str,
        loc: int,
        totalCc: int,
        avgCcPerFunction: float,
        maintainabilityIndex: float,
        avgLocPerFunction: float,
        class_nodes: list[ClassNode],
        function_nodes: list[FunctionNode],
    ):
        self.full_name = full_name
        self.loc = loc
        self.totalCc = totalCc
        self.avgCcPerFunction = avgCcPerFunction
        self.maintainabilityIndex = maintainabilityIndex
        self.avgLocPerFunction = avgLocPerFunction
        self.class_nodes = class_nodes
        self.function_nodes = function_nodes
        self.trend: FileTrendMetric | None = None

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "loc": self.loc,
            "loc_segment": Segmentor.get_loc_segment(self.loc),
            "totalCc": self.totalCc,
            "complexity_segment": Segmentor.get_complexity_segment(
                self.avgCcPerFunction
            ),
            "avgCcPerFunction": self.avgCcPerFunction,
            "maintainabilityIndex": round(self.maintainabilityIndex, 2),
            "maintainability_segment": Segmentor.get_maintainability_segment(
                self.maintainabilityIndex
            ),
            "avgLocPerFunction": self.avgLocPerFunction,
            "method_size_segment": Segmentor.get_method_size_segment(
                self.avgLocPerFunction
            ),
            "class_nodes": [node.to_dict() for node in self.class_nodes],
            "function_nodes": [node.to_dict() for node in self.function_nodes],
        }

    @staticmethod
    def from_dict(data: dict) -> Self:
        return FileMetrics(
            full_name=data["full_name"],
            loc=data["loc"],
            totalCc=data["totalCc"],
            avgCcPerFunction=data["avgCcPerFunction"],
            maintainabilityIndex=data["maintainabilityIndex"],
            avgLocPerFunction=data["avgLocPerFunction"],
            class_nodes=[ClassNode.from_dict(d) for d in data["class_nodes"]],
            function_nodes=[FunctionNode.from_dict(d) for d in data["function_nodes"]],
        )
