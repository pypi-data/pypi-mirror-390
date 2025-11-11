"""handle_push 전체 워크플로우 통합 테스트"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from keynet_train.cli.commands.push import handle_push
from keynet_train.clients.docker import BuildError, PushError
from keynet_train.clients.models import (
    FetchTrainableProjectsResponse,
    Model,
    PageMeta,
    TrainingProjectBrief,
    UploadKeyCommand,
    UploadKeyResponse,
)


@pytest.fixture
def valid_args():
    """유효한 push 명령 인자 fixture"""
    args = argparse.Namespace()
    args.entrypoint = "train.py"
    args.dockerfile = None
    args.requirements = None
    args.context = "."
    args.model_name = None  # CLI default is now None (auto-detect)
    args.base_image = None  # CLI default is now None (auto-detect)
    args.no_cache = False
    return args


@pytest.fixture
def mock_config_manager():
    """ConfigManager Mock fixture"""
    mock = MagicMock()
    mock.get_harbor_credentials.return_value = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    mock.get_api_key.return_value = "test_api_key"
    mock.get_server_url.return_value = "https://backend.example.com"
    return mock


@pytest.fixture
def sample_projects_response():
    """샘플 프로젝트 응답 데이터"""
    return FetchTrainableProjectsResponse(
        content=[
            TrainingProjectBrief(
                id=1,
                title="테스트 프로젝트",
                summary="테스트용",
                taskType="classification",
                author={"displayName": "테스터", "id": 123},
            )
        ],
        meta=PageMeta(total=1, page=0, limit=20, maxPage=1),
    )


@pytest.fixture
def sample_upload_response():
    """샘플 업로드 키 응답"""
    command = UploadKeyCommand(
        tag="docker tag <YOUR_IMAGE:TAG> kitech-harbor.wimcorp.dev/kitech-model/test-upload-key:latest",
        push="docker push kitech-harbor.wimcorp.dev/kitech-model/test-upload-key:latest",
    )
    model = Model(id=1, name="test-model")
    return UploadKeyResponse(
        id=999,
        project_id=207,
        upload_key="test-upload-key",
        model=model,
        command=command,
    )


def test_handle_push_success_workflow(
    valid_args,
    mock_config_manager,
    sample_projects_response,
    sample_upload_response,
    tmp_path,
):
    """전체 워크플로우 성공 케이스: Step 1-10 모두 성공"""
    # Step 0: 임시 train.py 파일 생성 (유효한 Python 파일)
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)
    valid_args.model_name = "test-model"  # model_name 명시
    valid_args.base_image = "python:3.10-slim"  # base_image 명시

    # requirements.txt 생성 (Step 6에서 자동 탐지됨)
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("numpy==1.21.0\n")

    # Step 1: 인증 확인 - ConfigManager Mock
    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        # Step 2: Entrypoint 검증 - PythonSyntaxValidator는 실제로 작동
        # (train.py가 유효한 파일이므로 패스)

        # Step 3: 하이퍼파라미터 추출 - ArgumentParserExtractor Mock
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {
                "parser_type": "argparse",
                "arguments": [
                    {"name": "lr", "type": "float", "default": 0.001, "required": False}
                ],
            }

            # Step 4: 프로젝트 선택 - select_project Mock으로 간단하게 처리
            with patch(
                "keynet_train.cli.commands.push.select_project", return_value=1
            ) as mock_select:
                # Step 5: 업로드 키 요청 - BackendClient Mock
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    # Context manager 설정
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None

                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    # Step 6: requirements.txt 해결은 자동으로 진행됨 (tmp_path에 requirements.txt 없음 → 에러 발생 가능)
                    # Step 7-9: DockerClient Mock (빌드, 태그, 푸시)
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value
                        mock_docker.build_image.return_value = "sha256:abc123"

                        # Mock Docker SDK direct access for tagging
                        mock_image = MagicMock()
                        mock_docker._client.images.get.return_value = mock_image

                        mock_docker.push_image.return_value = None

                        # 실행
                        exit_code = handle_push(valid_args)

                        # 검증: exit code 0 (성공)
                        assert exit_code == 0

                        # 주요 함수 호출 확인
                        mock_config_manager.get_harbor_credentials.assert_called_once()
                        mock_config_manager.get_api_key.assert_called_once()
                        mock_config_manager.get_server_url.assert_called_once()
                        mock_extractor.extract_metadata.assert_called_once()
                        assert mock_select.called
                        mock_backend_class.assert_called_once()
                        mock_docker_class.assert_called_once()
                        mock_docker.build_image.assert_called_once()
                        # Tag image is now called via Docker SDK directly
                        mock_docker._client.images.get.assert_called_once_with(
                            "sha256:abc123"
                        )
                        mock_image.tag.assert_called_once()
                        mock_docker.push_image.assert_called_once()


def test_handle_push_no_harbor_credentials(valid_args, tmp_path):
    """Step 1 실패: Harbor 자격증명 없음"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    # ConfigManager Mock - Harbor credentials 없음
    mock_config = MagicMock()
    mock_config.get_harbor_credentials.return_value = None

    with patch(
        "keynet_train.cli.commands.push.ConfigManager", return_value=mock_config
    ):
        exit_code = handle_push(valid_args)

        # 검증: exit code 1
        assert exit_code == 1


