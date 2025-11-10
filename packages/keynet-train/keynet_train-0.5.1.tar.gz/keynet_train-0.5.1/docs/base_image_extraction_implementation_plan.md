# Implementation Plan: Auto-extract base_image from @trace_pytorch decorator

## 개요

`@trace_pytorch` 데코레이터에 optional `base_image` 파라미터를 추가하고, `keynet-train push` 명령어가 데코레이터에서 이를 자동으로 추출하여 사용하도록 개선합니다.

### 목표

- **DRY 원칙**: base_image를 한 곳에서만 정의
- **편의성**: CLI 인자 생략 가능
- **유연성**: CLI override 지원
- **하위 호환성**: 기존 코드 100% 호환

### 우선순위 규칙

```text
CLI --base-image > 데코레이터 base_image > 기본값 "python:3.10-slim"
```

### 커스텀 Dockerfile 사용 시

base_image 설정은 **완전히 무시됨** (사용자 혼란 방지)

---

## Milestone 1: Decorator 파라미터 추출 함수 구현

### 파일: `keynet_train/cli/parser/decorator.py` (신규, ~50줄)

#### Task 1.1: 파일 및 함수 골격 생성

**목표:** 간단한 함수로 구현 (클래스 불필요)

**구현:**

```python
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
    pass  # 구현은 다음 태스크
```

**검증:**

- [ ] 파일 생성 확인
- [ ] import 에러 없음

---

#### Task 1.2: 리터럴 문자열 추출 (RED → GREEN)

**테스트 파일:** `tests/cli/test_decorator_extraction.py` (신규)

**RED - 실패하는 테스트:**

```python
"""Tests for decorator parameter extraction."""
import tempfile
from pathlib import Path

from keynet_train.cli.parser.decorator import extract_trace_pytorch_base_image


def test_extract_literal_string():
    """Extract base_image from string literal."""
    code = '''
import torch
from keynet_train.decorators import trace_pytorch

@trace_pytorch(
    "my_experiment",
    torch.randn(1, 784),
    base_image="pytorch/pytorch:2.0.1-cuda11.7"
)
def train_model():
    return model
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()

        result = extract_trace_pytorch_base_image(f.name)

    Path(f.name).unlink()

    assert result == "pytorch/pytorch:2.0.1-cuda11.7"
```

**실행:** `pytest tests/cli/test_decorator_extraction.py::test_extract_literal_string -v`

**예상:** FAIL

---

**GREEN - 구현:**

```python
def extract_trace_pytorch_base_image(file_path: str) -> Optional[str]:
    """Extract base_image from @trace_pytorch decorator."""
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        source = path.read_text(encoding='utf-8')
        tree = ast.parse(source)

        # Walk through all function definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if not isinstance(decorator, ast.Call):
                        continue

                    # Check if it's trace_pytorch
                    func_name = _get_func_name(decorator.func)
                    if func_name != "trace_pytorch":
                        continue

                    # Look for base_image keyword argument
                    for keyword in decorator.keywords:
                        if keyword.arg == "base_image":
                            if isinstance(keyword.value, ast.Constant):
                                return keyword.value.value
                            return None

        return None

    except Exception as e:
        logger.debug(f"Failed to extract base_image from {file_path}: {e}")
        return None


def _get_func_name(func_node: ast.expr) -> Optional[str]:
    """Get function name from AST node."""
    if isinstance(func_node, ast.Name):
        return func_node.id
    elif isinstance(func_node, ast.Attribute):
        return func_node.attr
    return None
```

**실행:** `pytest tests/cli/test_decorator_extraction.py::test_extract_literal_string -v`

**예상:** PASS ✅

---

#### Task 1.3: 모듈 상수 추출 (RED → GREEN)

**RED - 테스트:**

```python
def test_extract_module_constant():
    """Extract base_image from module-level constant."""
    code = '''
import torch
from keynet_train.decorators import trace_pytorch

BASE_IMAGE = "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"

@trace_pytorch(
    "my_experiment",
    torch.randn(1, 784),
    base_image=BASE_IMAGE
)
def train_model():
    return model
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result == "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"
```

