class GitKnowledgeSilo:
    def __init__(self, file_path: str, owner: str, commits_count: int):
        self.file_path = file_path
        self.owner = owner
        self.commits_count = commits_count
        self.risk_level = self._calc_risk_level(commits_count)
        self.risk_label = self._calc_risk_label(self.risk_level)

    def _calc_risk_level(self, commits_count: int) -> str:
        if commits_count >= 15:
            return "high"
        elif commits_count >= 8:
            return "medium"
        else:
            return "low"

    def _calc_risk_label(self, risk_level: str) -> str:
        return risk_level.capitalize()

    def to_dict(self) -> dict[str, int]:
        return {
            "file_path": f"{self.file_path}",
            "owner": f"{self.owner}",
            "commits_count": f"{self.commits_count}",
            "risk_level": f"{self.risk_level}",
            "risk_label": f"{self.risk_label}",
        }
