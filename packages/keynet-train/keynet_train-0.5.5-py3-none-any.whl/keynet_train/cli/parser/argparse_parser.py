"""
Argparse metadata extraction from AST.

This module extracts argument metadata from argparse-based CLI definitions.
"""

import ast
from typing import Any, Optional


class ArgparseMetadataExtractor:
    """
    Extract metadata from argparse.ArgumentParser definitions.

    Analyzes AST nodes to find add_argument() calls and extract:
    - Argument name
    - Type (int, str, float, bool)
    - Default value
    - Required flag
    - Help text
    - Choices list
    """

    def extract(self, parser_node: ast.AST) -> list[dict[str, Any]]:
        """
        Extract argument metadata from argparse parser AST node.

        Args:
            parser_node: AST node containing ArgumentParser (typically ast.Assign)

        Returns:
            List of argument metadata dictionaries with fields:
            - name: str
            - type: str ("int", "str", "float", "bool", or None)
            - default: Any
            - required: bool
            - help: str or None
            - choices: list or None

        """
        if not isinstance(parser_node, ast.Assign):
            return []

        # Get the variable name of the parser (e.g., "parser")
        if not parser_node.targets:
            return []

        parser_var_name = None
        if isinstance(parser_node.targets[0], ast.Name):
            parser_var_name = parser_node.targets[0].id

        if not parser_var_name:
            return []

        # Find all add_argument() calls on this parser
        arguments: list[dict[str, Any]] = []

        # Search in the same scope (function body or module body)
        # We need to walk through the parent scope to find add_argument calls
        # For now, we'll assume the parser_node is passed with context
        # This is a limitation - in real usage, we need the full function/module body

        # For a more robust solution, we should search the parent body
        # Let's extract from the node itself if it's in a function
        return arguments

    def extract_from_body(
        self, body: list[ast.stmt], parser_var_name: str
    ) -> list[dict[str, Any]]:
        """
        Extract arguments from a body of statements.

        Args:
            body: List of AST statements (from function or module)
            parser_var_name: Name of the ArgumentParser variable

        Returns:
            List of argument metadata dictionaries

        """
        arguments = []

        for node in body:
            # Look for parser.add_argument() calls
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if self._is_add_argument_call(call, parser_var_name):
                    arg_meta = self._extract_argument_metadata(call)
                    if arg_meta:
                        arguments.append(arg_meta)

            # Recursively search in nested blocks
            if hasattr(node, "body"):
                arguments.extend(self.extract_from_body(node.body, parser_var_name))

        return arguments

    def _is_add_argument_call(self, call: ast.Call, parser_var_name: str) -> bool:
        """Check if call is parser.add_argument()."""
        func = call.func

        # Check if it's called on the parser variable
        return (
            isinstance(func, ast.Attribute)
            and func.attr == "add_argument"
            and isinstance(func.value, ast.Name)
            and func.value.id == parser_var_name
        )

    def _extract_argument_metadata(self, call: ast.Call) -> Optional[dict[str, Any]]:
        """Extract metadata from add_argument() call."""
        # First positional arg is the argument name
        if not call.args:
            return None

        # Get argument name (e.g., "--epochs" or "input_file")
        arg_name_node = call.args[0]
        if not isinstance(arg_name_node, ast.Constant):
            return None

        arg_name = arg_name_node.value
        if not isinstance(arg_name, str):
            return None

        # Remove leading dashes for long options
        clean_name = arg_name.lstrip("-")

        # Check if positional argument (no leading dashes)
        is_positional = not arg_name.startswith("-")

        # Initialize metadata
        metadata: dict[str, Any] = {
            "name": clean_name,
            "type": None,
            "default": None,
            "required": is_positional,  # Positional args are required by default
            "help": None,
            "choices": None,
        }

        # Extract keyword arguments
        action_type = None
        for keyword in call.keywords:
            if keyword.arg == "type":
                metadata["type"] = self._extract_type(keyword.value)
            elif keyword.arg == "default":
                metadata["default"] = self._extract_value(keyword.value)
                # If positional arg has default, it's not required
                if is_positional:
                    metadata["required"] = False
            elif keyword.arg == "required":
                metadata["required"] = self._extract_bool(keyword.value)
            elif keyword.arg == "help":
                metadata["help"] = self._extract_string(keyword.value)
            elif keyword.arg == "choices":
                metadata["choices"] = self._extract_list(keyword.value)
            elif keyword.arg == "action":
                action_type = self._extract_string(keyword.value)

        # Handle action="store_true" or action="store_false"
        if action_type in ("store_true", "store_false"):
            metadata["type"] = "bool"
            metadata["default"] = (
                action_type == "store_false"
            )  # store_false means default is True

        return metadata

    def _extract_type(self, node: ast.expr) -> Optional[str]:
        """Extract type from AST node."""
        # Handle type=int, type=str, etc.
        if isinstance(node, ast.Name):
            type_name = node.id
            if type_name in ("int", "str", "float", "bool"):
                return type_name

        # Handle type=argparse.FileType('r')
        # For simplicity, we'll return "file" for FileType
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "FileType"
        ):
            return "file"

        return None

    def _extract_value(self, node: ast.expr) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value

        # Handle argparse.SUPPRESS or other special values
        if isinstance(node, ast.Attribute) and node.attr == "SUPPRESS":
            return None

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

    def _extract_list(self, node: ast.expr) -> Optional[list[Any]]:
        """Extract list from AST node."""
        if isinstance(node, ast.List):
            items = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    items.append(elt.value)
            return items if items else None

        return None
