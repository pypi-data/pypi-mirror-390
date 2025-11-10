"""
Click metadata extraction from AST.

This module extracts argument metadata from Click-based CLI definitions.
"""

import ast
from typing import Any, Optional


class ClickMetadataExtractor:
    """
    Extract metadata from Click decorator definitions.

    Analyzes function decorators to find @click.option() and @click.argument() calls.
    """

    def extract(self, func_node: ast.FunctionDef) -> list[dict[str, Any]]:
        """
        Extract argument metadata from Click-decorated function.

        Args:
            func_node: AST FunctionDef node with Click decorators

        Returns:
            List of argument metadata dictionaries with fields:
            - name: str
            - type: str ("int", "str", "float", "bool", or None)
            - default: Any
            - required: bool
            - help: str or None
            - choices: list or None

        """
        arguments = []

        # Process decorators in reverse order (bottom to top execution)
        for decorator in reversed(func_node.decorator_list):
            if isinstance(decorator, ast.Call):
                arg_meta = self._extract_from_decorator(decorator)
                if arg_meta:
                    arguments.append(arg_meta)

        return arguments

    def _extract_from_decorator(self, decorator: ast.Call) -> Optional[dict[str, Any]]:
        """Extract metadata from @click.option() or @click.argument()."""
        func = decorator.func

        # Check if it's @click.option() or @click.argument()
        if not isinstance(func, ast.Attribute):
            return None

        if func.attr not in ("option", "argument"):
            return None

        if not isinstance(func.value, ast.Name) or func.value.id != "click":
            return None

        # First positional arg is the option/argument name
        if not decorator.args:
            return None

        arg_name_node = decorator.args[0]
        if not isinstance(arg_name_node, ast.Constant):
            return None

        arg_name = arg_name_node.value
        if not isinstance(arg_name, str):
            return None

        # Remove leading dashes
        clean_name = arg_name.lstrip("-")

        # Initialize metadata
        metadata: dict[str, Any] = {
            "name": clean_name,
            "type": None,
            "default": None,
            "required": func.attr == "argument",  # arguments are required by default
            "help": None,
            "choices": None,
        }

        # Extract keyword arguments
        for keyword in decorator.keywords:
            if keyword.arg == "type":
                metadata["type"] = self._extract_type(keyword.value)
            elif keyword.arg == "default":
                metadata["default"] = self._extract_value(keyword.value)
            elif keyword.arg == "required":
                metadata["required"] = self._extract_bool(keyword.value)
            elif keyword.arg == "help":
                metadata["help"] = self._extract_string(keyword.value)
            elif keyword.arg == "type" and self._is_choice_type(keyword.value):
                metadata["choices"] = self._extract_choices(keyword.value)

        return metadata

    def _extract_type(self, node: ast.expr) -> Optional[str]:
        """Extract type from AST node."""
        # Handle type=click.INT, type=click.STRING, etc.
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "click"
        ):
            type_attr = node.attr.lower()
            if type_attr in ("int", "string", "float", "bool"):
                # Normalize STRING to str
                return "str" if type_attr == "string" else type_attr

        # Handle type=int, type=str (direct Python types)
        if isinstance(node, ast.Name) and node.id in ("int", "str", "float", "bool"):
            return node.id

        return None

    def _is_choice_type(self, node: ast.expr) -> bool:
        """Check if type is click.Choice()."""
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "Choice"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "click"
        )

    def _extract_choices(self, node: ast.expr) -> Optional[list[Any]]:
        """Extract choices from click.Choice() call."""
        if not isinstance(node, ast.Call):
            return None

        # First positional arg is the choices list
        if not node.args:
            return None

        choices_node = node.args[0]
        if isinstance(choices_node, ast.List):
            choices = []
            for elt in choices_node.elts:
                if isinstance(elt, ast.Constant):
                    choices.append(elt.value)
            return choices if choices else None

        return None

    def _extract_value(self, node: ast.expr) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        return None

    def _extract_bool(self, node: ast.expr) -> bool:
        """Extract boolean from AST node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return node.value
        return False

    def _extract_string(self, node: ast.expr) -> Optional[str]:
        """Extract string from AST node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None
