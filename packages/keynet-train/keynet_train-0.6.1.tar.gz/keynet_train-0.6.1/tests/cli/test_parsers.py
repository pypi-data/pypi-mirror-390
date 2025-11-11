"""
Tests for argument parser metadata extraction.

This module tests the extraction of CLI argument metadata from different
parser types: argparse, click, and typer.
"""

import textwrap
from pathlib import Path

import pytest

from keynet_train.cli.parser.extractor import ArgumentParserExtractor


@pytest.mark.unit
def test_argparse_metadata_extraction(tmp_path: Path) -> None:
    """Test metadata extraction from argparse-based CLI."""
    # Create a sample argparse script
    script = tmp_path / "train_argparse.py"
    script.write_text(
        textwrap.dedent(
            """
        import argparse

        def main():
            parser = argparse.ArgumentParser()
            parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
            parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
            parser.add_argument("--model", type=str, required=True, help="Model name")
            parser.add_argument("--verbose", action="store_true", help="Verbose output")
            args = parser.parse_args()
            return args

        if __name__ == "__main__":
            main()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "argparse"
    assert len(metadata["arguments"]) == 4

    # Check epochs argument
    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["type"] == "int"
    assert epochs_arg["default"] == 10
    assert epochs_arg["required"] is False
    assert "epochs" in epochs_arg["help"].lower()

    # Check lr argument
    lr_arg = next(a for a in metadata["arguments"] if a["name"] == "lr")
    assert lr_arg["type"] == "float"
    assert lr_arg["default"] == 0.001

    # Check model argument (required)
    model_arg = next(a for a in metadata["arguments"] if a["name"] == "model")
    assert model_arg["type"] == "str"
    assert model_arg["required"] is True

    # Check verbose argument (boolean flag)
    verbose_arg = next(a for a in metadata["arguments"] if a["name"] == "verbose")
    assert verbose_arg["type"] == "bool"
    assert verbose_arg["default"] is False


@pytest.mark.unit
def test_click_metadata_extraction(tmp_path: Path) -> None:
    """Test metadata extraction from Click-based CLI."""
    script = tmp_path / "train_click.py"
    script.write_text(
        textwrap.dedent(
            """
        import click

        @click.command()
        @click.option("--epochs", type=int, default=10, help="Number of epochs")
        @click.option("--lr", type=float, default=0.001, help="Learning rate")
        @click.option("--model", type=str, required=True, help="Model name")
        @click.option("--verbose", is_flag=True, help="Verbose output")
        def main(epochs, lr, model, verbose):
            click.echo(f"Training with epochs={epochs}, lr={lr}")

        if __name__ == "__main__":
            main()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "click"
    assert len(metadata["arguments"]) == 4

    # Check epochs option
    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["type"] == "int"
    assert epochs_arg["default"] == 10

    # Check model option (required)
    model_arg = next(a for a in metadata["arguments"] if a["name"] == "model")
    assert model_arg["required"] is True


@pytest.mark.unit
def test_typer_metadata_extraction(tmp_path: Path) -> None:
    """Test metadata extraction from Typer-based CLI."""
    script = tmp_path / "train_typer.py"
    script.write_text(
        textwrap.dedent(
            """
        import typer

        app = typer.Typer()

        @app.command()
        def main(
            epochs: int = typer.Option(10, help="Number of epochs"),
            lr: float = typer.Option(0.001, help="Learning rate"),
            model: str = typer.Option(..., help="Model name"),
        ):
            print(f"Training with epochs={epochs}, lr={lr}, model={model}")

        if __name__ == "__main__":
            app()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "typer"
    assert len(metadata["arguments"]) == 3

    # Check epochs argument (optional with default)
    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["type"] == "int"
    assert epochs_arg["default"] == 10
    assert epochs_arg["required"] is False
    assert epochs_arg["help"] == "Number of epochs"

    # Check lr argument (optional with default)
    lr_arg = next(a for a in metadata["arguments"] if a["name"] == "lr")
    assert lr_arg["type"] == "float"
    assert lr_arg["default"] == 0.001
    assert lr_arg["help"] == "Learning rate"

    # Check model argument (required with Ellipsis)
    model_arg = next(a for a in metadata["arguments"] if a["name"] == "model")
    assert model_arg["type"] == "str"
    assert model_arg["required"] is True
    assert model_arg["help"] == "Model name"


@pytest.mark.unit
def test_main_block_priority(tmp_path: Path) -> None:
    """Test that __main__ block has priority over main() function."""
    script = tmp_path / "train_priority.py"
    script.write_text(
        textwrap.dedent(
            """
        import argparse

        def main():
            # This parser should be ignored
            parser = argparse.ArgumentParser()
            parser.add_argument("--ignored", type=str)
            return parser

        if __name__ == "__main__":
            # This parser should be detected
            parser = argparse.ArgumentParser()
            parser.add_argument("--epochs", type=int, default=10)
            args = parser.parse_args()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "argparse"
    assert len(metadata["arguments"]) == 1
    assert metadata["arguments"][0]["name"] == "epochs"


@pytest.mark.unit
def test_choices_extraction(tmp_path: Path) -> None:
    """Test extraction of choices attribute."""
    script = tmp_path / "train_choices.py"
    script.write_text(
        textwrap.dedent(
            """
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--optimizer",
            type=str,
            choices=["adam", "sgd", "rmsprop"],
            default="adam",
            help="Optimizer type"
        )
        args = parser.parse_args()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "argparse"
    assert len(metadata["arguments"]) == 1

    optimizer_arg = metadata["arguments"][0]
    assert optimizer_arg["name"] == "optimizer"
    assert optimizer_arg["choices"] == ["adam", "sgd", "rmsprop"]
    assert optimizer_arg["default"] == "adam"


@pytest.mark.unit
def test_no_parser_found(tmp_path: Path) -> None:
    """Test handling of files with no argument parser."""
    script = tmp_path / "no_parser.py"
    script.write_text(
        textwrap.dedent(
            """
        def train_model():
            print("Training model without CLI")

        if __name__ == "__main__":
            train_model()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] is None
    assert metadata["arguments"] == []


@pytest.mark.unit
def test_mixed_argument_types(tmp_path: Path) -> None:
    """Test extraction of mixed argument types (positional and optional)."""
    script = tmp_path / "train_mixed.py"
    script.write_text(
        textwrap.dedent(
            """
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("config_file", type=str, help="Config file path")
        parser.add_argument("--epochs", type=int, default=10)
        parser.add_argument("--gpu", action="store_true")
        args = parser.parse_args()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "argparse"
    assert len(metadata["arguments"]) == 3

    # Check positional argument
    config_arg = next(a for a in metadata["arguments"] if a["name"] == "config_file")
    assert config_arg["type"] == "str"
    assert config_arg["required"] is True  # Positional args are required by default


@pytest.mark.unit
def test_click_arguments_vs_options(tmp_path: Path) -> None:
    """Test Click's distinction between arguments and options."""
    script = tmp_path / "train_click_args.py"
    script.write_text(
        textwrap.dedent(
            """
        import click

        @click.command()
        @click.argument("config_file")
        @click.option("--epochs", type=int, default=10)
        def main(config_file, epochs):
            click.echo(f"Config: {config_file}, Epochs: {epochs}")

        if __name__ == "__main__":
            main()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "click"
    assert len(metadata["arguments"]) == 2

    # Click arguments are required by default
    config_arg = next(a for a in metadata["arguments"] if a["name"] == "config_file")
    assert config_arg["required"] is True

    # Options are optional by default
    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["required"] is False


@pytest.mark.unit
def test_invalid_python_syntax(tmp_path: Path) -> None:
    """Test handling of files with invalid Python syntax."""
    script = tmp_path / "invalid_syntax.py"
    script.write_text(
        """
        import argparse
        def main(
            # Missing closing parenthesis
        """
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    # Should return empty metadata without crashing
    assert metadata["parser_type"] is None
    assert metadata["arguments"] == []


@pytest.mark.unit
def test_nested_function_parser(tmp_path: Path) -> None:
    """Test detection of parser in nested function structure."""
    script = tmp_path / "train_nested.py"
    script.write_text(
        textwrap.dedent(
            """
        import argparse

        def create_parser():
            parser = argparse.ArgumentParser()
            parser.add_argument("--epochs", type=int, default=10)
            return parser

        def main():
            parser = create_parser()
            args = parser.parse_args()
            return args

        if __name__ == "__main__":
            main()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    # Should detect parser in main() function
    assert metadata["parser_type"] == "argparse"
    # Note: This test might not extract arguments from nested create_parser()
    # That's expected behavior - we only extract from directly visible parsers


@pytest.mark.unit
def test_multiple_decorators_click(tmp_path: Path) -> None:
    """Test Click with multiple decorators including non-option decorators."""
    script = tmp_path / "train_click_multi.py"
    script.write_text(
        textwrap.dedent(
            """
        import click

        @click.command()
        @click.option("--epochs", type=int, default=10, help="Training epochs")
        @click.option("--lr", type=float, default=0.001, help="Learning rate")
        @click.pass_context
        def main(ctx, epochs, lr):
            click.echo(f"Context: {ctx}, Epochs: {epochs}, LR: {lr}")

        if __name__ == "__main__":
            main()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "click"
    # Should extract only option decorators, ignore pass_context
    assert len(metadata["arguments"]) == 2

    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["type"] == "int"

    lr_arg = next(a for a in metadata["arguments"] if a["name"] == "lr")
    assert lr_arg["type"] == "float"


@pytest.mark.unit
def test_typer_with_simple_defaults(tmp_path: Path) -> None:
    """Test Typer with simple default values (not typer.Option)."""
    script = tmp_path / "train_typer_simple.py"
    script.write_text(
        textwrap.dedent(
            """
        import typer

        app = typer.Typer()

        @app.command()
        def main(
            epochs: int = 10,
            lr: float = 0.001,
            verbose: bool = False,
        ):
            print(f"Training with epochs={epochs}, lr={lr}")

        if __name__ == "__main__":
            app()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "typer"
    assert len(metadata["arguments"]) == 3

    # Check epochs with simple default
    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["type"] == "int"
    assert epochs_arg["default"] == 10
    assert epochs_arg["required"] is False

    # Check boolean flag
    verbose_arg = next(a for a in metadata["arguments"] if a["name"] == "verbose")
    assert verbose_arg["type"] == "bool"
    assert verbose_arg["default"] is False


@pytest.mark.unit
def test_typer_required_arguments(tmp_path: Path) -> None:
    """Test Typer with required arguments using Ellipsis."""
    script = tmp_path / "train_typer_required.py"
    script.write_text(
        textwrap.dedent(
            """
        import typer

        app = typer.Typer()

        @app.command()
        def main(
            config_file: str = typer.Argument(..., help="Configuration file path"),
            model_name: str = typer.Argument(..., help="Model name"),
            epochs: int = typer.Option(10, help="Training epochs"),
        ):
            print(f"Config: {config_file}, Model: {model_name}")

        if __name__ == "__main__":
            app()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "typer"
    assert len(metadata["arguments"]) == 3

    # Check required arguments
    config_arg = next(a for a in metadata["arguments"] if a["name"] == "config_file")
    assert config_arg["type"] == "str"
    assert config_arg["required"] is True
    assert config_arg["help"] == "Configuration file path"

    model_arg = next(a for a in metadata["arguments"] if a["name"] == "model_name")
    assert model_arg["required"] is True

    # Check optional argument
    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["required"] is False
    assert epochs_arg["default"] == 10


@pytest.mark.unit
def test_typer_optional_type_annotation(tmp_path: Path) -> None:
    """Test Typer with Optional type annotation."""
    script = tmp_path / "train_typer_optional.py"
    script.write_text(
        textwrap.dedent(
            """
        from typing import Optional
        import typer

        app = typer.Typer()

        @app.command()
        def main(
            model: Optional[str] = typer.Option(None, help="Model name"),
            epochs: Optional[int] = typer.Option(100, help="Training epochs"),
        ):
            print(f"Model: {model}, Epochs: {epochs}")

        if __name__ == "__main__":
            app()
        """
        )
    )

    extractor = ArgumentParserExtractor()
    metadata = extractor.extract_metadata(str(script))

    assert metadata["parser_type"] == "typer"
    assert len(metadata["arguments"]) == 2

    # Check Optional[str] type extraction
    model_arg = next(a for a in metadata["arguments"] if a["name"] == "model")
    assert model_arg["type"] == "str"
    assert model_arg["default"] is None

    # Check Optional[int] type extraction
    epochs_arg = next(a for a in metadata["arguments"] if a["name"] == "epochs")
    assert epochs_arg["type"] == "int"
    assert epochs_arg["default"] == 100
