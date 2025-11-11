"""
Step 프로그레스 출력 검증 테스트

이 모듈은 handle_push 함수가 각 Step의 진행 상황을
사용자 친화적으로 출력하는지 검증합니다.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from keynet_train.cli.commands.push import handle_push
from keynet_train.clients.models import Model, UploadKeyCommand, UploadKeyResponse


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


def test_progress_output_shows_all_steps(
    valid_args, mock_config_manager, tmp_path, capsys
):
    """성공 워크플로우에서 Step 1-11 프로그레스 출력 검증"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    # requirements.txt 생성 (Step 6에서 자동 탐지됨)
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("numpy==1.21.0\n")

    # 샘플 업로드 응답 생성
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
                    # BackendClient 인스턴스 mock 설정
                    mock_backend_instance = MagicMock()
                    mock_backend_instance.request_upload_key.return_value = (
                        sample_upload_response
                    )

                    # Context manager 설정 - 자기 자신을 반환
                    mock_backend_instance.__enter__.return_value = mock_backend_instance
                    mock_backend_instance.__exit__.return_value = None

                    mock_backend_class.return_value = mock_backend_instance

                    # DockerClient Mock
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value
                        mock_docker.verify_harbor_credentials.return_value = True
                        mock_docker.build_image.return_value = "sha256:abc123"

                        # Mock Docker SDK direct access for tagging
                        mock_image = MagicMock()
                        mock_docker._client.images.get.return_value = mock_image

                        mock_docker.push_image.return_value = None

                        # 실행
                        exit_code = handle_push(valid_args)

                        # 검증: exit code 0
                        assert exit_code == 0

                        # stdout 캡처
                        captured = capsys.readouterr()

                        # Step 1-11 프로그레스 출력 검증
                        assert (
                            "📋 Step 1/11: Checking authentication..." in captured.out
                        )
                        assert "✅ Authenticated" in captured.out

                        assert (
                            "📋 Step 2/11: Verifying Harbor credentials..."
                            in captured.out
                        )
                        assert "✅ Harbor credentials verified" in captured.out

                        assert "📋 Step 3/11: Validating entrypoint..." in captured.out
                        assert "✅ Validation passed" in captured.out

                        assert (
                            "📋 Step 4/11: Extracting hyperparameters..."
                            in captured.out
                        )
                        assert "✅ Found 0 hyperparameters" in captured.out

                        assert "📋 Step 5/11: Selecting project..." in captured.out

                        assert "📋 Step 6/11: Determining model name..." in captured.out

                        assert "📋 Step 7/11: Requesting upload key..." in captured.out
                        assert "✅ Upload key:" in captured.out  # Mock 값 검증은 생략

                        assert (
                            "📋 Step 8/11: Resolving dependencies..." in captured.out
                            or "📋 Step 8/11: Using custom Dockerfile..."
                            in captured.out
                        )

                        assert (
                            "📋 Step 9/11: Building container image..." in captured.out
                        )
                        assert "✅ Built image: sha256:abc12" in captured.out

                        assert "📋 Step 10/11: Tagging image..." in captured.out
                        # Updated to match the actual image reference from sample_upload_response
                        assert (
                            "✅ Tagged: kitech-harbor.wimcorp.dev/kitech-model/test-upload-key:latest"
                            in captured.out
                        )

                        assert "📋 Step 11/11: Pushing to Harbor..." in captured.out
                        assert "✅ Push completed" in captured.out

                        # 최종 성공 메시지 검증 (rich Panel format)
                        assert "✨ Push Completed Successfully!" in captured.out
                        assert "Upload Key:" in captured.out
                        assert "test-upload-key" in captured.out
                        # 하이퍼파라미터가 없을 때 Panel 내부에 "None" 표시
                        assert "Hyperparameters: None" in captured.out


def test_progress_output_format(
    valid_args, mock_config_manager, sample_upload_response, tmp_path, capsys
):
    """프로그레스 출력 형식 검증 (이모지, 포맷팅)"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text('print("training")\n')
    valid_args.entrypoint = str(train_file)

    # requirements.txt 생성 (Step 6에서 자동 탐지됨)
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
            mock_extractor.extract_metadata.return_value = {
                "arguments": [
                    {"name": "lr", "type": "float", "default": 0.001},
                    {"name": "epochs", "type": "int", "default": 10},
                    {"name": "batch_size", "type": "int", "default": 32},
                ]
            }

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

                    # DockerClient Mock
                    with patch(
                        "keynet_train.clients.docker.DockerClient"
                    ) as mock_docker_class:
                        mock_docker = mock_docker_class.return_value
                        mock_docker.build_image.return_value = "sha256:def456"

                        # Mock Docker SDK direct access for tagging
                        mock_image = MagicMock()
                        mock_docker._client.images.get.return_value = mock_image

                        mock_docker.push_image.return_value = None

                        # 실행
                        exit_code = handle_push(valid_args)

                        # 검증: exit code 0
                        assert exit_code == 0

                        # stdout 캡처
                        captured = capsys.readouterr()

                        # 하이퍼파라미터 개수와 이름이 제대로 표시되는지 확인
                        assert (
                            "✅ Found 3 hyperparameters: lr, epochs, batch_size"
                            in captured.out
                        )

                        # 이미지 ID가 12자리로 잘 잘리는지 확인
                        assert "✅ Built image: sha256:def45" in captured.out

                        # 최종 메시지에 하이퍼파라미터 상세 정보 확인 (rich Table format)
                        assert "Hyperparameters (3 arguments)" in captured.out
                        # Table 헤더 확인
                        assert "Name" in captured.out
                        assert "Type" in captured.out
                        assert "Default" in captured.out
                        # Table 행 데이터 확인
                        assert "lr" in captured.out
                        assert "float" in captured.out
                        assert "0.001" in captured.out
                        assert "epochs" in captured.out
                        assert "int" in captured.out
                        assert "10" in captured.out
                        assert "batch_size" in captured.out
                        assert "32" in captured.out