**실행:** FAIL (변수 resolve 안 됨)

---

**GREEN - 구현 개선:**

```python
def extract_trace_pytorch_base_image(file_path: str) -> Optional[str]:
    """Extract base_image from @trace_pytorch decorator."""
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        source = path.read_text(encoding='utf-8')
        tree = ast.parse(source)

        # Build symbol table for module-level constants
        symbols = {
            target.id: node.value.value
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
        }

        # Find @trace_pytorch and extract base_image
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
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
```

**실행:** PASS ✅

---

#### Task 1.4: 실패 케이스 (RED → GREEN)

**테스트:**

```python
def test_extract_when_missing():
    """Return None when base_image parameter is missing."""
    code = '''
@trace_pytorch("exp", torch.randn(1, 784))
def train():
    return model
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None


def test_extract_when_no_decorator():
    """Return None when no @trace_pytorch decorator."""
    code = '''
def train():
    return model
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None


def test_extract_with_fstring():
    """Return None for dynamic f-string (not supported)."""
    code = '''
version = "2.0.1"

@trace_pytorch("exp", input, base_image=f"pytorch:{version}")
def train():
    return model
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None


def test_extract_with_syntax_error():
    """Return None gracefully on syntax error."""
    code = '''
@trace_pytorch("exp", input, base_image="value"
def train():  # Missing closing parenthesis
    return model
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result is None
```

**검증:** 현재 구현으로 모두 PASS해야 함

---

#### Task 1.5: 엣지 케이스

**테스트:**

```python
def test_extract_first_of_multiple():
    """Extract from first decorator when multiple exist."""
    code = '''
@trace_pytorch("exp1", input1, base_image="first:1.0")
def train1():
    return model1

@trace_pytorch("exp2", input2, base_image="second:2.0")
def train2():
    return model2
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        result = extract_trace_pytorch_base_image(f.name)
    Path(f.name).unlink()

    assert result == "first:1.0"


def test_extract_with_various_imports():
    """Handle different import styles."""
    test_cases = [
        '''
from keynet_train.decorators import trace_pytorch

@trace_pytorch("exp", input, base_image="pytorch:2.0")
def train():
    return model
''',
        '''
import keynet_train

@keynet_train.decorators.trace_pytorch("exp", input, base_image="pytorch:2.0")
def train():
    return model
''',
    ]

    for code in test_cases:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            result = extract_trace_pytorch_base_image(f.name)
        Path(f.name).unlink()

        assert result == "pytorch:2.0"
```

**검증:** 모두 PASS

---

#### Task 1.6: Milestone 1 완료 검증

**실행:**

```bash
pytest tests/cli/test_decorator_extraction.py -v
```

**예상 결과:**

```text
test_extract_literal_string PASSED
test_extract_module_constant PASSED
test_extract_when_missing PASSED
test_extract_when_no_decorator PASSED
test_extract_with_fstring PASSED
test_extract_with_syntax_error PASSED
test_extract_first_of_multiple PASSED
test_extract_with_various_imports PASSED

========== 8 passed ==========
```

**커밋:**

```bash
git add keynet_train/cli/parser/decorator.py
git add tests/cli/test_decorator_extraction.py
git commit -m "feat(train): Add decorator base_image extraction utility (BEHAVIORAL)"
```

---

## Milestone 2: trace_pytorch 데코레이터 수정

### 파일: `keynet_train/decorators/pytorch.py` (수정)

#### Task 2.1: 시그니처 수정 (STRUCTURAL)

**변경 전:**

```python
def trace_pytorch(
    experiment_name: str,
    sample_input: Union[torch.Tensor, dict[str, torch.Tensor]],
    run_name: Optional[str] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    onnx_opset_version: int = 17,
    auto_convert_onnx: bool = True,
    log_model_info: bool = True,
    enable_autolog: bool = True,
    dynamic_axes: Optional[dict[str, dict[int, str]]] = None,
):
```

