class ClassTrendMetric:
    def __init__(
        self,
        historical_lineno: int,
        lineno: int,
        historical_real_complexity: int,
        real_complexity: int,
    ):
        self.historical_lineno = historical_lineno
        self.lineno_delta = lineno - historical_lineno
        self.historical_real_complexity = historical_real_complexity
        self.real_complexity_delta = real_complexity - historical_real_complexity

    def to_dict(self) -> dict:
        return {
            "historical_lineno": self.historical_lineno,
            "lineno_delta": self.lineno_delta,
            "historical_real_complexity": self.historical_real_complexity,
            "real_complexity_delta": self.real_complexity_delta,
        }
