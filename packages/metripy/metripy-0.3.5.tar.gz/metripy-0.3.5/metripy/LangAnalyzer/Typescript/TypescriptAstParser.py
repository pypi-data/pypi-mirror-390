from collections import defaultdict

from tree_sitter_languages import get_parser


class TypescriptAstParser:
    def __init__(self):
        self.parser = get_parser("typescript")

    def _get_node_text(self, code: str, node) -> str:
        return code[node.start_byte : node.end_byte].decode("utf-8")

    def extract_structure(self, code: str) -> dict:
        tree = self.parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        structure = defaultdict(list)
        structure["classes"] = {}
        structure["functions"] = []
        structure["enums"] = []

        def traverse(node, parent_class=None):
            if node.type == "class_declaration":
                class_name = None
                for child in node.children:
                    if child.type == "type_identifier":
                        class_name = self._get_node_text(code.encode(), child)
                        structure["classes"][class_name] = []
                for child in node.children:
                    traverse(child, class_name)

            elif node.type == "method_definition" and parent_class:
                for child in node.children:
                    if child.type == "property_identifier":
                        method_name = self._get_node_text(code.encode(), child)
                        structure["classes"][parent_class].append(method_name)

            elif node.type == "function_declaration":
                for child in node.children:
                    if child.type == "identifier":
                        function_name = self._get_node_text(code.encode(), child)
                        structure["functions"].append(function_name)

            elif node.type == "lexical_declaration":
                # Handle exported arrow functions like: export const foo = (...) => {...}
                for child in node.children:
                    if child.type == "variable_declarator":
                        identifier = None
                        for grandchild in child.children:
                            if grandchild.type == "identifier":
                                identifier = self._get_node_text(
                                    code.encode(), grandchild
                                )
                            elif grandchild.type == "arrow_function":
                                if identifier:
                                    structure["functions"].append(identifier)

            elif node.type == "enum_declaration":
                enum_name = None
                for child in node.children:
                    if child.type == "identifier":
                        enum_name = self._get_node_text(code.encode(), child)
                        structure["enums"].append(enum_name)

            for child in node.children:
                traverse(child, parent_class)

        traverse(root_node)
        return dict(structure)
