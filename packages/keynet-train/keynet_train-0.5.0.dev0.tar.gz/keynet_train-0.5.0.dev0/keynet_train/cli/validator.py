"""
Python syntax validator for training scripts.

This module provides utilities to validate Python syntax before processing.
Extracted from the original CodePackager for reuse in the new architecture.
"""

import ast
from pathlib import Path
from typing import Optional


class PythonSyntaxValidator:
    """
    Validates Python syntax for source files.

    This validator checks Python files for syntax errors using AST parsing,
    providing detailed error messages with line numbers and context.
    """

    @staticmethod
    def validate_files(files: list[Path]) -> tuple[bool, list[str]]:
        """
        Validate Python syntax for a list of files.

        Args:
            files: List of file paths to validate

        Returns:
            Tuple of (success, error_messages):
            - success: True if all files are valid Python
            - error_messages: List of formatted error messages for invalid files

        Example:
            >>> validator = PythonSyntaxValidator()
            >>> files = [Path("train.py"), Path("model.py")]
            >>> success, errors = validator.validate_files(files)
            >>> if not success:
            ...     for error in errors:
            ...         print(error)

        """
        errors = []

        for file_path in files:
            # Skip non-Python files
            if not file_path.name.endswith(".py"):
                continue

            try:
                # Read file content
                content = file_path.read_text(encoding="utf-8")

                # Parse Python syntax (will raise SyntaxError if invalid)
                ast.parse(content, filename=str(file_path))

            except SyntaxError as e:
                # Format error message with file, line, and error details
                error_msg = f"{file_path}:{e.lineno}: {e.msg}"
                if e.text:
                    error_msg += f"\n  {e.text.rstrip()}"
                    if e.offset:
                        error_msg += f"\n  {' ' * (e.offset - 1)}^"
                errors.append(error_msg)

            except UnicodeDecodeError as e:
                errors.append(f"{file_path}: Invalid UTF-8 encoding - {e}")

            except Exception as e:
                errors.append(f"{file_path}: Unexpected error - {e}")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_file(file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate a single Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Tuple of (success, error_message):
            - success: True if file is valid Python
            - error_message: Error message if invalid, None if valid

        """
        success, errors = PythonSyntaxValidator.validate_files([file_path])
        return (success, errors[0] if errors else None)
