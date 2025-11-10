from functools import reduce
from typing import Any, Dict, Optional

from .sub_engines.EachTemplater import EachTemplater
from .sub_engines.FunctionTemplater import FunctionTemplater
from .sub_engines.IfTemplater import IfTemplater
from .sub_engines.IncludeTemplater import IncludeTemplater
from .sub_engines.RenderTemplater import RenderTemplater
from .sub_engines.VariableTemplater import VariableTemplater
from .TemplaterInterface import TemplaterInterface


class TemplateEngine:
    def __init__(
        self, template_path: Optional[str] = None, template_string: Optional[str] = None
    ) -> None:
        if template_path:
            self._load_template(template_path)
        elif template_string:
            self._template = template_string
        else:
            raise ValueError("Either template_path or template_string must be provided")

        self._templaters: list[TemplaterInterface] = [
            IncludeTemplater(),
            RenderTemplater(),
            EachTemplater(),
            IfTemplater(),
            FunctionTemplater(),
            VariableTemplater(),
        ]

    def _load_template(self, template_path: str) -> None:
        with open(template_path, "r") as file:
            self._template = file.read()

    def render(self, **kwargs: Dict[str, Any]) -> str:
        return reduce(
            lambda acc, templater: templater.render(acc, **kwargs),
            self._templaters,
            self._template,
        )

    def add_templater(self, index: int, templater: TemplaterInterface) -> None:
        if index < 0 or index > len(self._templaters):
            raise ValueError("Index out of range")
        self._templaters.insert(index, templater)

    def remove_templater(self, index: int) -> None:
        if index < 0 or index >= len(self._templaters):
            raise ValueError("Index out of range")
        self._templaters.pop(index)