def test_handle_push_no_api_key(valid_args, mock_config_manager, tmp_path):
    """Step 1 실패: API 키 없음"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    # API key 없음
    mock_config_manager.get_api_key.return_value = None

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        exit_code = handle_push(valid_args)

        # 검증: exit code 1
        assert exit_code == 1


def test_handle_push_entrypoint_not_found(valid_args, mock_config_manager):
    """Step 2 실패: Entrypoint 파일 없음"""
    valid_args.entrypoint = "nonexistent_file.py"

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        exit_code = handle_push(valid_args)

        # 검증: exit code 1
        assert exit_code == 1


def test_handle_push_invalid_python_syntax(valid_args, mock_config_manager, tmp_path):
    """Step 2 실패: 잘못된 Python 문법"""
    # 잘못된 Python 파일 생성
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def broken syntax(:\n")
    valid_args.entrypoint = str(invalid_file)

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        exit_code = handle_push(valid_args)

        # 검증: exit code 1
        assert exit_code == 1


def test_handle_push_no_projects_available(valid_args, mock_config_manager, tmp_path):
    """Step 4 실패: 사용 가능한 프로젝트 없음"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch(
                "keynet_train.clients.backend.BackendClient"
            ) as mock_backend_class:
                # Context manager 설정
                mock_backend_instance = MagicMock()
                mock_backend_class.return_value.__enter__.return_value = (
                    mock_backend_instance
                )
                mock_backend_class.return_value.__exit__.return_value = None

                # 빈 프로젝트 목록
                empty_response = FetchTrainableProjectsResponse(
                    content=[], meta=PageMeta(total=0, page=0, limit=20, maxPage=0)
                )
                mock_backend_instance.fetch_trainable_projects.return_value = (
                    empty_response
                )

                exit_code = handle_push(valid_args)

                # 검증: exit code 1 (ValueError 발생)
                assert exit_code == 1


def test_handle_push_api_error_on_upload_key(
    valid_args, mock_config_manager, sample_upload_response, tmp_path
):
    """Step 5 실패: request_upload_key API 에러"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch("keynet_train.cli.commands.push.select_project", return_value=1):
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    # Context manager 설정
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None

                    # request_upload_key API 에러 발생
                    from keynet_train.clients.backend import ServerError

                    mock_backend_instance.request_upload_key.side_effect = ServerError(
                        "Internal server error"
                    )

                    exit_code = handle_push(valid_args)

                    # 검증: exit code 1
                    assert exit_code == 1


def test_handle_push_build_error(
    valid_args, mock_config_manager, sample_upload_response, tmp_path
):
    """Step 6 실패: 빌드 에러"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch("keynet_train.cli.commands.push.select_project", return_value=1):
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    # Context manager 설정
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None

                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    # PodmanClient Mock - build_image 실패
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_podman_class:
                        mock_podman = mock_podman_class.return_value

                        mock_podman.build_image.side_effect = BuildError(
                            "Docker build failed"
                        )

                        exit_code = handle_push(valid_args)

                        # 검증: exit code 1
                        assert exit_code == 1


