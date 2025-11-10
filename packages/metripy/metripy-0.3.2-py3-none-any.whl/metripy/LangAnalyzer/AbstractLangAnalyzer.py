from abc import ABC, abstractmethod

from metripy.Metric.Code.FileMetrics import FileMetrics
from metripy.Tree.ModuleNode import ModuleNode


class AbstractLangAnalyzer(ABC):
    def __init__(self):
        self.files: list[str] = []
        self.modules: dict[str, ModuleNode] = {}

    @abstractmethod
    def set_files(self, files: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_needed(self) -> bool:
        pass

    def before_run(self) -> None:
        # build cache
        pass

    def after_run(self) -> None:
        # clear cache
        pass

    @abstractmethod
    def get_lang_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_metrics(self) -> list[FileMetrics]:
        metrics = []
        for module in self.modules.values():
            full_name = module.full_name

            if len(module.functions) > 0:
                totalCc = sum(function.complexity for function in module.functions)
                avgCcPerFunction = totalCc / len(module.functions)
                avgLocPerFunction = (
                    module.lloc - module.comments - len(module.functions)
                ) / len(module.functions)
            else:
                totalCc = 0
                avgCcPerFunction = 0
                avgLocPerFunction = 0
            maintainabilityIndex = module.maintainability_index

            file_metric = FileMetrics(
                full_name=full_name,
                loc=module.loc,
                totalCc=totalCc,
                avgCcPerFunction=avgCcPerFunction,
                maintainabilityIndex=maintainabilityIndex,
                avgLocPerFunction=avgLocPerFunction,
                class_nodes=module.classes,
                function_nodes=module.functions,
            )
            metrics.append(file_metric)

        return metrics
