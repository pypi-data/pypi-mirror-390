"""DockerClient push_image 메서드 테스트"""

from unittest.mock import MagicMock, patch

import pytest

from keynet_train.clients.docker import DockerClient, PushError


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


def test_push_image_success(client):
    """push_image 성공 케이스: 이미지 푸시 성공"""
    # Podman SDK의 images.push() Mock - generator를 반환
    with patch.object(client._client.images, "push") as mock_push:
        # Mock: 간단한 push 스트림 반환
        mock_push.return_value = iter(
            [
                {"status": "The push refers to repository"},
                {"status": "Pushed", "id": "sha256:abc123"},
            ]
        )

        # push_image 실행 (반환값 없음)
        result = client.push_image("harbor.example.com/ml-models/my-model:v1.0.0")

        # images.push() 호출 확인 (repository와 tag 분리 + stream, decode 추가)
        mock_push.assert_called_once_with(
            repository="harbor.example.com/ml-models/my-model",
            tag="v1.0.0",
            stream=True,
            decode=True,
        )

        # 반환값 확인 (None)
        assert result is None


def test_push_image_without_tag(client):
    """태그가 없는 이미지 푸시 (latest 기본값)"""
    with patch.object(client._client.images, "push") as mock_push:
        mock_push.return_value = iter([{"status": "Pushed", "id": "sha256:abc123"}])

        client.push_image("harbor.example.com/ml-models/my-model")

        # tag=None으로 호출되어야 함
        mock_push.assert_called_once_with(
            repository="harbor.example.com/ml-models/my-model",
            tag=None,
            stream=True,
            decode=True,
        )


def test_push_image_with_port_in_registry(client):
    """포트가 포함된 레지스트리 URL 처리"""
    with patch.object(client._client.images, "push") as mock_push:
        mock_push.return_value = iter([{"status": "Pushed", "id": "sha256:abc123"}])

        client.push_image("registry.example.com:8443/project/model:v2.0")

        # 포트는 repository에 포함, tag는 분리
        mock_push.assert_called_once_with(
            repository="registry.example.com:8443/project/model",
            tag="v2.0",
            stream=True,
            decode=True,
        )


def test_push_image_with_multiple_colons(client):
    """여러 콜론이 있는 경우 (포트 + 태그)"""
    with patch.object(client._client.images, "push") as mock_push:
        mock_push.return_value = iter([{"status": "Pushed", "id": "sha256:abc123"}])

        # 마지막 콜론을 기준으로 tag 분리
        client.push_image("harbor.example.com:8443/project/model:latest")

        mock_push.assert_called_once_with(
            repository="harbor.example.com:8443/project/model",
            tag="latest",
            stream=True,
            decode=True,
        )


def test_push_image_raises_push_error_on_failure(client):
    """images.push() 실패 시 PushError 발생"""
    # Podman SDK가 예외를 발생시키도록 설정
    with patch.object(
        client._client.images,
        "push",
        side_effect=Exception("Push operation failed"),
    ):
        with pytest.raises(PushError) as exc_info:
            client.push_image("harbor.example.com/ml-models/my-model:v1")

        # 에러 메시지 확인
        assert "Image push failed" in str(exc_info.value)
        assert "Push operation failed" in str(exc_info.value)


def test_push_image_raises_push_error_on_network_failure(client):
    """네트워크 에러 시 PushError 발생"""
    # push() 실행 시 네트워크 에러 발생
    with patch.object(
        client._client.images,
        "push",
        side_effect=ConnectionError("Cannot reach registry"),
    ):
        with pytest.raises(PushError) as exc_info:
            client.push_image("harbor.example.com/ml-models/my-model:v1")

        # 에러 메시지 확인
        assert "Image push failed" in str(exc_info.value)
        assert "Cannot reach registry" in str(exc_info.value)


def test_push_image_raises_push_error_on_auth_failure(client):
    """인증 실패 시 PushError 발생"""
    with patch.object(
        client._client.images,
        "push",
        side_effect=Exception("Authentication required"),
    ):
        with pytest.raises(PushError) as exc_info:
            client.push_image("harbor.example.com/ml-models/my-model:v1")

        assert "Image push failed" in str(exc_info.value)
        assert "Authentication required" in str(exc_info.value)