def test_handle_push_push_error(
    valid_args, mock_config_manager, sample_upload_response, tmp_path
):
    """Step 8 실패: 푸시 에러"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch("keynet_train.cli.commands.push.select_project", return_value=1):
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    # Context manager 설정
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None

                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    # PodmanClient Mock - push_image 실패
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_podman_class:
                        mock_podman = mock_podman_class.return_value
                        mock_podman.build_image.return_value = "sha256:abc123"
                        mock_podman.tag_image.return_value = (
                            "harbor.example.com/kitech-model/test-model:v1.0.0"
                        )

                        mock_podman.push_image.side_effect = PushError(
                            "Failed to push image"
                        )

                        exit_code = handle_push(valid_args)

                        # 검증: exit code 1
                        assert exit_code == 1


def test_handle_push_base_image_cli_priority(
    mock_config_manager, sample_upload_response, tmp_path
):
    """base_image 우선순위: CLI argument가 decorator보다 우선"""
    # 임시 train.py 생성 (@trace_pytorch with base_image)
    train_file = tmp_path / "train.py"
    train_file.write_text(
        """
import torch
from keynet_train import trace_pytorch

@trace_pytorch(
    "test-model",
    torch.randn(1, 784),
    base_image="decorator/image:1.0"
)
def train():
    return torch.nn.Linear(784, 10)
"""
    )

    # CLI에서 명시적으로 base_image 지정
    args = argparse.Namespace()
    args.entrypoint = str(train_file)
    args.dockerfile = None
    args.requirements = None
    args.context = "."
    args.model_name = None
    args.base_image = "cli/image:2.0"  # CLI에서 명시적 지정
    args.no_cache = False

    # requirements.txt 생성
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("torch==2.0.0\n")

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch("keynet_train.cli.commands.push.select_project", return_value=1):
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None
                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value
                        mock_docker.build_image.return_value = "sha256:abc123"
                        mock_image = MagicMock()
                        mock_docker._client.images.get.return_value = mock_image
                        mock_docker.push_image.return_value = None

                        exit_code = handle_push(args)

                        # 검증: 성공
                        assert exit_code == 0

                        # build_image가 CLI base_image로 호출되었는지 확인
                        mock_docker.build_image.assert_called_once()
                        call_kwargs = mock_docker.build_image.call_args[1]
                        assert call_kwargs["base_image"] == "cli/image:2.0"


def test_handle_push_base_image_from_decorator(
    mock_config_manager, sample_upload_response, tmp_path
):
    """base_image 우선순위: CLI 없으면 decorator 사용"""
    # 임시 train.py 생성 (@trace_pytorch with base_image)
    train_file = tmp_path / "train.py"
    train_file.write_text(
        """
import torch
from keynet_train import trace_pytorch

@trace_pytorch(
    "test-model",
    torch.randn(1, 784),
    base_image="decorator/image:1.0"
)
def train():
    return torch.nn.Linear(784, 10)
