from typing import Self

from metripy.Dependency.Dependency import Dependency
from metripy.Metric.Code.AggregatedMetrics import AggregatedMetrics
from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Metric.Code.SegmentedMetrics import SegmentedMetrics
from metripy.Metric.Git.GitMetrics import GitMetrics


class ProjectMetrics:
    def __init__(
        self,
        file_metrics: list[FileMetrics],
        git_metrics: GitMetrics | None,
        dependencies: list[Dependency] | None,
    ):
        self.file_metrics = file_metrics
        self.git_metrics = git_metrics
        self.dependencies = dependencies
        self.total_code_metrics = self._compile_total_metrics(self.file_metrics)

    def _compile_total_metrics(
        self, file_metrics: list[FileMetrics]
    ) -> AggregatedMetrics:
        files = 0
        locs = []
        avgCcPerFunctions = []
        maintainabilityIndices = []
        avgLocPerFunctions = []
        for file_metric in file_metrics:
            files += 1
            locs.append(file_metric.loc)
            avgCcPerFunctions.append(file_metric.avgCcPerFunction)
            maintainabilityIndices.append(file_metric.maintainabilityIndex)
            avgLocPerFunctions.append(file_metric.avgLocPerFunction)

        if files == 0:
            return AggregatedMetrics()

        return AggregatedMetrics(
            loc=sum(locs),
            avgCcPerFunction=self._avg(avgCcPerFunctions),
            maintainabilityIndex=self._avg(maintainabilityIndices),
            avgLocPerFunction=self._avg(avgLocPerFunctions),
            num_files=files,
            segmented_loc=SegmentedMetrics().set_loc(locs),
            segmented_complexity=SegmentedMetrics().set_complexity(avgCcPerFunctions),
            segmented_maintainability=SegmentedMetrics().set_maintainability(
                maintainabilityIndices
            ),
            segmented_method_size=SegmentedMetrics().set_method_size(
                avgLocPerFunctions
            ),
        )

    def _avg(self, items: list[float | int]) -> float:
        return sum(items) / len(items)

    def to_dict(self) -> dict:
        data = {
            "file_metrics": [m.to_dict() for m in self.file_metrics],
            "aggregated": self.total_code_metrics.to_dict(),
            "aggregated_segmented": self.total_code_metrics.to_dict_segmentation(),
        }
        if self.git_metrics:
            data["git_metrics"] = self.git_metrics.to_dict()
        if self.dependencies:
            data["dependencies"] = [d.to_dict() for d in self.dependencies]
            data["license_distribution"] = Dependency.get_lisence_distribution(
                self.dependencies
            )
        return data

    @staticmethod
    def from_dict(data: dict) -> Self:
        # TODO: not needed yet
        # git_metrics = GitMetrics.from_dict(data["git_metrics"]) if "git_metrics" in data.keys() else None
        # dependencies = [Dependency.from_dict(d) for d in data["dependencies"]] if "dependencies" in data.keys() else None

        return ProjectMetrics(
            file_metrics=[FileMetrics.from_dict(m) for m in data["file_metrics"]],
            git_metrics=None,
            dependencies=None,
        )
