class Segmentor:
    @staticmethod
    def get_loc_segment(loc: int) -> str:
        if loc <= 200:
            return "good"
        elif loc <= 500:
            return "ok"
        elif loc <= 1000:
            return "warning"
        else:
            return "critical"

    @staticmethod
    def get_complexity_segment(complexity: float) -> str:
        if complexity <= 5:
            return "good"
        elif complexity <= 10:
            return "ok"
        elif complexity <= 20:
            return "warning"
        else:
            return "critical"

    @staticmethod
    def get_maintainability_segment(maintainability: float) -> str:
        if maintainability > 80:
            return "good"
        elif maintainability > 60:
            return "ok"
        elif maintainability > 40:
            return "warning"
        else:
            return "critical"

    @staticmethod
    def get_method_size_segment(method_size: float) -> str:
        if method_size <= 15:
            return "good"
        elif method_size <= 30:
            return "ok"
        elif method_size <= 50:
            return "warning"
        else:
            return "critical"
