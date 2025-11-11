"""DockerClient build_image 메서드 테스트 (동적 Dockerfile)"""

from unittest.mock import MagicMock, patch

import pytest

from keynet_train.clients.docker import BuildError, DockerClient

from .conftest import create_mock_build_logs


@pytest.fixture
def harbor_config():
    """Harbor 설정 fixture"""
    return {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }


@pytest.fixture
def client(harbor_config):
    """DockerClient fixture with mocked Docker client"""
    # Docker client 초기화 전에 docker.from_env() Mock
    with patch("keynet_train.clients.docker.docker.from_env") as mock_from_env:
        mock_docker_client = MagicMock()
        mock_from_env.return_value = mock_docker_client

        client = DockerClient(harbor_config)
        # Mock된 Docker client를 반환
        return client


def test_build_image_with_dynamic_dockerfile(client, tmp_path):
    """dockerfile_path=None: 동적 Dockerfile 생성 및 빌드"""
    # Mock build logs
    mock_logs = create_mock_build_logs("sha256:abc123")

    # Mock Docker API build 메서드
    with patch.object(client._client.api, "build", return_value=iter(mock_logs)):
        # 빌드 실행
        image_id = client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=None,
            base_image="python:3.10-slim",
        )

        # 이미지 ID 반환 확인
        assert image_id == "sha256:abc123"

        # build() 호출 확인
        client._client.api.build.assert_called_once()
        call_kwargs = client._client.api.build.call_args.kwargs

        assert call_kwargs["path"] == str(tmp_path)
        assert call_kwargs["dockerfile"] == ".Dockerfile.keynet-train.tmp"
        assert call_kwargs["nocache"] is False
        assert call_kwargs["decode"] is True


def test_build_image_creates_temp_dockerfile(client, tmp_path):
    """동적 Dockerfile이 context_path에 생성되는지 확인"""
    temp_dockerfile_path = tmp_path / ".Dockerfile.keynet-train.tmp"

    def mock_build(*args, **kwargs):
        # build() 호출 시점에 임시 Dockerfile이 존재하는지 확인
        assert temp_dockerfile_path.exists()
        return iter(create_mock_build_logs("sha256:abc123"))

    with patch.object(client._client.api, "build", side_effect=mock_build):
        client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=None,
            base_image="python:3.10-slim",
        )


def test_build_image_cleans_up_temp_dockerfile(client, tmp_path):
    """Finally 블록으로 임시 Dockerfile이 정리되는지 확인"""
    temp_dockerfile_path = tmp_path / ".Dockerfile.keynet-train.tmp"
    mock_logs = create_mock_build_logs("sha256:abc123")

    with patch.object(client._client.api, "build", return_value=iter(mock_logs)):
        client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=None,
            base_image="python:3.10-slim",
        )

        # 빌드 완료 후 임시 파일이 삭제되었는지 확인
        assert not temp_dockerfile_path.exists()


def test_build_image_cleans_up_temp_dockerfile_on_error(client, tmp_path):
    """빌드 실패 시에도 임시 Dockerfile이 정리되는지 확인"""
    temp_dockerfile_path = tmp_path / ".Dockerfile.keynet-train.tmp"

    with patch.object(
        client._client.api, "build", side_effect=Exception("Build failed")
    ):
        # BuildError 발생 확인

        with pytest.raises(BuildError):
            client.build_image(
                entrypoint="train.py",
                context_path=str(tmp_path),
                dockerfile_path=None,
                base_image="python:3.10-slim",
            )

        # 실패 후에도 임시 파일이 삭제되었는지 확인
        assert not temp_dockerfile_path.exists()


def test_build_image_uses_entire_context(client, tmp_path):
    """전체 context_path가 빌드에 포함되는지 확인"""
    # 컨텍스트에 파일 생성
    (tmp_path / "train.py").write_text("# training script")
    (tmp_path / "requirements.txt").write_text("torch==2.0.0")
    (tmp_path / "data.txt").write_text("sample data")

    mock_logs = create_mock_build_logs("sha256:abc123")

    with patch.object(client._client.api, "build", return_value=iter(mock_logs)):
        client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=None,
            base_image="python:3.10-slim",
        )

        # build()에 전달된 path가 context_path인지 확인
        call_kwargs = client._client.api.build.call_args.kwargs
        assert call_kwargs["path"] == str(tmp_path)


