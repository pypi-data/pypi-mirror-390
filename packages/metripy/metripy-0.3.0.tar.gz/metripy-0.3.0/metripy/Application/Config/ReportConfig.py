class ReportConfig:
    def __init__(self, report_type: str, path: str) -> None:
        self.type = report_type
        self.path = path

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "path": self.path,
        }
