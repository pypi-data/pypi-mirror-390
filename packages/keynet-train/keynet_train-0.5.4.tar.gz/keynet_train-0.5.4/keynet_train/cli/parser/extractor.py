"""
AST-based argument parser detection and metadata extraction.

This module provides functionality to detect and extract metadata from Python
argument parsers (argparse, click, typer) using AST analysis.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Optional

from .argparse_parser import ArgparseMetadataExtractor
from .click_parser import ClickMetadataExtractor

logger = logging.getLogger(__name__)


class ArgumentParserExtractor:
    """
    Extracts argument parser metadata from Python source files using AST.

    Detects argparse, click, and typer parsers with the following priority:
    1. Arguments defined in `if __name__ == "__main__"` block
    2. Arguments defined in `main()` function
    3. First ArgumentParser instance found in module
    """

    def find_parser(
        self, file_path: str
    ) -> tuple[Optional[str], Optional[ast.AST], Optional[list[ast.stmt]]]:
        """
        Find argument parser in Python source file.

        Args:
            file_path: Path to Python source file

        Returns:
            Tuple of (parser_type, ast_node, body):
            - parser_type: "argparse", "click", "typer", or None
            - ast_node: AST node of parser (ArgumentParser call, function def, etc.)
            - body: List of statements in the scope where parser was found

        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return None, None, None

        try:
            source = file_path_obj.read_text(encoding="utf-8")
        except Exception:
            return None, None, None

        try:
            tree = ast.parse(source, filename=str(file_path_obj))
        except SyntaxError:
            return None, None, None

        # Priority 1: Check __main__ block
        parser_info = self._find_in_main_block(tree)
        if parser_info[0]:
            return parser_info

        # Priority 2: Check main() function
        parser_info = self._find_in_main_function(tree)
        if parser_info[0]:
            return parser_info

        # Priority 3: First parser instance in module
        parser_info = self._find_first_parser(tree)
        return parser_info

    def _find_in_main_block(
        self, tree: ast.Module
    ) -> tuple[Optional[str], Optional[ast.AST], Optional[list[ast.stmt]]]:
        """Find parser in `if __name__ == "__main__"` block."""
        for node in ast.walk(tree):
            # Check if condition is `__name__ == "__main__"`
            if isinstance(node, ast.If) and self._is_main_guard(node.test):
                # Search for parser in the if block
                parser_type, parser_node = self._find_parser_in_body(node.body)
                if parser_type:
                    return parser_type, parser_node, node.body
        return None, None, None

    def _find_in_main_function(
        self, tree: ast.Module
    ) -> tuple[Optional[str], Optional[ast.AST], Optional[list[ast.stmt]]]:
        """Find parser in main() function definition."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                # Check for click decorators on main function
                if self._has_click_decorator(node):
                    return "click", node, node.body

                # Search for parser in function body
                parser_type, parser_node = self._find_parser_in_body(node.body)
                if parser_type:
                    return parser_type, parser_node, node.body
        return None, None, None

    def _find_first_parser(
        self, tree: ast.Module
    ) -> tuple[Optional[str], Optional[ast.AST], Optional[list[ast.stmt]]]:
        """Find first parser instance in module."""
        parser_type, parser_node = self._find_parser_in_body(tree.body)
        if parser_type:
            return parser_type, parser_node, tree.body
        return None, None, None

    def _find_parser_in_body(
        self, body: list[ast.stmt]
    ) -> tuple[Optional[str], Optional[ast.AST]]:
        """Search for parser in AST body."""
        typer_app_var = None  # Track typer app variable name

        for node in body:
            # Check for argparse.ArgumentParser()
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call)
                and self._is_argparse_parser(node.value)
            ):
                return "argparse", node

            # Check for typer.Typer() or app = typer.Typer()
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call)
                and self._is_typer_app(node.value)
                and node.targets
                and isinstance(node.targets[0], ast.Name)
            ):
                # Track typer app variable name
                typer_app_var = node.targets[0].id

            # Check for function with click decorators
            if isinstance(node, ast.FunctionDef) and self._has_click_decorator(node):
                return "click", node

            # Check for function with typer decorators
            if isinstance(node, ast.FunctionDef) and self._has_typer_decorator(
                node, typer_app_var
            ):
                return "typer", node

            # Recursively check nested blocks (if, for, with, etc.)
            if hasattr(node, "body"):
                parser_info = self._find_parser_in_body(node.body)
                if parser_info[0]:
                    return parser_info

        return None, None

    def _is_main_guard(self, test_node: ast.expr) -> bool:
        """Check if expression is `__name__ == "__main__"`."""
        if (
            isinstance(test_node, ast.Compare)
            and isinstance(test_node.left, ast.Name)
            and test_node.left.id == "__name__"
            and len(test_node.ops) == 1
            and isinstance(test_node.ops[0], ast.Eq)
            and len(test_node.comparators) == 1
        ):
            comparator = test_node.comparators[0]
            if isinstance(comparator, ast.Constant):
                return comparator.value == "__main__"
        return False

    def _is_argparse_parser(self, call_node: ast.Call) -> bool:
        """Check if call is argparse.ArgumentParser()."""
        func = call_node.func

        # Check for ArgumentParser() or argparse.ArgumentParser()
        if isinstance(func, ast.Name) and func.id == "ArgumentParser":
            return True

        # Check if module is argparse
        return (
            isinstance(func, ast.Attribute)
            and func.attr == "ArgumentParser"
            and isinstance(func.value, ast.Name)
            and func.value.id == "argparse"
        )

    def _is_typer_app(self, call_node: ast.Call) -> bool:
        """Check if call is typer.Typer()."""
        func = call_node.func

        # Check for Typer() or typer.Typer()
        if isinstance(func, ast.Name) and func.id == "Typer":
            return True

        # Check if module is typer
        return (
            isinstance(func, ast.Attribute)
            and func.attr == "Typer"
            and isinstance(func.value, ast.Name)
            and func.value.id == "typer"
        )

    def _has_click_decorator(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has click decorators."""
        for decorator in func_node.decorator_list:
            # Check for @click.command(), @click.option(), @click.argument()
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr in ("command", "option", "argument", "group")
                and isinstance(decorator.func.value, ast.Name)
                and decorator.func.value.id == "click"
            ):
                return True

            # Check for @click.command (without parentheses)
            if (
                isinstance(decorator, ast.Attribute)
                and decorator.attr in ("command", "group")
                and isinstance(decorator.value, ast.Name)
                and decorator.value.id == "click"
            ):
                return True

        return False

    def _has_typer_decorator(
        self, func_node: ast.FunctionDef, app_var_name: Optional[str]
    ) -> bool:
        """Check if function has typer decorators (e.g., @app.command())."""
        for decorator in func_node.decorator_list:
            # Check for @app.command() where app is the typer app variable
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr == "command"
                and isinstance(decorator.func.value, ast.Name)
                and (app_var_name is None or decorator.func.value.id == app_var_name)
            ):
                return True

            # Check for @app.command (without parentheses)
            if (
                isinstance(decorator, ast.Attribute)
                and decorator.attr == "command"
                and isinstance(decorator.value, ast.Name)
                and (app_var_name is None or decorator.value.id == app_var_name)
            ):
                return True

        return False

    def extract_metadata(self, file_path: str) -> dict[str, Any]:
        """
        Extract complete argument metadata from Python file.

        This method:
        1. Detects the parser type (argparse, click, typer)
        2. Extracts arguments using the appropriate extractor
        3. Returns structured metadata

        Args:
            file_path: Path to Python source file

        Returns:
            Dictionary with fields:
            - parser_type: str ("argparse", "click", "typer", or None)
            - arguments: list of argument metadata dicts

        Example:
            {
                "parser_type": "argparse",
                "arguments": [
                    {
                        "name": "epochs",
                        "type": "int",
                        "default": 100,
                        "required": False,
                        "help": "Number of training epochs",
                        "choices": None
                    }
                ]
            }

        """
        # Initialize empty metadata
        metadata: dict[str, Any] = {"parser_type": None, "arguments": []}

        try:
            # Detect parser type and get AST node + scope
            parser_type, parser_node, parser_body = self.find_parser(file_path)

            if not parser_type or not parser_node:
                logger.warning(f"No argument parser found in {file_path}")
                return metadata

            metadata["parser_type"] = parser_type

            # Extract arguments using appropriate extractor
            if parser_type == "argparse":
                arguments = self._extract_argparse_metadata(parser_node, parser_body)
            elif parser_type == "click":
                arguments = self._extract_click_metadata(parser_node)
            elif parser_type == "typer":
                arguments = self._extract_typer_metadata(parser_node)
            else:
                logger.warning(f"Unsupported parser type: {parser_type}")
                return metadata

            metadata["arguments"] = arguments

        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")

        return metadata

    def _extract_argparse_metadata(
        self, parser_node: ast.AST, parser_body: Optional[list[ast.stmt]]
    ) -> list[dict[str, Any]]:
        """Extract metadata using ArgparseMetadataExtractor."""
        if parser_body is None:
            return []

        extractor = ArgparseMetadataExtractor()

        # Get parser variable name
        if not isinstance(parser_node, ast.Assign) or not parser_node.targets:
            return []

        if not isinstance(parser_node.targets[0], ast.Name):
            return []

        parser_var_name = parser_node.targets[0].id

        # Extract from the provided body (scope where parser was found)
        return extractor.extract_from_body(parser_body, parser_var_name)

    def _extract_click_metadata(self, parser_node: ast.AST) -> list[dict[str, Any]]:
        """Extract metadata using ClickMetadataExtractor."""
        if not isinstance(parser_node, ast.FunctionDef):
            return []

        extractor = ClickMetadataExtractor()
        return extractor.extract(parser_node)

    def _extract_typer_metadata(self, parser_node: ast.AST) -> list[dict[str, Any]]:
        """Extract metadata using TyperMetadataExtractor."""
        if not isinstance(parser_node, ast.FunctionDef):
            logger.warning(f"Expected FunctionDef for typer, got {type(parser_node)}")
            return []

        from .typer_parser import TyperMetadataExtractor

        extractor = TyperMetadataExtractor()
        return extractor.extract(parser_node)
