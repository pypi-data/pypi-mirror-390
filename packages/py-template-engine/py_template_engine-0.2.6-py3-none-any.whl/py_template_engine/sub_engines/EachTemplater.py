import re
from functools import reduce

from py_template_engine.TemplaterInterface import TemplaterInterface


class EachTemplater(TemplaterInterface):
    def render(self, template: str, **kwargs) -> str:
        return re.sub(
            r"{{#EACH\s+([^}]+)\s+AS\s+([^}]+)}}([\s\S]*?){{/EACH}}",
            lambda m: self.process(
                m.group(1).strip(), m.group(2).strip(), m.group(3), **kwargs
            ),
            template,
        )

    def process(
        self, list_name: str, item_name: str, item_template: str, **kwargs
    ) -> str:
        # Import here to avoid circular import
        from py_template_engine.TemplateEngine import TemplateEngine

        return "".join(
            [
                TemplateEngine(template_string=item_template).render(
                    **{**kwargs, item_name: item}
                )
                for item in reduce(
                    lambda acc, part: acc[part], list_name.split("."), kwargs
                )
            ]
        )
