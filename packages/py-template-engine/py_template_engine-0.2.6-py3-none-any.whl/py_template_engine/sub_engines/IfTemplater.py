import re
from functools import reduce
from typing import Any

from py_template_engine.TemplaterInterface import TemplaterInterface


class IfTemplater(TemplaterInterface):
    def render(self, template: str, **kwargs) -> str:
        # Process nested IF blocks recursively by finding innermost blocks first
        max_iterations = 100  # Prevent infinite loops
        iteration_count = 0

        while "{{#IF" in template and iteration_count < max_iterations:
            new_template = self._process_innermost_if_block(template, **kwargs)
            if new_template == template:
                # If no progress was made, break to avoid infinite loop
                break
            template = new_template
            iteration_count += 1

        return template

    def _process_innermost_if_block(self, template: str, **kwargs) -> str:
        """Find and process the innermost IF block that has no nested IF blocks inside it."""

        # Find all IF block starts
        if_starts = []
        pos = 0
        while True:
            pos = template.find("{{#IF", pos)
            if pos == -1:
                break
            if_starts.append(pos)
            pos += 5

        if not if_starts:
            return template

        # For each IF start, find its matching END and check if it's innermost
        for if_start in reversed(
            if_starts
        ):  # Start from the end to find innermost first
            # Find the condition name
            condition_match = re.match(r"{{#IF\s+([^}]+)}}", template[if_start:])
            if not condition_match:
                continue

            condition_name = condition_match.group(1).strip()
            content_start = if_start + condition_match.end()

            # Find matching {{/IF}} and check for {{#ELSE}}
            depth = 1
            pos = content_start
            else_pos = None
            if_content_end = None

            while pos < len(template) and depth > 0:
                # Check for nested IF
                if template[pos:].startswith("{{#IF"):
                    depth += 1
                    pos += 5
                # Check for closing IF
                elif template[pos:].startswith("{{/IF}}"):
                    depth -= 1
                    if depth == 0:
                        if_content_end = pos
                        break
                    pos += 7
                # Check for ELSE at current depth level
                elif (
                    template[pos:].startswith("{{#ELSE}}")
                    and depth == 1
                    and else_pos is None
                ):
                    else_pos = pos
                    pos += 9
                else:
                    pos += 1

            if if_content_end is None:
                continue

            # Check if this is an innermost block (no nested IF blocks in the content)
            if else_pos is not None:
                if_content = template[content_start:else_pos]
                else_content = template[else_pos + 9 : if_content_end]
            else:
                if_content = template[content_start:if_content_end]
                else_content = None

            # Check if this IF block contains nested IF blocks
            if "{{#IF" not in if_content and (
                else_content is None or "{{#IF" not in else_content
            ):
                # This is an innermost block, process it
                result = self.process(
                    condition_name, if_content, else_content, **kwargs
                )

                # Replace this IF block with the result
                end_pos = if_content_end + 7  # +7 for {{/IF}}
                new_template = template[:if_start] + result + template[end_pos:]
                return new_template

        # If no innermost block found, there might be a parsing error
        # Fall back to simple processing of the first IF block
        match = re.search(r"{{#IF\s+([^}]+)}}(.*?){{/IF}}", template, re.DOTALL)
        if match:
            condition_name = match.group(1).strip()
            content = match.group(2)

            # Simple ELSE handling for fallback
            if "{{#ELSE}}" in content:
                parts = content.split("{{#ELSE}}", 1)
                if_content = parts[0]
                else_content = parts[1]
            else:
                if_content = content
                else_content = None

            result = self.process(condition_name, if_content, else_content, **kwargs)
            return template[: match.start()] + result + template[match.end() :]

        return template

    def process(
        self, condition_name: str, if_content: str, else_content: str, **kwargs
    ) -> str:
        try:
            condition = reduce(
                lambda acc, part: acc[part], condition_name.split("."), kwargs
            )
            if self.is_truthy(condition):
                return if_content.strip() if if_content else ""
            elif else_content is not None:
                return else_content.strip()
            else:
                return ""
        except (KeyError, TypeError):
            if else_content is not None:
                return else_content.strip()
            else:
                return ""

    def is_truthy(self, condition: Any) -> bool:
        """
        Check if a condition is truthy
        """
        if condition is None:
            return False
        if isinstance(condition, bool):
            return condition
        if isinstance(condition, str):
            return condition != "" and condition.lower() != "false"
        if isinstance(condition, (int, float)):
            return condition != 0
        if hasattr(condition, "__len__"):
            return len(condition) > 0
        return True
