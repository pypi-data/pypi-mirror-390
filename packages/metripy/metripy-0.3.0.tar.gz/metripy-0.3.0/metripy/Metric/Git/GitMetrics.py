from metripy.Metric.Git.GitCodeHotspot import GitCodeHotspot
from metripy.Metric.Git.GitContributor import GitContributor
from metripy.Metric.Git.GitKnowledgeSilo import GitKnowledgeSilo


class GitMetrics:
    def __init__(
        self,
        analysis_start_date: str,
        commit_stats_per_month: dict[str, int],
        churn_per_month: dict[str, dict[str, int]],
        contributor_stats: dict[str, dict[str, int]],
        file_contributors: dict[str, dict[str, int]],
    ):
        self.analysis_start_date = analysis_start_date
        self._commit_stats_per_month: dict[str, int] = commit_stats_per_month
        self._churn_per_month: dict[str, dict[str, int]] = churn_per_month
        self._contributor_stats = contributor_stats
        self.total_commits = sum(data["commits"] for data in contributor_stats.values())
        self.contributors: list[GitContributor] = self._calc_contributors(
            contributor_stats
        )
        self.core_contributors, self.core_percentage = self._calc_core_contributors(
            self.contributors
        )
        self.silos: list[GitKnowledgeSilo] = self._calc_silos(file_contributors)
        self.hotspots: list[GitCodeHotspot] = self._calc_hotspots(file_contributors)

    def get_analysis_start_date(self) -> str:
        return self.analysis_start_date

    def get_commit_stats_per_month(self) -> dict[str, int]:
        return self._commit_stats_per_month

    def get_churn_per_month(self) -> dict[str, dict[str, int]]:
        return self._churn_per_month

    def get_avg_commit_size(self) -> float:
        return (
            sum(
                data["lines_added"] + data["lines_removed"]
                for data in self._contributor_stats.values()
            )
            / self.total_commits
        )

    def get_contributors_dict(self) -> dict[str, dict[str, int]]:
        return {
            contributor.name: contributor.to_dict() for contributor in self.contributors
        }

    def get_contributors_list(self) -> list[dict[str, int]]:
        return [contributor.to_dict() for contributor in self.contributors]

    def get_hotspots_list(self) -> list[dict[str, int]]:
        return [hotspot.to_dict() for hotspot in self.hotspots]

    def get_silos_dict(self) -> dict[str, dict[str, int]]:
        return {silo.file_path: silo.to_dict() for silo in self.silos}

    def get_silos_list(self) -> list[dict[str, int]]:
        return [silo.to_dict() for silo in self.silos]

    def _calc_hotspots(
        self, file_contributors: dict[str, dict[str, int]]
    ) -> list[GitCodeHotspot]:
        hotspots = []
        for file_path, data in file_contributors.items():
            changes_count = data["commits"]
            if changes_count < 10:
                continue
            hotspots.append(
                GitCodeHotspot(
                    file_path=file_path,
                    changes_count=changes_count,
                    contributors_count=len(data["contributors"]),
                )
            )
        return sorted(hotspots, key=lambda x: x.changes_count, reverse=True)

    def _calc_contributors(
        self, contributor_stats: dict[str, dict[str, int]]
    ) -> list[GitContributor]:
        # determine top contributors
        total_commits = self.total_commits
        contributors = []

        for name, data in contributor_stats.items():
            percentage = (
                (data["commits"] / total_commits * 100) if total_commits > 0 else 0
            )
            contributors.append(
                GitContributor(
                    name=name,
                    commits_count=data["commits"],
                    lines_added=data["lines_added"],
                    lines_removed=data["lines_removed"],
                    contribution_percentage=int(percentage),
                )
            )

        return sorted(contributors, key=lambda x: x.commits_count, reverse=True)

    def _calc_core_contributors(
        self, contributors: list[GitContributor]
    ) -> tuple[int, int]:
        # Calculate core contributors (top contributors making up 67% of commits)
        core_contributors = 0
        core_percentage = 0
        for contributor in contributors:
            core_percentage += contributor.contribution_percentage
            core_contributors += 1
            if core_percentage >= 67:
                break
        core_percentage = min(67, core_percentage)

        return core_contributors, core_percentage

    def _calc_silos(
        self, file_contributors: dict[str, dict[str, int]]
    ) -> list[GitKnowledgeSilo]:
        silos = []
        for file_path, data in file_contributors.items():
            if len(data["contributors"]) > 1 or data["commits"] < 3:
                continue
            owner = list(data["contributors"])[0]
            silos.append(
                GitKnowledgeSilo(
                    file_path=file_path,
                    owner=owner,
                    commits_count=data["commits"],
                )
            )
        return sorted(silos, key=lambda x: x.commits_count, reverse=True)

    def to_dict(self) -> dict[str, any]:
        return {
            "analysis_start_date": self.analysis_start_date,
            "avg_commit_size": round(self.get_avg_commit_size(), 2),
            "commit_stats_per_month": self.get_commit_stats_per_month(),
            "churn_per_month": self.get_churn_per_month(),
            "total_commits": self.total_commits,
            "active_contributors": len(self.contributors),
            "contributors": self.get_contributors_dict(),
            "core_contributors": self.core_contributors,
            "core_percentage": self.core_percentage,
            "silos": self.get_silos_list(),
        }
