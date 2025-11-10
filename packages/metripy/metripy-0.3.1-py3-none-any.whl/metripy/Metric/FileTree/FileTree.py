from typing import Self


class FileTree:
    def __init__(self, name: str, full_name: str, children: list[Self] | None = None):
        self.name = name
        self.full_name = full_name
        self.children: list[Self] = children if children is not None else []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "full_name": self.full_name,
            "children": [child.to_dict() for child in self.children],
        }
