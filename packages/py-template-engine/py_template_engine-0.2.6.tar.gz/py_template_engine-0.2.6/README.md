# 🚀 Python Template Engine

A powerful, lightweight template engine for Python with support for variables, functions, conditionals, loops, and file includes. Built for simplicity and extensibility.

[![PyPI version](https://img.shields.io/pypi/v/py-template-engine.svg)](https://pypi.org/project/py-template-engine/)
[![Tests](https://img.shields.io/badge/tests-75%20passed-brightgreen)](./tests)
[![Coverage](https://codecov.io/gh/zimmer-yan/py-template-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/zimmer-yan/py-template-engine)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/py-template-engine.svg)](https://pypi.org/project/py-template-engine/)

## ✨ Features

- 🔤 **Variable substitution** - `{{name}}`, `{{user.email}}`
- ⚡ **Function calls** - `{{get_time()}}`, `{{utils.format()}}`
- 🔀 **Conditionals** - `{{#IF condition}}...{{#ELSE}}...{{/IF}}`
- 🔄 **Loops** - `{{#EACH items AS item}}...{{/EACH}}`
- 📄 **File includes** - `{{#INCLUDE file_path}}`
- 🎨 **Template rendering** - `{{#RENDER template_path}}`
- 🧪 **Fully tested** - Comprehensive test suite with 73 tests
- 🎯 **Type hints** - Full type annotation support
- 🏗️ **Extensible** - Modular architecture for custom engines

## 🚀 Quick Start

### Installation

#### **From PyPI (Recommended)**
```bash
# Install from PyPI
pip install py-template-engine
```

#### **From Source**
```bash
# Clone the repository
git clone https://github.com/zimmer-yan/py-template-engine.git
cd py-template-engine

# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

#### **Direct from GitHub**
```bash
# Install directly from GitHub
pip install git+https://github.com/zimmer-yan/py-template-engine.git
```

### Basic Usage

```python
from py_template_engine import TemplateEngine

# Simple variable substitution
template = "Hello {{name}}!"
engine = TemplateEngine(template_string=template)
result = engine.render(name="World")
print(result)  # Output: Hello World!
```

## 📖 Template Syntax

### Variables
```html
<!-- Basic variables -->
<h1>{{title}}</h1>
<p>Welcome {{user.name}}!</p>

<!-- Nested object access -->
<span>{{user.profile.email}}</span>
```

### Functions
```html
<!-- Function calls -->
<p>Current time: {{get_time()}}</p>
<p>Formatted date: {{utils.format_date()}}</p>
```

### Conditionals
```html
<!-- IF/ELSE statements -->
{{#IF user_logged_in}}
    <p>Welcome back, {{username}}!</p>
{{#ELSE}}
    <p>Please log in to continue</p>
{{/IF}}

<!-- Nested conditions -->
{{#IF user}}
    {{#IF user.is_premium}}
        <span class="premium">Premium User</span>
    {{/IF}}
{{/IF}}
```

### Loops
```html
<!-- EACH loops -->
<ul>
{{#EACH items AS item}}
    <li>{{item}}</li>
{{/EACH}}
</ul>

<!-- Loop with objects -->
{{#EACH users AS user}}
    <div class="user">
        <h3>{{user.name}}</h3>
        <p>{{user.email}}</p>
    </div>
{{/EACH}}
```

### File Operations
```html
<!-- Include raw file content -->
{{#INCLUDE includes/header.html}}

<!-- Render template with full processing -->
{{#RENDER user_template}}
```

## 💡 Advanced Examples

### Complete Web Page Template

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{page_title}}</title>
</head>
<body>
    {{#INCLUDE header.html}}
    
    <main>
        {{#IF featured_posts}}
            <section class="featured">
                <h2>Featured Posts</h2>
                {{#EACH featured_posts AS post}}
                    <article>
                        <h3>{{post.title}}</h3>
                        <p>{{post.excerpt}}</p>
                        <time>{{post.format_date()}}</time>
                    </article>
                {{/EACH}}
            </section>
        {{/IF}}
        
        {{#RENDER templates/blog_content.html}}
    </main>
    
    {{#INCLUDE footer.html}}
</body>
</html>
```

```python
from py_template_engine import TemplateEngine

engine = TemplateEngine(template_path="page.html")
result = engine.render(
    page_title="My Blog",
    featured_posts=[
        {
            "title": "Getting Started",
            "excerpt": "Learn the basics...",
            "format_date": lambda: "2024-01-15"
        }
    ],
)
```

### Dynamic Dashboard

```python
# Context data
dashboard_data = {
    "user": {
        "name": "Alice Johnson",
        "role": "admin",
        "notifications": 5
    },
    "stats": [
        {"label": "Users", "value": 1247},
        {"label": "Revenue", "value": "$52,340"},
        {"label": "Orders", "value": 89}
    ],
    "is_admin": True,
    "get_alert_class": lambda count: "danger" if count > 10 else "info"
}

template = """
<div class="dashboard">
    <h1>Welcome {{user.name}}</h1>
    
    {{#IF is_admin}}
        <div class="admin-panel">
            <h2>Admin Controls</h2>
            <p>Notifications: <span class="{{get_alert_class()}}">{{user.notifications}}</span></p>
        </div>
    {{/IF}}
    
    <div class="stats">
        {{#EACH stats AS stat}}
            <div class="stat-card">
                <h3>{{stat.label}}</h3>
                <p class="value">{{stat.value}}</p>
            </div>
        {{/EACH}}
    </div>
</div>
"""

engine = TemplateEngine(template_string=template)
result = engine.render(**dashboard_data)
```

## 🏗️ API Reference

### TemplateEngine

```python
class TemplateEngine:
    def __init__(self, template_path: Optional[str] = None, 
                 template_string: Optional[str] = None) -> None:
        """
        Initialize template engine with either file path or string.
        
        Args:
            template_path: Path to template file
            template_string: Template content as string
            
        Raises:
            ValueError: If neither template_path nor template_string provided
        """
    
    def render(self, **kwargs) -> str:
        """
        Render template with provided context variables.
        
        Args:
            **kwargs: Template context variables
            
        Returns:
            Rendered template as string
        """
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests with pytest
pytest tests -v

# Run specific test file
python tests/test_template_engine.py

# Run with coverage
pytest tests --cov=py_template_engine
```

**Test Coverage**: 63 tests covering all features:
- Variable substitution (basic + nested)
- Function calls (simple + nested objects)
- Conditional logic (IF/ELSE + nested)
- Loop processing (EACH + complex data)
- File operations (INCLUDE + RENDER)
- Error handling & edge cases

## 🔧 Development

### Project Structure

```
py-templater/
├── py_template_engine/          # Main package
│   ├── __init__.py
│   ├── TemplateEngine.py        # Main engine
│   ├── TemplaterInterface.py
│   └── sub_engines/             # Individual processors
│       ├── VariableTemplater.py
│       ├── FunctionTemplater.py
│       ├── IfTemplater.py
│       ├── EachTemplater.py
│       ├── IncludeTemplater.py
│       └── RenderTemplater.py
├── tests/                       # Test suite
├── examples/                    # Usage examples
└── pyproject.toml              # Project configuration
```

### Adding Custom Engines

Create custom template processors by extending `TemplaterInterface`:

```python
from py_template_engine.TemplaterInterface import TemplaterInterface
import re

class CustomTemplater(TemplaterInterface):
    def render(self, template: str, **kwargs) -> str:
        return re.sub(
            r'{{#CUSTOM (.*?)}}',
            lambda m: self.process(m.group(1), **kwargs),
            template
        )
    
    def process(self, content: str, **kwargs) -> str:
        # Custom processing logic
        return f"Processed: {content}"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest tests`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Happy templating!** 🎉
