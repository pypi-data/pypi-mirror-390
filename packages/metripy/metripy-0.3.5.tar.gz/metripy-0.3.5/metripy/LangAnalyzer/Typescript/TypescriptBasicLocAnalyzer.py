class TypescriptBasicLocAnalyzer:
    @staticmethod
    def get_loc_metrics(code: str, filename: str) -> dict:
        """Fallback LOC calculation using manual analysis"""
        try:
            lines = code.split("\n")

            total_lines = len(lines)
            blank_lines = TypescriptBasicLocAnalyzer._count_blank_lines(lines)
            comment_lines = TypescriptBasicLocAnalyzer._count_comment_lines(lines)
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
