"""DockerClient tag_image 메서드 테스트"""

from unittest.mock import MagicMock, patch

import pytest

from keynet_train.clients.docker import DockerClient


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


def test_tag_image_success(client):
    """tag_image 성공 케이스: 이미지 태깅 및 전체 경로 반환"""
    # Mock 이미지 객체
    mock_image = MagicMock()

    # Podman SDK의 images.get() Mock
    with patch.object(client._client.images, "get", return_value=mock_image):
        tagged_image = client.tag_image(
            image_id="sha256:abc123",
            project="ml-models",
            upload_key="my-model:v1.0.0",
        )

        # images.get() 호출 확인
        client._client.images.get.assert_called_once_with("sha256:abc123")

        # image.tag() 호출 확인 (repository와 tag 분리)
        mock_image.tag.assert_called_once_with(
            repository="harbor.example.com/ml-models/my-model", tag="v1.0.0"
        )

        # 반환된 태그 확인
        assert tagged_image == "harbor.example.com/ml-models/my-model:v1.0.0"


def test_tag_image_normalizes_registry_url(client):
    """tag_image는 Harbor URL을 정규화해야 함 (https:// 제거)"""
    mock_image = MagicMock()

    with patch.object(client._client.images, "get", return_value=mock_image):
        tagged_image = client.tag_image(
            image_id="sha256:def456",
            project="project-a",
            upload_key="model-b:v2",
        )

        # https:// 스킴이 제거되었는지 확인
        assert tagged_image.startswith("harbor.example.com/")
        assert "https://" not in tagged_image


def test_tag_image_with_port_in_registry(harbor_config):
    """Harbor URL에 포트가 포함된 경우 처리"""
    harbor_config["url"] = "https://harbor.example.com:8443"

    # Mock Docker client 생성
    with patch("keynet_train.clients.docker.docker.from_env") as mock_from_env:
        mock_docker_client = MagicMock()
        mock_from_env.return_value = mock_docker_client

        client = DockerClient(harbor_config)

        mock_image = MagicMock()
        client._client.images.get.return_value = mock_image

        tagged_image = client.tag_image(
            image_id="sha256:ghi789",
            project="project-c",
            upload_key="model-c:v3",
        )

        # 포트가 유지되는지 확인
        assert tagged_image == "harbor.example.com:8443/project-c/model-c:v3"


def test_tag_image_with_trailing_slash_in_registry(harbor_config):
    """Harbor URL에 트레일링 슬래시가 있는 경우 제거"""
    harbor_config["url"] = "https://harbor.example.com/"

    # Mock Docker client 생성
    with patch("keynet_train.clients.docker.docker.from_env") as mock_from_env:
        mock_docker_client = MagicMock()
        mock_from_env.return_value = mock_docker_client

        client = DockerClient(harbor_config)

        mock_image = MagicMock()
        client._client.images.get.return_value = mock_image

        tagged_image = client.tag_image(
            image_id="sha256:jkl012",
            project="project-d",
            upload_key="model-d:v4",
        )

        # 트레일링 슬래시 제거 확인 (이중 슬래시 없음)
        assert tagged_image == "harbor.example.com/project-d/model-d:v4"
        assert "//" not in tagged_image.replace("://", "")  # 스킴 제외
