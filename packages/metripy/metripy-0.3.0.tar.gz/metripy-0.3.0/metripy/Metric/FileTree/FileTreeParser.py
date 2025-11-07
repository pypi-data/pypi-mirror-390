from metripy.Metric.FileTree.FileTree import FileTree


class FileTreeParser:
    @staticmethod
    def parse(paths: list[str], shorten: bool = False) -> FileTree:
        root = FileTree(".", ".")

        for path in paths:
            parts = path.strip("./").split("/")
            current = root

            for part in parts:
                # Check if part already exists in current children
                found = next(
                    (child for child in current.children if child.name == part), None
                )
                if not found:
                    found = FileTree(part, path)
                    current.children.append(found)
                current = found

        if shorten:
            FileTreeParser._shorten_tree(root)

        return root

    @staticmethod
    def _shorten_tree(node: FileTree):
        """shorten tree nodes that only have a single child"""
        while len(node.children) == 1:
            child = node.children[0]
            node.name += "/" + child.name
            node.full_name = child.full_name
            node.children = child.children

        for child in node.children:
            FileTreeParser._shorten_tree(child)