**변경 후:**

```python
def trace_pytorch(
    experiment_name: str,
    sample_input: Union[torch.Tensor, dict[str, torch.Tensor]],
    run_name: Optional[str] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    onnx_opset_version: int = 17,
    auto_convert_onnx: bool = True,
    log_model_info: bool = True,
    enable_autolog: bool = True,
    base_image: Optional[str] = None,  # 🆕 NEW
    dynamic_axes: Optional[dict[str, dict[int, str]]] = None,
):
```

**위치:** `dynamic_axes` 직전에 추가

**검증:**

```bash
poe test tests/test_annotation.py -v
```

**예상:** 모든 기존 테스트 PASS (하위 호환성 확인)

---

#### Task 2.2: MLflow 로깅 추가 (RED → GREEN)

**RED - 테스트 추가:**

파일: `tests/test_annotation.py`

```python
def test_trace_pytorch_with_base_image(self, setup_mlflow, mock_pytorch_onnx_client):
    """Test that base_image is logged to MLflow."""

    @trace_pytorch(
        "base_image_experiment",
        torch.randn(1, 784),
        base_image="pytorch/pytorch:2.0.1-cuda11.7",
        enable_autolog=False,
        auto_convert_onnx=False,
    )
    def train():
        model = nn.Linear(784, 10)
        return model

    model = train()

    # Verify MLflow logged the base_image
    run = mlflow.active_run()
    assert run is not None

    client = mlflow.tracking.MlflowClient()
    run_data = client.get_run(run.info.run_id)

    assert "container_base_image" in run_data.data.params
    assert run_data.data.params["container_base_image"] == "pytorch/pytorch:2.0.1-cuda11.7"
```

**실행:** `pytest tests/test_annotation.py::TestTracePytorch::test_trace_pytorch_with_base_image -v`

**예상:** FAIL

---

**GREEN - 구현:**

파일: `keynet_train/decorators/pytorch.py`

데코레이터 내부 (Line ~450, MLflow run 내부):

```python
with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run:
    try:
        # ... existing code ...

        logger.info(f"MLflow 실행 시작 (run_id: {run_uuid})")

        # 🆕 Log base_image if provided
        if base_image:
            mlflow.log_param("container_base_image", base_image)
            logger.info(f"Container base image: {base_image}")

        # 사용자 함수 실행
        result = func(*args, **kwargs)
        # ... rest of code ...
```

**실행:** PASS ✅

---

#### Task 2.3: base_image None 케이스 (RED → GREEN)

**테스트:**

```python
def test_trace_pytorch_without_base_image(self, setup_mlflow, mock_pytorch_onnx_client):
    """Test that base_image is NOT logged when None."""

    @trace_pytorch(
        "no_base_image_experiment",
        torch.randn(1, 784),
        enable_autolog=False,
        auto_convert_onnx=False,
    )
    def train():
        model = nn.Linear(784, 10)
        return model

    model = train()

    run = mlflow.active_run()
    client = mlflow.tracking.MlflowClient()
    run_data = client.get_run(run.info.run_id)

    # Verify base_image is NOT in params
    assert "container_base_image" not in run_data.data.params
```

**검증:** 현재 구현 (`if base_image:`)으로 PASS해야 함

---

#### Task 2.4: 기존 기능 회귀 테스트

**실행:**

```bash
pytest tests/test_annotation.py -v
```

**예상:** 모든 테스트 PASS (회귀 없음)

---

#### Task 2.5: Docstring 업데이트 (STRUCTURAL)

**수정 위치:** `trace_pytorch` docstring (Line ~326)

**Args 섹션에 추가:**

```python
    base_image: 컨테이너 베이스 이미지 (선택사항) 🆕
        - 지정하면 MLflow에 기록되고, `keynet-train push`에서 자동 사용
        - 예: "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"
        - `keynet-train push --dockerfile`로 커스텀 Dockerfile 사용 시 무시됨
        - CLI `--base-image` 옵션이 이 값보다 우선함
```

