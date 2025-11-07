from metripy.LangAnalyzer.Generic.HalSteadAnalyzer import HalSteadAnalyzer


class PythonHalSteadAnalyzer:
    def __init__(self):
        self.operators = [
            "+",
            "-",
            "*",
            "/",
            "//",
            "%",
            "**",
            "==",
            "!=",
            ">",
            "<",
            ">=",
            "<=",
            "=",
            "+=",
            "-=",
            "*=",
            "/=",
            "%=",
            "//=",
            "**=",
            "and",
            "or",
            "not",
            "&",
            "|",
            "^",
            "~",
            "<<",
            ">>",
            "in",
            "not in",
            "is",
            "is not",
            ":",
            ",",
            ".",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
        ]

        self.analyzer = HalSteadAnalyzer(self.operators)

    def calculate_halstead_metrics(self, code: str):
        return self.analyzer.calculate_halstead_metrics(code)
