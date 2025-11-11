import os
from datetime import datetime

from py_template_engine import TemplateEngine

from metripy.Application.Info import Info


class PageRenderer:
    def __init__(self, template_dir: str, output_dir: str, project_name: str):
        self.template_dir = template_dir
        self.output_dir = output_dir

        self.global_template_args = {
            "project_name": project_name,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "author": "Metripy",
            "version": Info().get_version(),
        }

    @staticmethod
    def _stringify_values(obj):
        if isinstance(obj, dict):
            return {
                key: PageRenderer._stringify_values(value) for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [PageRenderer._stringify_values(item) for item in obj]
        else:
            return str(obj)

    def render_template(self, template_name: str, data: dict):
        data = self._stringify_values(
            {
                **self.global_template_args,
                **data,
            }
        )
        engine = TemplateEngine(os.path.join(self.template_dir, template_name))
        content = engine.render(**data)
        with open(os.path.join(self.output_dir, template_name), "w") as file:
            file.write(content)