def test_build_image_with_no_cache(client, tmp_path):
    """no_cache=True일 때 nocache 파라미터 전달 확인"""
    mock_logs = create_mock_build_logs("sha256:abc123")

    with patch.object(client._client.api, "build", return_value=iter(mock_logs)):
        client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=None,
            base_image="python:3.10-slim",
            no_cache=True,
        )

        call_kwargs = client._client.api.build.call_args.kwargs
        assert call_kwargs["nocache"] is True


def test_build_image_with_user_provided_dockerfile(client, tmp_path):
    """사용자가 제공한 Dockerfile을 사용하는 케이스"""
    # 사용자 Dockerfile 생성
    user_dockerfile = tmp_path / "Dockerfile"
    user_dockerfile.write_text("""FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
""")

    mock_logs = create_mock_build_logs("sha256:custom123")

    with patch.object(client._client.api, "build", return_value=iter(mock_logs)):
        image_id = client.build_image(
            entrypoint="train.py",  # entrypoint는 무시됨
            context_path=str(tmp_path),
            dockerfile_path=str(user_dockerfile),
        )

        # 이미지 ID 반환 확인
        assert image_id == "sha256:custom123"

        # build() 호출 확인
        client._client.api.build.assert_called_once()
        call_kwargs = client._client.api.build.call_args.kwargs

        assert call_kwargs["path"] == str(tmp_path)
        assert call_kwargs["dockerfile"] == str(user_dockerfile)


def test_build_image_with_user_dockerfile_does_not_create_temp(client, tmp_path):
    """사용자 Dockerfile 사용 시 임시 Dockerfile이 생성되지 않음"""
    user_dockerfile = tmp_path / "Dockerfile.custom"
    user_dockerfile.write_text('FROM alpine\nCMD ["echo", "hello"]')

    temp_dockerfile_path = tmp_path / ".Dockerfile.keynet-train.tmp"

    mock_logs = create_mock_build_logs("sha256:custom456")

    with patch.object(client._client.api, "build", return_value=iter(mock_logs)):
        client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=str(user_dockerfile),
        )

        # 임시 Dockerfile이 생성되지 않았는지 확인
        assert not temp_dockerfile_path.exists()


def test_build_image_raises_build_error_on_podman_failure(client, tmp_path):
    """Docker API build() 실패 시 BuildError 발생"""
    # Docker API가 예외를 발생시키도록 설정
    with patch.object(
        client._client.api, "build", side_effect=Exception("Docker build failed")
    ):
        with pytest.raises(BuildError) as exc_info:
            client.build_image(
                entrypoint="train.py",
                context_path=str(tmp_path),
                dockerfile_path=None,
                base_image="python:3.10-slim",
            )

        # 에러 메시지에 원인이 포함되어 있는지 확인
        assert "Unexpected error during build" in str(exc_info.value)
        assert "Docker build failed" in str(exc_info.value)


def test_build_image_with_invalid_dockerfile_raises_build_error(client, tmp_path):
    """잘못된 Dockerfile 사용 시 BuildError 발생"""
    # 잘못된 Dockerfile 생성 (문법 오류)
    invalid_dockerfile = tmp_path / "Dockerfile.invalid"
    invalid_dockerfile.write_text("INVALID SYNTAX\nFROM")

    # 에러 로그를 반환하도록 설정
    error_logs = create_mock_build_logs(error="Invalid Dockerfile syntax")

    with patch.object(client._client.api, "build", return_value=iter(error_logs)):
        with pytest.raises(BuildError) as exc_info:
            client.build_image(
                entrypoint="train.py",
                context_path=str(tmp_path),
                dockerfile_path=str(invalid_dockerfile),
            )

        assert "Build failed" in str(exc_info.value)
        assert "Invalid Dockerfile syntax" in str(exc_info.value)


def test_build_image_with_podman_connection_error(client, tmp_path):
    """Docker 연결 실패 시 BuildError 발생"""
    # Docker 연결 실패 시뮬레이션
    with patch.object(
        client._client.api,
        "build",
        side_effect=ConnectionError("Cannot connect to Docker service"),
    ):
        with pytest.raises(BuildError) as exc_info:
            client.build_image(
                entrypoint="train.py",
                context_path=str(tmp_path),
                dockerfile_path=None,
                base_image="python:3.10-slim",
            )

        assert "Unexpected error during build" in str(exc_info.value)
        assert "Cannot connect to Docker service" in str(exc_info.value)


def test_build_image_auto_generate_without_base_image_raises_error(client, tmp_path):
    """Auto-generate 모드에서 base_image=None이면 BuildError 발생"""
    with pytest.raises(BuildError) as exc_info:
        client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=None,
            base_image=None,
        )

    assert "base_image is required" in str(exc_info.value)
