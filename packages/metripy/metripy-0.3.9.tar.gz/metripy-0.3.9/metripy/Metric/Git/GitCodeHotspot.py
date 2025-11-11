class GitCodeHotspot:

    def __init__(self, file_path: str, changes_count: int, contributors_count: int):
        self.file_path = file_path
        self.changes_count = changes_count
        self.contributors_count = contributors_count
        self.risk_level = self._calc_risk_level(changes_count, contributors_count)
        self.risk_label = self._label_from_risk_level()

    def _calc_risk_level(self, changes_count: int, contributors_count: int) -> str:
        if changes_count < 10:
            if contributors_count < 5:
                return "low"
            else:
                return "medium"
        elif changes_count < 50:
            if contributors_count < 5:
                return "medium"
            else:
                return "high"
        else:
            if contributors_count < 1:
                return "medium"
            else:
                return "high"

    def _label_from_risk_level(self) -> str:
        return self.risk_level.capitalize()

    def to_dict(self) -> dict[str, str]:
        return {
            "file_path": self.file_path,
            "changes_count": self.changes_count,
            "risk_level": self.risk_level,
            "risk_label": self.risk_label,
            "contributors_count": self.contributors_count,
        }
