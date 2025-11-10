"""
py-templater:
A Python template engine with support for variables, functions, conditionals, loops, and includes
"""

from .TemplateEngine import TemplateEngine
from .TemplaterInterface import TemplaterInterface

__version__ = "0.1.0"
__author__ = "Yannick Zimmermann"
__email__ = "yannick.zimmermann@proton.me"
__description__ = "A Python template engine with support for variables, functions, conditionals, loops, and includes"

__all__ = [
    "TemplateEngine",
    "TemplaterInterface",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
