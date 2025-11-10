import re


class PhpBasicAstParser:

    @staticmethod
    def parse_php_structure(code: str):

        # Regex patterns
        class_pattern = re.compile(r"class\s+(\w*)")
        interface_pattern = re.compile(r"interface\s+(\w*)")
        method_pattern = re.compile(r"function\s+(\w+)\s*\([^)]*\)?")
        function_pattern = re.compile(r"function\s+(\w+)\s*\([^)]*\)?")

        lines = code.split("\n")
        structure = []
        current_class = None

        for i, line in enumerate(lines):
            class_match = class_pattern.search(line)
            if class_match:
                current_class = class_match.group(1)
                structure.append(
                    {"type": "class", "name": current_class, "line": i + 1}
                )

            interface_match = interface_pattern.search(line)
            if interface_match:
                current_class = interface_match.group(1)
                structure.append(
                    {
                        "type": "class",
                        "type_type": "interface",
                        "name": current_class,
                        "line": i + 1,
                    }
                )

            method_match = method_pattern.search(line)
            if method_match and current_class:
                structure.append(
                    {
                        "type": "method",
                        "name": method_match.group(1),
                        "class": current_class,
                        "line": i + 1,
                    }
                )

            elif function_pattern.search(line) and not current_class:
                function_name = function_pattern.search(line).group(1)
                structure.append(
                    {"type": "function", "name": function_name, "line": i + 1}
                )

        return structure
