from metripy.LangAnalyzer.Generic.HalSteadAnalyzer import HalSteadAnalyzer


class PhpHalSteadAnalyzer:
    def __init__(self):
        self.operators = set(
            [
                "+",
                "-",
                "*",
                "/",
                "%",
                "++",
                "--",
                "=",
                "==",
                "!=",
                "===",
                "!==",
                "<",
                ">",
                "<=",
                ">=",
                "&&",
                "||",
                "!",
                ".",
                "->",
                "=>",
                "::",
                "?",
                ":",
                "&",
                "|",
                "^",
                "~",
                "<<",
                ">>",
            ]
        )
        self.analyzer = HalSteadAnalyzer(self.operators)

    def calculate_halstead_metrics(self, code: str):
        return self.analyzer.calculate_halstead_metrics(code)
