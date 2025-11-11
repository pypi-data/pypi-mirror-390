from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode


class ModuleMetrics:
    def __init__(
        self,
        loc: int,
        avgCcPerFunction: float,
        maintainabilityIndex: float,
        avgLocPerFunction: float,
        class_nodes: list[ClassNode],
        function_nodes: list[FunctionNode],
    ):
        self.loc = loc
        self.avgCcPerFunction = avgCcPerFunction
        self.maintainabilityIndex = maintainabilityIndex
        self.avgLocPerFunction = avgLocPerFunction
        self.num_files = 1
        self.class_nodes: list[ClassNode] = class_nodes
        self.function_nodes: list[FunctionNode] = function_nodes

    def to_dict(self) -> dict:
        return {
            "loc": self.loc,
            "avgCcPerFunction": round(self.avgCcPerFunction, 2),
            "maintainabilityIndex": round(self.maintainabilityIndex, 2),
            "avgLocPerFunction": round(self.avgLocPerFunction, 2),
            "num_files": self.num_files,
            "class_nodes": [node.to_dict() for node in self.class_nodes],
            "function_nodes": [node.to_dict() for node in self.function_nodes],
        }
