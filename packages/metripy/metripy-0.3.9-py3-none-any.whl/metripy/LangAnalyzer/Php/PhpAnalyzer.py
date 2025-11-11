import math
import os
import re
import tempfile
from pathlib import Path

import lizard

from metripy.Component.Output.ProgressBar import ProgressBar
from metripy.LangAnalyzer.AbstractLangAnalyzer import AbstractLangAnalyzer
from metripy.LangAnalyzer.Php.PhpBasicAstParser import PhpBasicAstParser
from metripy.LangAnalyzer.Php.PhpBasicLocAnalyzer import PhpBasicLocAnalyzer
from metripy.LangAnalyzer.Php.PhpHalSteadAnalyzer import PhpHalSteadAnalyzer
from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode
from metripy.Tree.ModuleNode import ModuleNode


class PhpAnalyzer(AbstractLangAnalyzer):
    def __init__(self):
        super().__init__()
        self.loc_analyzer = PhpBasicLocAnalyzer()
        self.halstead_analyzer = PhpHalSteadAnalyzer()

    def get_lang_name(self) -> str:
        return "PHP"

    def set_files(self, files: list[str]) -> None:
        self.files = list(filter(lambda file: file.endswith(".php"), files))

    def is_needed(self) -> bool:
        return len(self.files) > 0

    def run(self, progress_bar: ProgressBar) -> None:
        for file in self.files:
            with open(file, "r") as f:
                code = f.read()
                self.analyze(code, file)
            progress_bar.advance()

    @staticmethod
    def full_name(
        filename: str, item_name: str | None = None, class_name: str | None = None
    ) -> str:
        if class_name is None:
            if item_name is None:
                return filename
            return f"{filename}:{item_name}"
        return f"{filename}:{class_name}:{item_name}"

    def _create_lizard_analyzable_file(self, filename: str) -> str:
        """
        Because of a bug in lizard it cannot correctly analyze traits.
        See https://github.com/terryyin/lizard/issues/441
        Because of a bug in lizard we need to replace use function statements.
        See https://github.com/terryyin/lizard/issues/442
        """
        tmp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".php")
        with open(filename, "r") as f:
            code = f.readlines()
            code = [re.sub(r"^(\s*)trait\s+", r"\1class ", line) for line in code]
            # use remove the function keyword, so it gets counted the same way and dont increate blank lines / lower loc
            code = [
                re.sub(r"^(\s*)use\s+function\s+", r"\1use ", line) for line in code
            ]
            tmp_file.writelines(code)
            tmp_file.close()
        return tmp_file.name

    def analyze(self, code: str, filename: str) -> None:
        file_stem = Path(filename).stem
        structure = PhpBasicAstParser.parse_php_structure(code)

        is_tmp_file = False
        filename_to_analyze = filename
        if "trait" in filename.lower() or "use function" in code:
            filename_to_analyze = self._create_lizard_analyzable_file(filename)
            is_tmp_file = True

        lizard_result = lizard.analyze_file(filename_to_analyze)
        complexity_data = {
            func.name: {
                "complexity": func.cyclomatic_complexity,
                "start_line": func.start_line,
                "end_line": func.end_line,
            }
            for func in lizard_result.function_list
        }

        if is_tmp_file:
            os.unlink(filename_to_analyze)

        classes: dict[str, ClassNode] = {}
        functions: dict[str, FunctionNode] = {}
        for obj in structure:
            if obj["type"] == "class":
                full_name = self.full_name(filename, obj["name"])
                classes[full_name] = ClassNode(
                    full_name,
                    obj["name"],
                    obj["line"],
                    0,
                    0,  # gets filled in later, based on methods
                )
            elif obj["type"] == "method" or obj["type"] == "function":
                full_name = self.full_name(filename, obj["name"])
                try:
                    function_node = FunctionNode(
                        full_name,
                        obj["name"],
                        obj["line"],
                        0,
                        complexity_data[f"{file_stem}::{obj['name']}"]["complexity"],
                    )
                    function_node.line_end = complexity_data[
                        f"{file_stem}::{obj['name']}"
                    ]["end_line"]
                except KeyError:
                    # no complexity data, function must be empty
                    function_node = FunctionNode(
                        full_name,
                        obj["name"],
                        obj["line"],
                        0,
                        0,
                    )

                if obj["type"] == "method":
                    class_name = obj["class"]
                    full_class_name = self.full_name(filename, class_name)
                    class_node = classes.get(full_class_name)
                    if class_node is not None:
                        class_node.functions.append(function_node)
                    else:
                        raise ValueError(
                            f"Class node not found for function {full_class_name}"
                        )
                functions[full_name] = function_node

        # complexity of classes
        for class_node in classes.values():
            class_node.real_complexity = sum(
                [func.complexity for func in class_node.functions]
            )

        loc_data = self.loc_analyzer.get_loc_metrics(code, filename)

        full_name = self.full_name(filename)
        module_node = ModuleNode(
            full_name,
            loc_data.get("lines", 0),
            loc_data.get("linesOfCode", 0),
            loc_data.get("logicalLinesOfCode", 0),
            loc_data.get("commentLines", 0),
            0,  # multi-line comments - not directly available
            loc_data.get("linesOfCode", 0) - loc_data.get("logicalLinesOfCode", 0),
            loc_data.get("commentLines", 0),
        )
        module_node.classes.extend(classes.values())
        module_node.functions.extend(functions.values())

        code_lines = code.split("\n")
        for func_name, function_node in functions.items():
            lines = code_lines[function_node.lineno : function_node.line_end]
            function_metrics = self.halstead_analyzer.calculate_halstead_metrics(
                "\n".join(lines)
            )
            function_node.h1 = function_metrics["n1"]
            function_node.h2 = function_metrics["n2"]
            function_node.N1 = function_metrics["N1"]
            function_node.N2 = function_metrics["N2"]
            function_node.vocabulary = function_metrics["vocabulary"]
            function_node.length = function_metrics["length"]
            function_node.volume = function_metrics["volume"]
            function_node.difficulty = function_metrics["difficulty"]
            function_node.effort = function_metrics["effort"]
            function_node.calculated_length = function_metrics["calculated_length"]
            function_node.bugs = function_metrics["bugs"]
            function_node.time = function_metrics["time"]
            function_node.calc_mi()

        maintainability_index = self._calculate_maintainability_index(
            functions.values(), module_node
        )
        module_node.maintainability_index = maintainability_index
        self.modules[full_name] = module_node

    def _calculate_maintainability_index(
        self, functions: list[FunctionNode], module_node: ModuleNode
    ) -> float:
        """Calculate maintainability index for PHP"""
        if not functions:
            return 100.0

        total_volume = sum(func.volume for func in functions)
        total_complexity = sum(func.complexity for func in functions)
        total_length = sum(func.length for func in functions)

        if total_volume == 0 or total_length == 0:
            return 100.0

        # PHP maintainability index calculation
        mi_base = max(
            (
                171
                - 5.2 * math.log(total_volume)
                - 0.23 * total_complexity
                - 16.2 * math.log(total_length)
            )
            * 100
            / 171,
            0,
        )

        # Comment weight
        comment_weight = 0
        if module_node.loc > 0:
            comment_ratio = module_node.single_comments / module_node.loc
            comment_weight = 50 * math.sin(math.sqrt(2.4 * comment_ratio))

        return mi_base + comment_weight

    def get_metrics(self) -> list[FileMetrics]:
        return super().get_metrics()