"""
    )

    # CLI에서 base_image 지정 안 함 (None)
    args = argparse.Namespace()
    args.entrypoint = str(train_file)
    args.dockerfile = None
    args.requirements = None
    args.context = "."
    args.model_name = None
    args.base_image = None  # CLI에서 지정 안 함
    args.no_cache = False

    # requirements.txt 생성
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("torch==2.0.0\n")

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch("keynet_train.cli.commands.push.select_project", return_value=1):
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None
                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value
                        mock_docker.build_image.return_value = "sha256:abc123"
                        mock_image = MagicMock()
                        mock_docker._client.images.get.return_value = mock_image
                        mock_docker.push_image.return_value = None

                        exit_code = handle_push(args)

                        # 검증: 성공
                        assert exit_code == 0

                        # build_image가 decorator base_image로 호출되었는지 확인
                        mock_docker.build_image.assert_called_once()
                        call_kwargs = mock_docker.build_image.call_args[1]
                        assert call_kwargs["base_image"] == "decorator/image:1.0"


def test_handle_push_base_image_default(
    mock_config_manager, sample_upload_response, tmp_path, capsys
):
    """base_image 우선순위: CLI도 decorator도 없으면 에러 발생"""
    # 임시 train.py 생성 (decorator 없음)
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')

    # CLI에서 base_image 지정 안 함
    args = argparse.Namespace()
    args.entrypoint = str(train_file)
    args.dockerfile = None
    args.requirements = None
    args.context = "."
    args.model_name = "test-model"  # model_name 명시
    args.base_image = None
    args.no_cache = False

    # requirements.txt 생성
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("numpy==1.21.0\n")

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch("keynet_train.cli.commands.push.select_project", return_value=1):
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None
                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    # DockerClient Mock 추가
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value
                        mock_docker.verify_harbor_credentials.return_value = True

                        exit_code = handle_push(args)

                        # 검증: 실패 (base_image 없음)
                        assert exit_code == 1

                        # 에러 메시지 확인
                        captured = capsys.readouterr()
                        assert "base_image not specified" in captured.err
                        assert "@trace_pytorch" in captured.err
                        assert "--base-image" in captured.err
                        assert "--dockerfile" in captured.err


def test_handle_push_base_image_decorator_extraction_fails(
    mock_config_manager, sample_upload_response, tmp_path, capsys
):
    """base_image 추출 실패 시: 에러 발생 (no graceful fallback)"""
    # 임시 train.py 생성 (decorator가 있지만 추출 불가능한 형태)
    train_file = tmp_path / "train.py"
    train_file.write_text(
        """
import torch
from keynet_train import trace_pytorch

version = "2.0"

@trace_pytorch(
    "test-model",
    torch.randn(1, 784),
    base_image=f"pytorch:{version}"  # f-string은 추출 불가
)
def train():
    return torch.nn.Linear(784, 10)
"""
    )

    # CLI에서 base_image 지정 안 함
    args = argparse.Namespace()
    args.entrypoint = str(train_file)
    args.dockerfile = None
    args.requirements = None
    args.context = "."
    args.model_name = None
    args.base_image = None
    args.no_cache = False

    # requirements.txt 생성
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("torch==2.0.0\n")

    with patch(
        "keynet_train.cli.commands.push.ConfigManager",
        return_value=mock_config_manager,
    ):
        with patch(
            "keynet_train.cli.commands.push.ArgumentParserExtractor"
        ) as mock_extractor_class:
            mock_extractor = mock_extractor_class.return_value
            mock_extractor.extract_metadata.return_value = {"arguments": []}

            with patch("keynet_train.cli.commands.push.select_project", return_value=1):
                with patch(
                    "keynet_train.clients.backend.BackendClient"
                ) as mock_backend_class:
                    mock_backend_instance = MagicMock()
                    mock_backend_class.return_value.__enter__.return_value = (
                        mock_backend_instance
                    )
                    mock_backend_class.return_value.__exit__.return_value = None
                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    # DockerClient Mock 추가
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value
                        mock_docker.verify_harbor_credentials.return_value = True

                        exit_code = handle_push(args)

                        # 검증: 실패 (base_image 추출 실패 → 없음)
                        assert exit_code == 1

                        # 에러 메시지 확인
                        captured = capsys.readouterr()
                        assert "base_image not specified" in captured.err
