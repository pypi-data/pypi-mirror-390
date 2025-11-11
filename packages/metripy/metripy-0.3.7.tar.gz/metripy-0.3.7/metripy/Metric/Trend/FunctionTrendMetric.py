class FunctionTrendMetric:
    def __init__(
        self,
        historical_loc: int,
        loc: int,
        historical_complexity: int,
        complexity: int,
        historical_maintainability_index: float,
        maintainability_index: float,
    ):
        self.historical_loc = historical_loc
        self.loc_delta = loc - historical_loc
        self.historical_complexity = historical_complexity
        self.complexity_delta = complexity - historical_complexity
        self.historical_maintainability_index = historical_maintainability_index
        self.maintainability_index_delta = (
            maintainability_index - historical_maintainability_index
        )

    def to_dict(self) -> dict:
        return {
            "historical_loc": self.historical_loc,
            "loc_delta": self.loc_delta,
            "historical_complexity": self.historical_complexity,
            "complexity_delta": self.complexity_delta,
            "historical_maintainability_index": self.historical_maintainability_index,
            "maintainability_index_delta": self.maintainability_index_delta,
        }
