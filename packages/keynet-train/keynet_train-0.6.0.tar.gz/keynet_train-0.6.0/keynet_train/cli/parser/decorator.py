"""Decorator parameter extraction utilities."""

import ast
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_trace_pytorch_base_image(file_path: str) -> Optional[str]:
    """
    Extract base_image parameter from @trace_pytorch decorator.

    Supports:
    - String literals: base_image="pytorch:2.0"
    - Module constants: BASE_IMAGE="..."; base_image=BASE_IMAGE

    Returns None for:
    - No @trace_pytorch decorator
    - No base_image parameter
    - Dynamic expressions (f-string, function calls)
    - Parse errors (graceful failure)

    Args:
        file_path: Path to Python training script

    Returns:
        base_image value or None

    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Build symbol table for module-level constants
        symbols = {}
        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                symbols[node.targets[0].id] = node.value.value

        # Find @trace_pytorch and extract base_image
        for node in ast.walk(tree):  # type: ignore[assignment]
            if not isinstance(node, ast.FunctionDef):
                continue

            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue

                func_name = _get_func_name(decorator.func)
                if func_name != "trace_pytorch":
                    continue

                for keyword in decorator.keywords:
                    if keyword.arg == "base_image":
                        value = keyword.value

                        # Case 1: String literal
                        if isinstance(value, ast.Constant):
                            if isinstance(value.value, str):
                                return value.value

                        # Case 2: Variable reference
                        elif isinstance(value, ast.Name):
                            return symbols.get(value.id)

                        # Case 3: Dynamic - not supported
                        return None

        return None

    except Exception as e:
        logger.debug(f"Failed to extract base_image from {file_path}: {e}")
        return None


def extract_trace_pytorch_model_name(file_path: str) -> Optional[str]:
    """
    Extract model_name parameter from @trace_pytorch decorator.

    Supports:
    - First positional argument: @trace_pytorch("my-model", ...)
    - Keyword argument: @trace_pytorch(model_name="my-model", ...)
    - Module constants: MODEL_NAME="..."; @trace_pytorch(MODEL_NAME, ...)

    Returns None for:
    - No @trace_pytorch decorator
    - No model_name parameter
    - Dynamic expressions (f-string, function calls)
    - Parse errors (graceful failure)

    Args:
        file_path: Path to Python training script

    Returns:
        model_name value or None

    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Build symbol table for module-level constants
        symbols = {}
        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                symbols[node.targets[0].id] = node.value.value

        # Find @trace_pytorch and extract model_name
        for node in ast.walk(tree):  # type: ignore[assignment]
            if not isinstance(node, ast.FunctionDef):
                continue

            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue

                func_name = _get_func_name(decorator.func)
                if func_name != "trace_pytorch":
                    continue

                # Priority 1: Check first positional argument
                if decorator.args and len(decorator.args) > 0:
                    first_arg = decorator.args[0]

                    # Case 1: String literal
                    if isinstance(first_arg, ast.Constant):
                        if isinstance(first_arg.value, str):
                            return first_arg.value

                    # Case 2: Variable reference
                    elif isinstance(first_arg, ast.Name):
                        return symbols.get(first_arg.id)

                    # Case 3: Dynamic - not supported
                    return None

                # Priority 2: Check keyword argument
                for keyword in decorator.keywords:
                    if keyword.arg == "model_name":
                        value = keyword.value

                        # Case 1: String literal
                        if isinstance(value, ast.Constant):
                            if isinstance(value.value, str):
                                return value.value

                        # Case 2: Variable reference
                        elif isinstance(value, ast.Name):
                            return symbols.get(value.id)

                        # Case 3: Dynamic - not supported
                        return None

        return None

    except Exception as e:
        logger.debug(f"Failed to extract model_name from {file_path}: {e}")
        return None


def _get_func_name(func_node: ast.expr) -> Optional[str]:
    """Get function name from AST node."""
    if isinstance(func_node, ast.Name):
        return func_node.id
    elif isinstance(func_node, ast.Attribute):
        return func_node.attr
    return None
