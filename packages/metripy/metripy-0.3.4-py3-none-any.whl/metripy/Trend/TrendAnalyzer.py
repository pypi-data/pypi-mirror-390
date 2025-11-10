from metripy.Metric.Code.AggregatedMetrics import AggregatedMetrics
from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Metric.ProjectMetrics import ProjectMetrics
from metripy.Metric.Trend.AggregatedTrendMetric import AggregatedTrendMetric
from metripy.Metric.Trend.ClassTrendMetric import ClassTrendMetric
from metripy.Metric.Trend.FileTrendMetric import FileTrendMetric
from metripy.Metric.Trend.FunctionTrendMetric import FunctionTrendMetric
from metripy.Tree.ClassNode import ClassNode
from metripy.Tree.FunctionNode import FunctionNode


class TrendAnalyzer:
    def create_file_trend_metric(
        self, file_metric: FileMetrics, historical_file_metric: FileMetrics
    ) -> FileTrendMetric:
        return FileTrendMetric(
            historical_loc=historical_file_metric.loc,
            loc=file_metric.loc,
            historical_totalCc=historical_file_metric.totalCc,
            totalCc=file_metric.totalCc,
            historical_avgCcPerFunction=historical_file_metric.avgCcPerFunction,
            avgCcPerFunction=file_metric.avgCcPerFunction,
            historical_maintainabilityIndex=historical_file_metric.maintainabilityIndex,
            maintainabilityIndex=file_metric.maintainabilityIndex,
            historical_avgLocPerFunction=historical_file_metric.avgLocPerFunction,
            avgLocPerFunction=file_metric.avgLocPerFunction,
        )

    def create_class_trend_metric(
        self, class_metric: ClassNode, historical_class_metric: ClassNode
    ) -> ClassTrendMetric:
        return ClassTrendMetric(
            historical_lineno=historical_class_metric.lineno,
            lineno=class_metric.lineno,
            historical_real_complexity=historical_class_metric.real_complexity,
            real_complexity=class_metric.real_complexity,
        )

    def create_function_trend_metric(
        self, function_metric: FunctionNode, historical_function_metric: FunctionNode
    ) -> FunctionTrendMetric:
        return FunctionTrendMetric(
            historical_loc=historical_function_metric.get_loc(),
            loc=function_metric.get_loc(),
            historical_complexity=historical_function_metric.complexity,
            complexity=function_metric.complexity,
            historical_maintainability_index=historical_function_metric.maintainability_index,
            maintainability_index=function_metric.maintainability_index,
        )

    def add_historical_file_trends(
        self,
        file_metrics: list[FileMetrics],
        historical_file_metrics: list[FileMetrics],
    ):
        indexed_file_metrics = {m.full_name: m for m in file_metrics}
        indexed_historical_file_metrics = {
            m.full_name: m for m in historical_file_metrics
        }

        for full_name, file_metric in indexed_file_metrics.items():
            historical_file_metric = indexed_historical_file_metrics.get(full_name)
            if not historical_file_metric:
                continue
            file_metric.trend = self.create_file_trend_metric(
                file_metric, historical_file_metric
            )

            indexed_class_nodes = {
                n.full_name: n for n in historical_file_metric.class_nodes
            }
            for class_node in file_metric.class_nodes:
                historical_class_node = indexed_class_nodes.get(class_node.full_name)
                if not historical_class_node:
                    continue
                class_node.trend = self.create_class_trend_metric(
                    class_node, historical_class_node
                )

                indexed_function_nodes = {
                    n.full_name: n for n in historical_class_node.functions
                }
                for function_node in class_node.functions:
                    historical_function_node = indexed_function_nodes.get(
                        function_node.full_name
                    )
                    if not historical_function_node:
                        continue
                    function_node.trend = self.create_function_trend_metric(
                        function_node, historical_function_node
                    )

            indexed_function_nodes = {
                n.full_name: n for n in historical_file_metric.function_nodes
            }
            for function_node in file_metric.function_nodes:
                historical_function_node = indexed_function_nodes.get(
                    function_node.full_name
                )
                if not historical_function_node:
                    continue
                function_node.trend = self.create_function_trend_metric(
                    function_node, historical_function_node
                )

    def create_aggregated_trend_metric(
        self,
        aggregated_metric: AggregatedMetrics,
        historical_aggregated_metric: AggregatedMetrics,
    ) -> AggregatedTrendMetric:
        return AggregatedTrendMetric(
            historical_loc=historical_aggregated_metric.loc,
            loc=aggregated_metric.loc,
            historical_avgCcPerFunction=historical_aggregated_metric.avgCcPerFunction,
            avgCcPerFunction=aggregated_metric.avgCcPerFunction,
            historical_maintainabilityIndex=historical_aggregated_metric.maintainabilityIndex,
            maintainabilityIndex=aggregated_metric.maintainabilityIndex,
            historical_avgLocPerFunction=historical_aggregated_metric.avgLocPerFunction,
            avgLocPerFunction=aggregated_metric.avgLocPerFunction,
            historical_num_files=historical_aggregated_metric.num_files,
            num_files=aggregated_metric.num_files,
            historical_segmented_loc=historical_aggregated_metric.segmentation_data[
                "loc"
            ],
            segmented_loc=aggregated_metric.segmentation_data["loc"],
            historical_segmented_complexity=historical_aggregated_metric.segmentation_data[
                "complexity"
            ],
            segmented_complexity=aggregated_metric.segmentation_data["complexity"],
            historical_segmented_maintainability=historical_aggregated_metric.segmentation_data[
                "maintainability"
            ],
            segmented_maintainability=aggregated_metric.segmentation_data[
                "maintainability"
            ],
            historical_segmented_method_size=historical_aggregated_metric.segmentation_data[
                "methodSize"
            ],
            segmented_method_size=aggregated_metric.segmentation_data["methodSize"],
        )

    def add_historical_project_trends(
        self,
        project_metrics: ProjectMetrics,
        historical_project_metrics: ProjectMetrics,
    ):
        project_metrics.total_code_metrics.trend = self.create_aggregated_trend_metric(
            project_metrics.total_code_metrics,
            historical_project_metrics.total_code_metrics,
        )
