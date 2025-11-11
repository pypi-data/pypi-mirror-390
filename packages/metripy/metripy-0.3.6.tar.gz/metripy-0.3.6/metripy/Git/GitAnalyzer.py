from collections import defaultdict
from datetime import datetime

from git import Repo

from metripy.Application.Config.GitConfig import GitConfig
from metripy.Metric.Git.GitMetrics import GitMetrics


class GitAnalyzer:
    def __init__(self, git_config: GitConfig):
        self.repo = Repo(git_config.repo)
        self.branch_name = git_config.branch

    def analyze(self) -> GitMetrics:
        """Main analysis method with comprehensive output"""

        # Calculate first day of this month last year
        now = datetime.now()
        first_of_month_last_year = datetime(now.year - 1, now.month, 1)
        # first_of_month_last_year = datetime(now.year, now.month, 1)
        after_date = first_of_month_last_year.strftime("%Y-%m-%d")

        return self.get_metrics(after_date)

    def _is_source_file(self, file_path: str) -> bool:
        """Check if file is a source code file we want to analyze"""
        source_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".php",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".rb",
            ".go",
            ".rs",
        }
        return any(file_path.endswith(ext) for ext in source_extensions)

    def get_metrics(self, after: str) -> GitMetrics:
        commits_per_month = {}
        chrun_per_month = defaultdict(lambda: {"added": 0, "removed": 0})
        file_contributors = defaultdict(lambda: {"contributors": set(), "commits": 0})
        contributor_stats = defaultdict(
            lambda: {"commits": 0, "lines_added": 0, "lines_removed": 0}
        )

        for commit in self.repo.iter_commits(
            self.branch_name, no_merges=True, after=after
        ):
            month = commit.committed_datetime.strftime("%Y-%m")
            author = commit.author.name

            if month not in commits_per_month.keys():
                commits_per_month[month] = 0
            commits_per_month[month] += 1

            stats = commit.stats.total
            insertions = stats.get("insertions", 0)
            deletions = stats.get("deletions", 0)
            chrun_per_month[month]["added"] += insertions
            chrun_per_month[month]["removed"] += deletions

            contributor_stats[author]["commits"] += 1
            contributor_stats[author]["lines_added"] += insertions
            contributor_stats[author]["lines_removed"] += deletions

            for file_path in commit.stats.files:
                if self._is_source_file(file_path):
                    file_contributors[file_path]["contributors"].add(author)
                    file_contributors[file_path]["commits"] += 1

        return GitMetrics(
            analysis_start_date=after,
            commit_stats_per_month=commits_per_month,
            churn_per_month=chrun_per_month,
            contributor_stats=contributor_stats,
            file_contributors=file_contributors,
        )
