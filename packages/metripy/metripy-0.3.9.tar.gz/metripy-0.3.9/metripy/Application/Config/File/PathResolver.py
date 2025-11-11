from datetime import datetime

class PathResolver:
    @staticmethod
    def resolve(path: str) -> str:
        return path.format(
            DATE_ISO_8601=datetime.now().strftime("%Y-%m-%d"),
            DATE_YEAR=datetime.now().strftime("%Y"),
            DATE_MONTH=datetime.now().strftime("%m"),
            DATE_DAY=datetime.now().strftime("%d"),
            DATE_HOUR=datetime.now().strftime("%H"),
            DATE_MINUTE=datetime.now().strftime("%M"),
            DATE_SECOND=datetime.now().strftime("%S"),
        )