**사용 예시 섹션에 추가:**

```python
    # 🆕 베이스 이미지 지정 (keynet-train push에서 자동 사용)
    @trace_pytorch(
        "my_experiment",
        torch.randn(1, 3, 224, 224),
        base_image="pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"
    )
    def train_model():
        model = MyModel()
        return model

    # CLI에서 자동 추출:
    # $ keynet-train push train.py

    # 또는 CLI에서 override:
    # $ keynet-train push train.py --base-image custom:1.0
```

**커밋:**

```bash
git add keynet_train/decorators/pytorch.py
git add tests/test_annotation.py
git commit -m "feat(train): Add optional base_image parameter to trace_pytorch (BEHAVIORAL)"
```

---

## Milestone 3: push 명령어 통합

### 파일: `keynet_train/cli/commands/push.py` (수정)

#### Task 3.1: base_image 결정 로직 추가

**변경 위치:** `handle_push` 함수 Step 6과 7 사이

**추가 코드:**

```python
# Step 6.5: Resolve base_image
if args.dockerfile:
    print_step(6, 11, "Using custom Dockerfile")
    print_success(f"Dockerfile: {args.dockerfile}")
    base_image_resolved = None  # Will be ignored by DockerClient
else:
    print_step(6, 11, "Resolving base image")

    # Priority: CLI > decorator > default
    if args.base_image:
        base_image_resolved = args.base_image
        print_success(f"Using CLI base image: {base_image_resolved}")

        # Check if decorator also has value
        from ..parser.decorator import extract_trace_pytorch_base_image
        decorator_value = extract_trace_pytorch_base_image(str(entrypoint))
        if decorator_value and decorator_value != args.base_image:
            print(f"   (Overrides decorator value: {decorator_value})")
    else:
        # Try to extract from decorator
        from ..parser.decorator import extract_trace_pytorch_base_image
        extracted = extract_trace_pytorch_base_image(str(entrypoint))

        if extracted:
            base_image_resolved = extracted
            print_success(f"Extracted from decorator: {base_image_resolved}")
        else:
            base_image_resolved = "python:3.10-slim"
            print_success(f"Using default base image: {base_image_resolved}")

# Step 7: Build container image (번호 조정)
print_step(7, 11, "Building container image")
client = DockerClient(harbor_creds)
image_id = client.build_image(
    entrypoint=str(entrypoint),
    context_path=args.context,
    dockerfile_path=args.dockerfile,
    base_image=base_image_resolved,  # ← 결정된 값 사용
    no_cache=args.no_cache,
)
```

**단계 번호 조정:** 나머지 8→9, 9→10, 10→11로 조정

---

#### Task 3.2: 통합 테스트 작성 (RED → GREEN)

**파일:** `tests/cli/test_push_base_image_resolution.py` (신규)

**테스트:**

