"""
Typer metadata extraction from AST.

This module extracts argument metadata from Typer-based CLI definitions.
"""

import ast
from typing import Any, Optional


class TyperMetadataExtractor:
    """
    Extract metadata from Typer function definitions.

    Analyzes function parameters with type hints and typer.Option()/typer.Argument() defaults.
    """

    def extract(self, func_node: ast.FunctionDef) -> list[dict[str, Any]]:
        """
        Extract argument metadata from Typer function.

        Args:
            func_node: AST FunctionDef node with Typer-style parameters

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

        # Analyze function parameters
        for arg in func_node.args.args:
            # Skip self/cls parameters
            if arg.arg in ("self", "cls"):
                continue

            metadata: dict[str, Any] = {
                "name": arg.arg,
                "type": None,
                "default": None,
                "required": True,  # Default to required
                "help": None,
                "choices": None,
            }

            # Extract type from type annotation
            if arg.annotation:
                metadata["type"] = self._extract_type_from_annotation(arg.annotation)

            # Check if parameter has a default value
            # Find the default value from func_node.args.defaults
            num_defaults = len(func_node.args.defaults)
            num_args = len(func_node.args.args)
            arg_index = func_node.args.args.index(arg)

            # Defaults are aligned to the right (last parameters)
            if arg_index >= num_args - num_defaults:
                default_index = arg_index - (num_args - num_defaults)
                default_node = func_node.args.defaults[default_index]

                # Check if default is typer.Option() or typer.Argument()
                if isinstance(default_node, ast.Call):
                    typer_info = self._extract_typer_info(default_node)
                    if typer_info:
                        metadata.update(typer_info)
                        # If default is None (from Ellipsis), it's required
                        # Otherwise it has a default value
                        if metadata.get("default") is not None:
                            metadata["required"] = False
                        else:
                            metadata["required"] = True
                else:
                    # Simple default value
                    metadata["default"] = self._extract_value(default_node)
                    metadata["required"] = False

            arguments.append(metadata)

        return arguments

    def _extract_type_from_annotation(self, annotation: ast.expr) -> Optional[str]:
        """Extract type from type annotation."""
        # Handle simple types: int, str, float, bool
        if isinstance(annotation, ast.Name) and annotation.id in (
            "int",
            "str",
            "float",
            "bool",
        ):
            return annotation.id

        # Handle Optional[int] -> extract int
        if (
            isinstance(annotation, ast.Subscript)
            and isinstance(annotation.value, ast.Name)
            and annotation.value.id == "Optional"
        ):
            return self._extract_type_from_annotation(annotation.slice)

        return None

    def _extract_typer_info(self, call_node: ast.Call) -> Optional[dict[str, Any]]:
        """Extract metadata from typer.Option() or typer.Argument() call."""
        func = call_node.func

        # Check if it's typer.Option() or typer.Argument()
        is_typer_call = (
            isinstance(func, ast.Attribute)
            and func.attr in ("Option", "Argument")
            and isinstance(func.value, ast.Name)
            and func.value.id == "typer"
        ) or (isinstance(func, ast.Name) and func.id in ("Option", "Argument"))

        if not is_typer_call:
            return None

        info: dict[str, Any] = {}

        # First positional argument is the default value (if present)
        if call_node.args:
            default_val = self._extract_value(call_node.args[0])
            # typer uses ... (Ellipsis) for required parameters
            if default_val is not None:
                info["default"] = default_val

        # Extract keyword arguments
        for keyword in call_node.keywords:
            if keyword.arg == "help":
                info["help"] = self._extract_string(keyword.value)
            elif keyword.arg == "default":
                info["default"] = self._extract_value(keyword.value)
            elif keyword.arg == "min":
                info["min"] = self._extract_value(keyword.value)
            elif keyword.arg == "max":
                info["max"] = self._extract_value(keyword.value)
            elif keyword.arg == "case_sensitive":
                info["case_sensitive"] = self._extract_bool(keyword.value)

        return info

    def _extract_value(self, node: ast.expr) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            # Handle Ellipsis (...) used in typer for required parameters
            if node.value is ...:
                return None
            return node.value

        # Handle ast.Ellipsis (older Python versions)
        if isinstance(node, ast.Ellipsis):
            return None

        return None

    def _extract_string(self, node: ast.expr) -> Optional[str]:
        """Extract string from AST node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None

    def _extract_bool(self, node: ast.expr) -> bool:
        """Extract boolean from AST node."""
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return node.value
        return False

    def _extract_list(self, node: ast.expr) -> Optional[list[Any]]:
        """Extract list from AST node."""
        if isinstance(node, ast.List):
            values = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    values.append(elt.value)
            return values if values else None
        return None
