import os
from unittest import TestCase

from py_template_engine.TemplateEngine import TemplateEngine


class TestTemplateEngine(TestCase):

    def test_variable_templating(self):
        """Test basic variable substitution."""
        template = "Hello {{name}}!"
        engine = TemplateEngine(template_string=template)
        result = engine.render(name="World")
        self.assertEqual(result, "Hello World!")

    def test_nested_variable_templating(self):
        """Test nested object variable substitution."""
        template = "Hello {{user.name}}!"
        engine = TemplateEngine(template_string=template)
        result = engine.render(user={"name": "Alice"})
        self.assertEqual(result, "Hello Alice!")

    def test_function_templating(self):
        """Test function execution in templates."""
        template = "Current time: {{get_time()}}"
        engine = TemplateEngine(template_string=template)
        result = engine.render(get_time=lambda: "12:00 PM")
        self.assertEqual(result, "Current time: 12:00 PM")

    def test_if_templating_true(self):
        """Test IF condition when true."""
        template = "{{#IF show_message}}<p>Hello!</p>{{/IF}}"
        engine = TemplateEngine(template_string=template)
        result = engine.render(show_message=True)
        self.assertEqual(result, "<p>Hello!</p>")

    def test_if_templating_false(self):
        """Test IF condition when false."""
        template = "{{#IF show_message}}<p>Hello!</p>{{/IF}}"
        engine = TemplateEngine(template_string=template)
        result = engine.render(show_message=False)
        self.assertEqual(result, "")

    def test_if_else_templating(self):
        """Test IF-ELSE conditions."""
        template = "{{#IF logged_in}}Welcome back!{{#ELSE}}Please log in{{/IF}}"
        engine = TemplateEngine(template_string=template)

        result_true = engine.render(logged_in=True)
        self.assertEqual(result_true, "Welcome back!")

        result_false = engine.render(logged_in=False)
        self.assertEqual(result_false, "Please log in")

    def test_each_templating(self):
        """Test EACH loop templating."""
        template = "{{#EACH items AS item}}<li>{{item}}</li>{{/EACH}}"
        engine = TemplateEngine(template_string=template)
        result = engine.render(items=["Apple", "Banana"])
        self.assertEqual(result, "<li>Apple</li><li>Banana</li>")

    def test_complex_template(self):
        """Test a complex template with multiple features."""
        template = """
        {{#IF user}}
            <h1>Hello {{user.name}}!</h1>
            {{#EACH user.items AS item}}
                <p>Item: {{item}}</p>
            {{/EACH}}
        {{#ELSE}}
            <p>Please log in</p>
        {{/IF}}
        """
        engine = TemplateEngine(template_string=template)

        result = engine.render(user={"name": "Alice", "items": ["Book", "Pen"]})

        # Check that all parts are present (whitespace-agnostic)
        self.assertIn("Hello Alice!", result)
        self.assertIn("Item: Book", result)
        self.assertIn("Item: Pen", result)

    def test_complex_template_with_nested_conditions(self):
        """Test a complex template with nested IF conditions in EACH loop."""
        template = """{{#EACH user.items AS item}}{{#IF item.name}}<p>Item: {{item.name}}</p>{{#ELSE}}<p>No item name</p>{{/IF}}{{/EACH}}"""
        engine = TemplateEngine(template_string=template)
        result = engine.render(user={"items": [{"name": "Book"}, {"name": ""}]})
        self.assertEqual(result, "<p>Item: Book</p><p>No item name</p>")

    def test_include_functionality(self):
        """Test INCLUDE directive with temporary files."""
        import tempfile

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("<header>Welcome!</header>")
            temp_file_path = f.name

        try:
            template = f"{{{{#INCLUDE {temp_file_path}}}}}"
            engine = TemplateEngine(template_string=template)
            result = engine.render()
            self.assertEqual(result, "<header>Welcome!</header>")
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_render_functionality(self):
        """Test RENDER directive with temporary template files."""
        import tempfile

        # Create a temporary template file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write("Hello {{name}}!")
            temp_template_path = f.name

        try:
            template = f"{{{{#RENDER {temp_template_path}}}}}"
            engine = TemplateEngine(template_string=template)
            result = engine.render(name="World")
            self.assertEqual(result, "Hello World!")
        finally:
            # Clean up
            os.unlink(temp_template_path)

    def test_nested_object_functions(self):
        """Test nested object function calls."""
        template = "Time: {{utils.get_time()}}"
        engine = TemplateEngine(template_string=template)

        utils = {"get_time": lambda: "14:30"}

        result = engine.render(utils=utils)
        self.assertEqual(result, "Time: 14:30")

    def test_empty_template(self):
        """Test rendering template with minimal content."""
        template = " "  # Minimal whitespace content
        engine = TemplateEngine(template_string=template)
        result = engine.render()
        self.assertEqual(result, " ")

    def test_template_constructor_validation(self):
        """Test that TemplateEngine constructor validates input properly."""
        # Test that empty string raises ValueError
        with self.assertRaises(ValueError):
            TemplateEngine(template_string="")

        # Test that None values raise ValueError
        with self.assertRaises(ValueError):
            TemplateEngine()

    def test_template_with_no_directives(self):
        """Test template with just plain text."""
        template = "<h1>Static Content</h1>"
        engine = TemplateEngine(template_string=template)
        result = engine.render()
        self.assertEqual(result, "<h1>Static Content</h1>")
