"""
에러 메시지 표준화 테스트

이 모듈은 handle_push 함수가 다양한 에러 상황에서
사용자 친화적인 에러 메시지를 출력하는지 검증합니다.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from keynet_train.cli.commands.push import handle_push
from keynet_train.clients.backend import AuthenticationError, NetworkError
from keynet_train.clients.docker import BuildError


@pytest.fixture
def valid_args():
    """유효한 push 명령 인자 fixture"""
    args = argparse.Namespace()
    args.entrypoint = "train.py"
    args.dockerfile = None
    args.requirements = None
    args.context = "."
    args.model_name = "test-model"  # model_name은 필수
    args.base_image = "python:3.10-slim"
    args.no_cache = False
    return args


@pytest.fixture
def mock_config_manager():
    """ConfigManager Mock fixture (인증 성공 케이스)"""
    mock = MagicMock()
    mock.get_harbor_credentials.return_value = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    mock.get_api_key.return_value = "test_api_key"
    mock.get_server_url.return_value = "https://backend.example.com"
    return mock


def test_authentication_error_message_includes_guidance(
    valid_args, mock_config_manager, tmp_path, capsys
):
    """AuthenticationError 발생 시 재로그인 안내 포함"""
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
                    # Mock 인스턴스 생성
                    mock_backend_instance = MagicMock()

                    # AuthenticationError 발생 설정
                    mock_backend_instance.request_upload_key.side_effect = (
                        AuthenticationError("Invalid API key")
                    )

                    # Context manager 설정: BackendClient() 호출 시 mock_backend_instance 반환
                    mock_backend_class.return_value = mock_backend_instance
                    # __enter__는 self를 반환
                    mock_backend_instance.__enter__.return_value = mock_backend_instance
                    mock_backend_instance.__exit__.return_value = None

                    # DockerClient Mock으로 실제 초기화 방지
                    with patch("keynet_train.clients.docker.DockerClient"):
                        # 실행
                        exit_code = handle_push(valid_args)

                        # 검증: exit code 1
                        assert exit_code == 1

                        # stderr 캡처
                        captured = capsys.readouterr()

                        # 에러 메시지 검증
                        assert "❌ Authentication failed:" in captured.err
                        assert "Invalid API key" in captured.err

                        # 재로그인 안내 검증
                        assert "→ Run: keynet-train login" in captured.err

                        # 자격증명 확인 안내 검증
                        assert "→ Check your credentials" in captured.err


def test_build_error_message_includes_troubleshooting(
    valid_args, mock_config_manager, tmp_path, capsys
):
    """BuildError 발생 시 구체적 원인 및 해결 방법 표시"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    # requirements.txt 생성 (Step 6에서 자동 탐지됨)
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("numpy==1.21.0\n")

    from keynet_train.clients.models import Model, UploadKeyCommand, UploadKeyResponse

    sample_upload_response = UploadKeyResponse(
        id=999,
        project_id=207,
        upload_key="test-upload-key",
        model=Model(id=1, name="test-model"),
        command=UploadKeyCommand(
            tag="docker tag <YOUR_IMAGE:TAG> kitech-harbor.wimcorp.dev/kitech-model/test-upload-key:latest",
            push="docker push kitech-harbor.wimcorp.dev/kitech-model/test-upload-key:latest",
        ),
    )

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

                    # DockerClient Mock - build_image 실패
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value

                        # BuildError 발생
                        mock_docker.build_image.side_effect = BuildError(
                            "Dockerfile syntax error at line 10"
                        )

                        # 실행
                        exit_code = handle_push(valid_args)

                        # 검증: exit code 1
                        assert exit_code == 1

                        # stderr 캡처
                        captured = capsys.readouterr()

                        # 에러 메시지 검증
                        assert "❌ Build failed:" in captured.err
                        assert "Dockerfile syntax error" in captured.err

                        # 해결 방법 안내 검증
                        assert "→ Check your Dockerfile syntax" in captured.err
                        assert "→ Verify build context path" in captured.err
                        assert (
                            "→ Check requirements.txt if using auto-generated Dockerfile"
                            in captured.err
                        )
                        assert (
                            "→ Try with --no-cache flag to force clean build"
                            in captured.err
                        )


def test_network_error_message_includes_connection_guidance(
    valid_args, mock_config_manager, tmp_path, capsys
):
    """NetworkError 발생 시 연결 확인 안내 포함"""
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
                    # Mock 인스턴스 생성
                    mock_backend_instance = MagicMock()

                    # NetworkError 발생 설정
                    mock_backend_instance.request_upload_key.side_effect = NetworkError(
                        "Connection timeout"
                    )

                    # Context manager 설정: BackendClient() 호출 시 mock_backend_instance 반환
                    mock_backend_class.return_value = mock_backend_instance
                    # __enter__는 self를 반환
                    mock_backend_instance.__enter__.return_value = mock_backend_instance
                    mock_backend_instance.__exit__.return_value = None

                    # DockerClient Mock으로 실제 초기화 방지
                    with patch("keynet_train.clients.docker.DockerClient"):
                        # 실행
                        exit_code = handle_push(valid_args)

                        # 검증: exit code 1
                        assert exit_code == 1

                        # stderr 캡처
                        captured = capsys.readouterr()

                        # 에러 메시지 검증
                        assert "❌ Network error:" in captured.err
                        assert "Connection timeout" in captured.err

                        # 연결 확인 안내 검증
                        assert "→ Check your internet connection" in captured.err
                        assert "→ Verify server URL in config" in captured.err
                        assert "→ Check firewall/proxy settings" in captured.err


def test_docker_not_available_error_message(
    valid_args, mock_config_manager, tmp_path, capsys
):
    """Docker 미설치/미실행 시 명확한 에러 메시지 및 안내"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    # requirements.txt 생성 (Step 6에서 자동 탐지됨)
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("numpy==1.21.0\n")

    from keynet_train.clients.models import Model, UploadKeyCommand, UploadKeyResponse

    sample_upload_response = UploadKeyResponse(
        id=999,
        project_id=207,
        upload_key="test-upload-key",
        model=Model(id=1, name="test-model"),
        command=UploadKeyCommand(
            tag="docker tag <YOUR_IMAGE:TAG> kitech-harbor.wimcorp.dev/kitech-model/test-upload-key:latest",
            push="docker push kitech-harbor.wimcorp.dev/kitech-model/test-upload-key:latest",
        ),
    )

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

                    # DockerClient Mock - from_env() 실패
                    with patch("keynet_train.clients.docker.docker") as mock_docker:
                        from docker.errors import DockerException

                        # docker.from_env() 호출 시 DockerException 발생
                        mock_docker.from_env.side_effect = DockerException(
                            "Error while fetching server API version: "
                            "('Connection aborted.', ConnectionRefusedError(61, "
                            "'Connection refused'))"
                        )

                        # 실행
                        exit_code = handle_push(valid_args)

                        # 검증: exit code 1
                        assert exit_code == 1

                        # stderr 캡처
                        captured = capsys.readouterr()

                        # 에러 메시지 검증
                        assert "❌ Docker is not available:" in captured.err

                        # 해결 방법 안내 검증
                        assert "→ Install Docker Desktop" in captured.err
                        assert "→ Start Docker Desktop" in captured.err
                        assert "→ Run: docker version" in captured.err
