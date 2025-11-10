import re
from functools import reduce

from py_template_engine.RenderError import RenderError
from py_template_engine.TemplaterInterface import TemplaterInterface


class FunctionTemplater(TemplaterInterface):
    def render(self, template: str, **kwargs) -> str:
        return re.sub(
            r"{{(\w+(\.\w+)*)\(\)}}",
            lambda m: self.process(m.group(1).strip(), **kwargs),
            template,
        )

    def process(self, function_name: str, **kwargs) -> str:
        try:
            return reduce(
                lambda acc, part: acc[part], function_name.split("."), kwargs
            )()
        except (KeyError, TypeError) as e:
            if self.raise_on_error:
                raise RenderError(
                    f"Trying to insert function {function_name} but could not find {e}"
                )
            else:
                return f"{{{{{function_name}()}}}}"
