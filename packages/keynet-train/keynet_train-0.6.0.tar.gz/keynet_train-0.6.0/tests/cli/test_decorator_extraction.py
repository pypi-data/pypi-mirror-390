"""Tests for decorator parameter extraction."""

import tempfile
from pathlib import Path

from keynet_train.cli.parser.decorator import (
    extract_trace_pytorch_base_image,
    extract_trace_pytorch_model_name,
)


def test_extract_literal_string():
    """Extract base_image from string literal."""
    code = """
import torch
from keynet_train.decorators import trace_pytorch

@trace_pytorch(
    "test-model",
    torch.randn(1, 784),
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
    "test-model",
    torch.randn(1, 784),
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
@trace_pytorch("test-model", torch.randn(1, 784))
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

@trace_pytorch("test-model", input, base_image=f"pytorch:{version}")
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
@trace_pytorch("test-model", input, base_image="value"
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
@trace_pytorch("model1", input1, base_image="first:1.0")
def train1():
    return model1

@trace_pytorch("model2", input2, base_image="second:2.0")
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

@trace_pytorch("test-model", input, base_image="pytorch:2.0")
def train():
    return model
""",
        """
import keynet_train

@keynet_train.decorators.trace_pytorch("test-model", input, base_image="pytorch:2.0")
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


# Tests for model_name extraction


def test_extract_model_name_from_positional():
    """Extract model_name from first positional argument."""
    code = """
from keynet_train.decorators import trace_pytorch

@trace_pytorch("my-resnet50", torch.randn(1, 3, 224, 224))
def train():
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_model_name(f.name)
    Path(f.name).unlink()

    assert result == "my-resnet50"


def test_extract_model_name_from_keyword():
    """Extract model_name from keyword argument (backward compatibility)."""
    code = """
from keynet_train.decorators import trace_pytorch

@trace_pytorch(model_name="my-bert", sample_input=torch.randn(1, 128, 768))
def train():
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_model_name(f.name)
    Path(f.name).unlink()

    assert result == "my-bert"


def test_extract_model_name_from_constant():
    """Extract model_name from module constant."""
    code = """
from keynet_train.decorators import trace_pytorch

MODEL_NAME = "vit-base-patch16"

@trace_pytorch(MODEL_NAME, torch.randn(1, 3, 224, 224))
def train():
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_model_name(f.name)
    Path(f.name).unlink()

    assert result == "vit-base-patch16"


def test_extract_model_name_missing():
    """Return None when model_name cannot be extracted."""
    code = """
def train():
    return model
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_model_name(f.name)
    Path(f.name).unlink()

    assert result is None
