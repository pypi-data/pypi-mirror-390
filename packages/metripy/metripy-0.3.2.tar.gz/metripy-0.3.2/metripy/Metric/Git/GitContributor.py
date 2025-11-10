class GitContributor:
    def __init__(
        self,
        name: str,
        commits_count: int,
        lines_added: int,
        lines_removed: int,
        contribution_percentage: int,
    ):
        self.name = name
        self.initials = self._get_initials(name)
        self.commits_count = commits_count
        self.lines_added = lines_added
        self.lines_removed = lines_removed
        self.contribution_percentage = contribution_percentage

    def _get_initials(self, name: str) -> str:
        try:
            parts = name.split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[1][0]).upper()
            elif len(parts) == 1:
                return parts[0][:2].upper()
            else:
                return "UN"
        except Exception:
            return "UN"

    def to_dict(self) -> dict[str, int]:
        return {
            "name": self.name,
            "initials": self.initials,
            "commits_count": self.commits_count,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "contribution_percentage": self.contribution_percentage,
        }
