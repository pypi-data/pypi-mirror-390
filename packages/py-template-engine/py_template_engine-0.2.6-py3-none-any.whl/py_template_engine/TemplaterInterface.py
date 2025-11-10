from abc import ABC, abstractmethod
from typing import Any, Dict


class TemplaterInterface(ABC):
    def __init__(self, raise_on_error: bool = False):
        self.raise_on_error = raise_on_error

    @abstractmethod
    def render(self, template: str, **kwargs: Dict[str, Any]) -> str:
        raise NotImplementedError