```python
"""Tests for base_image resolution in push command."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_deps():
    """Mock all external dependencies."""
    with patch("keynet_train.cli.commands.push.ConfigManager") as mock_config, \
         patch("keynet_train.cli.commands.push.PythonSyntaxValidator") as mock_validator, \
         patch("keynet_train.cli.commands.push.ArgumentParserExtractor") as mock_extractor, \
         patch("keynet_train.cli.commands.push.BackendClient") as mock_backend, \
         patch("keynet_train.cli.commands.push.DockerClient") as mock_docker:

        # Setup mocks
        mock_config_inst = mock_config.return_value
        mock_config_inst.get_harbor_credentials.return_value = {
            "url": "https://harbor.example.com",
            "username": "test",
            "password": "test"
        }
        mock_config_inst.get_api_key.return_value = "test-key"
        mock_config_inst.get_server_url.return_value = "https://api.example.com"

        mock_validator_inst = mock_validator.return_value
        mock_validator_inst.validate_file.return_value = (True, None)

        mock_extractor_inst = mock_extractor.return_value
        mock_extractor_inst.extract_metadata.return_value = {
            "parser_type": "argparse",
            "arguments": []
        }

        mock_backend_inst = mock_backend.return_value.__enter__.return_value
        mock_backend_inst.list_projects.return_value = [{"id": 1, "name": "test"}]
        mock_backend_inst.request_upload_key.return_value = MagicMock(
            upload_key="test-key",
            get_image_reference=lambda: "harbor.example.com/test/model:latest"
        )

        mock_docker_inst = mock_docker.return_value
        mock_docker_inst.build_image.return_value = "sha256:abc123"
        mock_docker_inst._client = MagicMock()
        mock_docker_inst._client.images.get.return_value = MagicMock()

        yield {
            "config": mock_config_inst,
            "validator": mock_validator_inst,
            "extractor": mock_extractor_inst,
            "backend": mock_backend_inst,
            "docker": mock_docker_inst,
        }


def test_push_uses_decorator_base_image(mock_deps, monkeypatch):
    """Decorator base_image is used when no CLI argument."""
    code = '''
from keynet_train.decorators import trace_pytorch
import torch

@trace_pytorch("exp", torch.randn(1, 784), base_image="pytorch:2.0")
def train():
    return model
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        script_path = f.name

    try:
        # Mock input for project selection
        monkeypatch.setattr('builtins.input', lambda _: '1')

        from keynet_train.cli.commands.push import handle_push
        import argparse

        args = argparse.Namespace(
            entrypoint=script_path,
            dockerfile=None,
            requirements=None,
            context='.',
            base_image=None,  # No CLI value
            no_cache=False,
        )

        result = handle_push(args)

        assert result == 0
        # Verify build_image was called with extracted value
        mock_deps["docker"].build_image.assert_called_once()
        call_kwargs = mock_deps["docker"].build_image.call_args.kwargs
        assert call_kwargs["base_image"] == "pytorch:2.0"

    finally:
        Path(script_path).unlink()


def test_push_cli_overrides_decorator(mock_deps, monkeypatch):
    """CLI --base-image overrides decorator value."""
    code = '''
from keynet_train.decorators import trace_pytorch
import torch

@trace_pytorch("exp", torch.randn(1, 784), base_image="pytorch:2.0")
def train():
    return model
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        script_path = f.name

    try:
        monkeypatch.setattr('builtins.input', lambda _: '1')

        from keynet_train.cli.commands.push import handle_push
        import argparse

        args = argparse.Namespace(
            entrypoint=script_path,
            dockerfile=None,
            requirements=None,
            context='.',
            base_image="custom:1.0",  # CLI value
            no_cache=False,
        )

        result = handle_push(args)

        assert result == 0
        call_kwargs = mock_deps["docker"].build_image.call_args.kwargs
        assert call_kwargs["base_image"] == "custom:1.0"

    finally:
        Path(script_path).unlink()


def test_push_uses_default_when_none(mock_deps, monkeypatch):
    """Use default when no CLI and no decorator."""
    code = '''
from keynet_train.decorators import trace_pytorch
import torch

@trace_pytorch("exp", torch.randn(1, 784))
def train():
    return model
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        script_path = f.name

    try:
        monkeypatch.setattr('builtins.input', lambda _: '1')

        from keynet_train.cli.commands.push import handle_push
        import argparse

        args = argparse.Namespace(
            entrypoint=script_path,
            dockerfile=None,
            requirements=None,
            context='.',
            base_image=None,
            no_cache=False,
        )

        result = handle_push(args)

        assert result == 0
        call_kwargs = mock_deps["docker"].build_image.call_args.kwargs
        assert call_kwargs["base_image"] == "python:3.10-slim"

    finally:
        Path(script_path).unlink()


def test_push_ignores_base_image_with_dockerfile(mock_deps, monkeypatch):
    """base_image is ignored when using custom Dockerfile."""
    code = '''
from keynet_train.decorators import trace_pytorch
import torch

@trace_pytorch("exp", torch.randn(1, 784), base_image="pytorch:2.0")
def train():
    return model
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        script_path = f.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='', delete=False) as df:
        df.write(b'FROM alpine\nCMD echo hello')
        df.flush()
        dockerfile_path = df.name

    try:
        monkeypatch.setattr('builtins.input', lambda _: '1')

        from keynet_train.cli.commands.push import handle_push
        import argparse

        args = argparse.Namespace(
            entrypoint=script_path,
            dockerfile=dockerfile_path,
            requirements=None,
            context='.',
            base_image=None,
            no_cache=False,
        )

        result = handle_push(args)

        assert result == 0
        # base_image should be None (ignored)
        call_kwargs = mock_deps["docker"].build_image.call_args.kwargs
        assert call_kwargs["base_image"] is None

    finally:
        Path(script_path).unlink()
        Path(dockerfile_path).unlink()
```

