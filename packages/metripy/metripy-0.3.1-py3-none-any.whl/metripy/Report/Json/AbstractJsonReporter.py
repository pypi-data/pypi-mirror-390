import json
import os

from metripy.Report.ReporterInterface import ReporterInterface


class AbstractJsonReporter(ReporterInterface):
    def put_data(self, data: dict) -> None:
        os.makedirs(os.path.dirname(self.config.path), exist_ok=True)
        with open(self.config.path, "w") as file:
            json.dump(data, file, indent=2)
