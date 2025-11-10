import math

import lizard

from metripy.Component.Output.ProgressBar import ProgressBar
from metripy.LangAnalyzer.AbstractLangAnalyzer import AbstractLangAnalyzer
from metripy.LangAnalyzer.Typescript.TypescriptAstParser import TypescriptAstParser
from metripy.LangAnalyzer.Typescript.TypescriptBasicComplexityAnalyzer import (
    TypescriptBasicComplexityAnalzyer,
)
from metripy.LangAnalyzer.Typescript.TypescriptBasicLocAnalyzer import (
    TypescriptBasicLocAnalyzer,
)
from metripy.LangAnalyzer.Typescript.TypescriptHalSteadAnalyzer import (
    TypeScriptHalSteadAnalyzer,
)
from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode
from metripy.Tree.ModuleNode import ModuleNode


class TypescriptAnalyzer(AbstractLangAnalyzer):

    def __init__(self):
        super().__init__()
        self.ast_parser = TypescriptAstParser()
        self.halstead_analyzer = TypeScriptHalSteadAnalyzer()
        self.basic_complexity_analyzer = TypescriptBasicComplexityAnalzyer()

    def get_lang_name(self) -> str:
        return "Typescript"

    def set_files(self, files: list[str]) -> None:
        self.files = list(filter(lambda file: file.endswith((".ts", "js")), files))

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

    def analyze(self, code: str, filename: str) -> None:
        structure = self.ast_parser.extract_structure(code)

        lizard_result = lizard.analyze_file(filename)
        complexity_data = {
            func.name: {
                "complexity": func.cyclomatic_complexity,
                "start_line": func.start_line,
                "end_line": func.end_line,
            }
            for func in lizard_result.function_list
        }

        classes: dict[str, ClassNode] = {}
        functions: dict[str, FunctionNode] = {}

        for func_name in structure["functions"]:
            full_name = self.full_name(filename, func_name)
            try:
                function_complexity_data = complexity_data[func_name]
            except KeyError as e:
                function_complexity_data = (
                    self.basic_complexity_analyzer.get_complexity(code, func_name)
                )
                if function_complexity_data is None:
                    print(
                        f"error for function {full_name}: no lizard complexity data, basic analyzer also failed: '{e}'"
                    )
                    continue
            function_node = FunctionNode(
                full_name,
                func_name,
                function_complexity_data["start_line"],
                0,
                function_complexity_data["complexity"],
            )
            functions[full_name] = function_node

        for class_name, method_names in structure["classes"].items():
            full_name = self.full_name(filename, class_name)
            class_node = ClassNode(
                full_name,
                class_name,
                0,
                0,
                0.0,  # gets filled in later based on methods
            )
            classes[full_name] = class_node
            for func_name in method_names:
                full_name = self.full_name(filename, func_name, class_name)
                try:
                    function_complexity_data = complexity_data[func_name]
                except KeyError as e:
                    function_complexity_data = (
                        self.basic_complexity_analyzer.get_complexity(code, func_name)
                    )
                    if function_complexity_data is None:
                        print(
                            f"error for method {full_name}: no lizard complexity data, basic analyzer also failed: '{e}'"
                        )
                        continue
                function_node = FunctionNode(
                    full_name,
                    func_name,
                    function_complexity_data["start_line"],
                    function_complexity_data["end_line"],
                    function_complexity_data["complexity"],
                )
                class_node.functions.append(function_node)
                functions[full_name] = function_node

        # complexity of classes
        for class_node in classes.values():
            class_node.real_complexity = sum(
                [func.complexity for func in class_node.functions]
            )

        loc_data = TypescriptBasicLocAnalyzer.get_loc_metrics(code, filename)

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

    def get_metrics(self):
        return super().get_metrics()