**실행:**

```bash
pytest tests/cli/test_push_base_image_resolution.py -v
```

**예상:** 4개 테스트 모두 PASS ✅

---

#### Task 3.3: CLI help text 업데이트 (STRUCTURAL)

**수정 위치:** `setup_push_parser` 함수

**변경:**

```python
parser.add_argument(
    "--base-image",
    type=str,
    default=None,
    help=(
        "Base Docker image for auto-generated Dockerfile. "
        "Priority: CLI > decorator > default (python:3.10-slim). "
        "Ignored when --dockerfile is provided. "
        "Can be specified in @trace_pytorch decorator."
    ),
)
```

**Epilog 예제 추가:**

```python
epilog="""
Examples:
    # Auto-extract base_image from @trace_pytorch decorator
    keynet-train push train.py

    # Override decorator with CLI
    keynet-train push train.py --base-image pytorch/pytorch:2.0.1

    # Custom Dockerfile (base_image ignored)
    keynet-train push train.py --dockerfile ./Dockerfile

    # Custom base image
    keynet-train push train.py --base-image custom:1.0

Notes:
    - base_image priority: CLI > @trace_pytorch > default
    - With --dockerfile, base_image is ignored
"""
```

---

#### Task 3.4: Milestone 3 완료 검증

**실행:**

```bash
# Unit tests
pytest tests/cli/test_push_base_image_resolution.py -v

# Full suite
poe test

# Lint & typecheck
poe check
```

**커밋:**

```bash
git add keynet_train/cli/commands/push.py
git add tests/cli/test_push_base_image_resolution.py
git commit -m "feat(train): Auto-extract base_image from decorator in push command (BEHAVIORAL)"
```

---

## Milestone 4: E2E 검증 및 문서화

### Task 4.1: 수동 E2E 테스트

**테스트 스크립트:** `examples/test_base_image_extraction.py`

```python
"""Test script for base_image auto-extraction."""
import torch
import torch.nn as nn
from keynet_train.decorators import trace_pytorch

BASE_IMAGE = "pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"


class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(784, 10)

    def forward(self, x):
        return self.fc(x)


@trace_pytorch(
    "base_image_test_experiment",
    torch.randn(1, 784),
    base_image=BASE_IMAGE,
    enable_autolog=False,
    auto_convert_onnx=False,
)
def train_model():
    """Train a simple model."""
    model = SimpleModel()
    print("✅ Model created")
    return model


if __name__ == "__main__":
    model = train_model()
    print(f"✅ Training complete: {type(model)}")
```

**수동 테스트 체크리스트:**

- [ ] Scenario 1: `keynet-train push examples/test_base_image_extraction.py` → 데코레이터에서 추출
- [ ] Scenario 2: `keynet-train push ... --base-image custom:1.0` → CLI override
- [ ] Scenario 3: `keynet-train push ... --dockerfile ./Dockerfile` → 무시됨

---

### Task 4.2: 문서 업데이트

