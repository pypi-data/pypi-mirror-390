import re
from unittest import TestCase

from py_template_engine.TemplateEngine import TemplateEngine
from py_template_engine.TemplaterInterface import TemplaterInterface


class CustomTemplater(TemplaterInterface):
    def render(self, template: str, **kwargs) -> str:
        return re.sub(
            r"{{#CUSTOM (.*?)}}", lambda m: self.process(m.group(1), **kwargs), template
        )

    def process(self, content: str, **kwargs) -> str:
        return f"Processed: {content}"


class TestCustomTemplater(TestCase):
    def test_custom_templating(self):
        """Test custom templating."""
        template = "{{#CUSTOM foo}}!"
        engine = TemplateEngine(template_string=template)
        engine.add_templater(0, CustomTemplater())
        result = engine.render(**{})
        self.assertEqual(result, "Processed: foo!")
