import re

from py_template_engine.RenderError import RenderError
from py_template_engine.TemplaterInterface import TemplaterInterface


class IncludeTemplater(TemplaterInterface):
    def render(self, template: str, **kwargs) -> str:
        return re.sub(
            r"{{#INCLUDE (.*?)}}",
            lambda m: self.process(m.group(1).strip(), **kwargs),
            template,
        )

    def process(self, include_path: str, **kwargs) -> str:
        try:
            with open(include_path, "r") as file:
                return file.read()
        except FileNotFoundError as e:
            if self.raise_on_error:
                raise RenderError(
                    f"Trying to include file but could not find path '{include_path}'"
                )
            else:
                return f"{{{{#INCLUDE {include_path}}}}}"