**CLAUDE.md에 추가:**

```markdown
### @trace_pytorch base_image 자동 추출

**v0.2.0부터 추가된 기능**

`@trace_pytorch` 데코레이터에 `base_image` 파라미터를 지정하면,
`keynet-train push` 명령어가 자동으로 이를 추출하여 컨테이너 빌드에 사용합니다.

#### 사용법

```python
from keynet_train.decorators import trace_pytorch
import torch

@trace_pytorch(
    "my_experiment",
    torch.randn(1, 784),
    base_image="pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime"
)
def train_model():
    model = MyModel()
    # ... training code ...
    return model
```

#### 우선순위 규칙

1. **CLI `--base-image`**: 최우선 (데코레이터 값 override)
2. **데코레이터 `base_image`**: CLI 없으면 사용
3. **기본값**: `python:3.10-slim`

#### 예제

```bash
# 데코레이터에서 자동 추출
keynet-train push train.py

# CLI로 override
keynet-train push train.py --base-image custom:1.0

# 커스텀 Dockerfile 사용 시 무시됨
keynet-train push train.py --dockerfile ./Dockerfile
```

#### 지원되는 표현

✅ **문자열 리터럴:**

```python
@trace_pytorch(..., base_image="pytorch:2.0")
```

✅ **모듈 상수:**

```python
BASE_IMAGE = "pytorch:2.0"
@trace_pytorch(..., base_image=BASE_IMAGE)
```

❌ **동적 표현 (미지원):**

```python
@trace_pytorch(..., base_image=f"pytorch:{version}")  # 추출 실패 → 기본값
```

#### 주의사항

- `--dockerfile` 사용 시 `base_image`는 완전히 무시됩니다
- MLflow에는 항상 기록되어 추적 가능합니다
- 동적 표현 사용 시 추출 실패하며 기본값으로 fallback됩니다
```

**커밋:**

```bash
git add CLAUDE.md
git commit -m "docs(train): Document base_image auto-extraction feature (STRUCTURAL)"
```

---

### Task 4.3: 최종 검증

**전체 테스트:**

```bash
poe test
poe test-cov
poe check
```

**예상 결과:**

- [ ] 모든 테스트 통과 (273개 = 260 기존 + 13 신규)
- [ ] 새 코드 커버리지 > 90%
- [ ] 린트/타입체크 통과

---

## 테스트 매트릭스 요약

| Case # | Dockerfile | CLI | Decorator | Expected | Test |
|--------|-----------|-----|-----------|----------|------|
| 1 | 자동 | 없음 | 리터럴 | 추출 값 | ✅ |
| 2 | 자동 | 없음 | 상수 | 추출 값 | ✅ |
| 3 | 자동 | 없음 | 없음 | 기본값 | ✅ |
| 4 | 자동 | 있음 | 있음 | CLI 우선 | ✅ |
| 5 | 커스텀 | * | * | None | ✅ |

---

## 리스크 및 대응

### Risk 1: AST 파싱 실패

**대응:** Graceful fallback to default

### Risk 2: 성능

**예상:** < 10ms (무시 가능)

### Risk 3: 사용자 혼란

**대응:** 명확한 피드백 메시지, 문서화

---

## 예상 소요 시간

- Milestone 1: 1.5 hours (간소화)
- Milestone 2: 1 hour
- Milestone 3: 1.5 hours
- Milestone 4: 1 hour

**Total**: ~5 hours (기존 6h에서 감소)

---

## 성공 기준

✅ **기능:**

- [ ] 리터럴 추출 작동
- [ ] 상수 추출 작동
- [ ] 우선순위 규칙 작동
- [ ] Graceful fallback 작동

✅ **품질:**

- [ ] 13개 새 테스트 통과
- [ ] 기존 테스트 회귀 없음
- [ ] 커버리지 > 90%

✅ **문서:**

- [ ] Docstring 완전
- [ ] CLI help 명확
- [ ] CLAUDE.md 업데이트
