"""Tests for decorator parameter extraction."""

import tempfile
from pathlib import Path

from keynet_train.cli.parser.decorator import extract_trace_pytorch_base_image


def test_extract_literal_string():
    """Extract base_image from string literal."""
    code = """
import torch
from keynet_train.decorators import trace_pytorch

@trace_pytorch(
    "my_experiment",
    torch.randn(1, 784),
    model_name="test-model",
    base_image="pytorch/pytorch:2.0.1-cuda11.7"
)
def train_model():
    return model
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        result = extract_trace_pytorch_base_image(f.name)

    Path(f.name).unlink()

    assert result == "pytorch/pytorch:2.0.1-cuda11.7"


def test_extract_module_constant():
    """Extract base_image from module-level constant."""
    code = """
import torch
from keynet_train.decorators import trace_pytorch

BASE_IMAGE = "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"

@trace_pytorch(
    "my_experiment",
    torch.randn(1, 784),
    model_name="test-model",
    base_image=BASE_IMAGE
)
def train_model():
    return model
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result == "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"


def test_extract_when_missing():
    """Return None when base_image parameter is missing."""
    code = """
@trace_pytorch("exp", torch.randn(1, 784), model_name="test-model")
def train():
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None


def test_extract_when_no_decorator():
    """Return None when no @trace_pytorch decorator."""
    code = """
def train():
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None


def test_extract_with_fstring():
    """Return None for dynamic f-string (not supported)."""
    code = """
version = "2.0.1"

@trace_pytorch("exp", input, model_name="test-model", base_image=f"pytorch:{version}")
def train():
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None


def test_extract_with_syntax_error():
    """Return None gracefully on syntax error."""
    code = """
@trace_pytorch("exp", input, model_name="test-model", base_image="value"
def train():  # Missing closing parenthesis
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None


def test_extract_first_of_multiple():
    """Extract from first decorator when multiple exist."""
    code = """
@trace_pytorch("exp1", input1, model_name="model1", base_image="first:1.0")
def train1():
    return model1

@trace_pytorch("exp2", input2, model_name="model2", base_image="second:2.0")
def train2():
    return model2
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result == "first:1.0"


def test_extract_with_various_imports():
    """Handle different import styles."""
    test_cases = [
        """
from keynet_train.decorators import trace_pytorch

@trace_pytorch("exp", input, model_name="test-model", base_image="pytorch:2.0")
def train():
    return model
""",
        """
import keynet_train

@keynet_train.decorators.trace_pytorch("exp", input, model_name="test-model", base_image="pytorch:2.0")
def train():
    return model
""",
    ]

    for code in test_cases:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            result = extract_trace_pytorch_base_image(f.name)
        Path(f.name).unlink()

        assert result == "pytorch:2.0"
