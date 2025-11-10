class GitConfig:
    def __init__(self):
        self.repo = "./"
        self.branch = "main"

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "branch": self.branch,
        }
