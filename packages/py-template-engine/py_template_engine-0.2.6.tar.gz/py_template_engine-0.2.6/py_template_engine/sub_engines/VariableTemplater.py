import re
from functools import reduce

from py_template_engine.RenderError import RenderError
from py_template_engine.TemplaterInterface import TemplaterInterface


class VariableTemplater(TemplaterInterface):
    def render(self, template: str, **kwargs) -> str:
        return re.sub(
            r"{{(.*?)}}",
            lambda m: self.process(m.group(1).strip(), **kwargs),
            template,
        )

    def process(self, variable_name: str, **kwargs) -> str:
        try:
            return reduce(lambda acc, part: acc[part], variable_name.split("."), kwargs)
        except KeyError as e:
            if self.raise_on_error:
                raise RenderError(
                    f"Trying to insert variable {variable_name} but could not find {e}"
                )
            else:
                return f"{{{{{variable_name}}}}}"
        except TypeError as e:
            if self.raise_on_error:
                raise RenderError(
                    f"Trying to insert variable {variable_name} but could not find {e}. It is a {type(e)}"
                )
            else:
                return f"{{{{{variable_name}}}}}"
