from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode


class ModuleNode:
    def __init__(
        self,
        full_name: str,
        loc: int,
        lloc: int,
        sloc: int,
        comments: int,
        multi: int,
        blank: int,
        single_comments: int,
    ):
        self.full_name = full_name
        self.loc = loc
        self.lloc = lloc
        self.sloc = sloc
        self.comments = comments
        self.multi = multi
        self.blank = blank
        self.single_comments = single_comments
        self.maintainability_index = 0
        self.classes: list[ClassNode] = []
        self.functions: list[FunctionNode] = []

    def to_dict(self) -> dict:
        return {
            "full_name": self.full_name,
            "loc": self.loc,
            "lloc": self.lloc,
            "sloc": self.sloc,
            "comments": self.comments,
            "multi": self.multi,
            "blank": self.blank,
            "single_comments": self.single_comments,
            "maintainability_index": self.maintainability_index,
            "classes": [c.to_dict() for c in self.classes],
            "functions": [f.to_dict() for f in self.functions],
        }
