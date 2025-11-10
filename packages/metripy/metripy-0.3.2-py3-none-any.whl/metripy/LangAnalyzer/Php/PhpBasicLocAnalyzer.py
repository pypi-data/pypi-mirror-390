import re


class PhpBasicLocAnalyzer:
    @staticmethod
    def get_loc_metrics(code: str, filename: str) -> dict:
        """Fallback LOC calculation using manual analysis"""
        try:
            lines = code.split("\n")

            total_lines = len(lines)
            blank_lines = PhpBasicLocAnalyzer._count_blank_lines(lines)
            comment_lines = PhpBasicLocAnalyzer._count_comment_lines(lines)
            code_lines = total_lines - blank_lines - comment_lines

            return {
                "lines": total_lines,
                "linesOfCode": code_lines,
                "logicalLinesOfCode": code_lines,
                "commentLines": comment_lines,
                "blankLines": blank_lines,
            }
        except Exception as e:
            print(f"Fallback LOC analysis failed: {e}")
            return {
                "lines": 0,
                "linesOfCode": 0,
                "logicalLinesOfCode": 0,
                "commentLines": 0,
                "blankLines": 0,
            }

    @staticmethod
    def _count_blank_lines(lines: list) -> int:
        """Count blank lines"""
        return sum(1 for line in lines if not line.strip())

    @staticmethod
    def _count_comment_lines(lines: list) -> int:
        """Count comment lines (single-line and multi-line)"""
        comment_count = 0
        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            # Handle multi-line comments
            if "/*" in stripped:
                in_multiline_comment = True
                comment_count += 1
                # Check if comment closes on same line
                if "*/" in stripped:
                    in_multiline_comment = False
                continue

            if in_multiline_comment:
                comment_count += 1
                if "*/" in stripped:
                    in_multiline_comment = False
                continue

            # Handle single-line comments
            if stripped.startswith(("//")) or stripped.startswith("#"):
                comment_count += 1
                continue

            # Handle doc comments
            if stripped.startswith("*") and not stripped.startswith("*/"):
                comment_count += 1
                continue

        return comment_count

    def _count_classes(self, lines: list) -> int:
        """Count class definitions"""
        content = "".join(lines)
        class_pattern = r"(?:abstract\s+)?class\s+\w+"
        return len(re.findall(class_pattern, content, re.IGNORECASE))

    def _count_functions(self, lines: list) -> int:
        """Count all function definitions (including methods)"""
        content = "".join(lines)
        func_pattern = (
            r"(?:public\s+|private\s+|protected\s+)?(?:static\s+)?function\s+\w+"
        )
        return len(re.findall(func_pattern, content, re.IGNORECASE))

    def _count_methods(self, lines: list) -> int:
        """Count class methods (functions inside classes)"""
        content = "".join(lines)

        # This is a simplified approach - count functions that appear after class declarations
        class_positions = []
        for match in re.finditer(r"class\s+\w+", content, re.IGNORECASE):
            class_positions.append(match.start())

        if not class_positions:
            return 0

        method_count = 0
        for match in re.finditer(
            r"(?:public\s+|private\s+|protected\s+)?(?:static\s+)?function\s+\w+",
            content,
            re.IGNORECASE,
        ):
            func_pos = match.start()
            # Check if this function is after any class declaration
            for class_pos in class_positions:
                if func_pos > class_pos:
                    method_count += 1
                    break

        return method_count

    def _count_constants(self, lines: list) -> int:
        """Count constants (const and define)"""
        content = "".join(lines)

        # Count const declarations
        const_pattern = r"\bconst\s+\w+"
        const_count = len(re.findall(const_pattern, content, re.IGNORECASE))

        # Count define() calls
        define_pattern = r"\bdefine\s*\("
        define_count = len(re.findall(define_pattern, content, re.IGNORECASE))

        return const_count + define_count

    def analyze_code_structure(self, filepath: str) -> dict:
        """Analyze the overall structure of the PHP file"""
        try:
            with open(filepath, "r") as f:
                content = f.read()

            # Count various PHP constructs
            structure = {
                "namespaces": len(
                    re.findall(r"namespace\s+[\w\\]+", content, re.IGNORECASE)
                ),
                "use_statements": len(
                    re.findall(r"use\s+[\w\\]+", content, re.IGNORECASE)
                ),
                "interfaces": len(
                    re.findall(r"interface\s+\w+", content, re.IGNORECASE)
                ),
                "traits": len(re.findall(r"trait\s+\w+", content, re.IGNORECASE)),
                "abstract_classes": len(
                    re.findall(r"abstract\s+class\s+\w+", content, re.IGNORECASE)
                ),
                "final_classes": len(
                    re.findall(r"final\s+class\s+\w+", content, re.IGNORECASE)
                ),
                "magic_methods": len(
                    re.findall(r"function\s+__\w+", content, re.IGNORECASE)
                ),
                "static_methods": len(
                    re.findall(r"static\s+function\s+\w+", content, re.IGNORECASE)
                ),
                "private_methods": len(
                    re.findall(r"private\s+function\s+\w+", content, re.IGNORECASE)
                ),
                "protected_methods": len(
                    re.findall(r"protected\s+function\s+\w+", content, re.IGNORECASE)
                ),
                "public_methods": len(
                    re.findall(r"public\s+function\s+\w+", content, re.IGNORECASE)
                ),
            }

            return structure

        except Exception as e:
            print(f"Code structure analysis failed: {e}")
            return {}
