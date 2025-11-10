"""Tests for DockerClient"""

from unittest.mock import Mock, patch

import pytest

from .conftest import create_mock_build_logs


class TestDockerClientInit:
    """Test DockerClient initialization"""

    @patch("keynet_train.clients.docker.docker")
    def test_docker_client_init_success(self, mock_docker):
        """DockerClient 초기화 성공"""
        from keynet_train.clients.docker import DockerClient

        harbor_config = {
            "url": "https://harbor.example.com",
            "username": "robot$test",
            "password": "test_password",
        }

        client = DockerClient(harbor_config)

        assert client is not None
        assert client._harbor_url == "https://harbor.example.com"
        mock_docker.from_env.assert_called_once()

    @patch("keynet_train.clients.docker.docker")
    def test_docker_client_validates_harbor_config(self, mock_docker):
        """Harbor 설정 검증"""
        from keynet_train.clients.docker import DockerClient

        # 빈 config
        with pytest.raises(ValueError, match="harbor_config"):
            DockerClient({})

        # url 누락
        with pytest.raises(ValueError, match="url"):
            DockerClient({"username": "test", "password": "test"})

        # username 누락
        with pytest.raises(ValueError, match="username"):
            DockerClient({"url": "test", "password": "test"})

        # password 누락
        with pytest.raises(ValueError, match="password"):
            DockerClient({"url": "test", "username": "test"})


class TestDockerClientClassMethods:
    """Test DockerClient class methods"""

    def test_get_runtime_name(self):
        """런타임 이름 반환"""
        from keynet_train.clients.docker import DockerClient

        assert DockerClient.get_runtime_name() == "Docker"

    @patch("keynet_train.clients.docker.docker")
    def test_is_available_success(self, mock_docker):
        """Docker가 사용 가능한 경우"""
        from keynet_train.clients.docker import DockerClient

        # Docker ping 성공
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_docker.from_env.return_value = mock_client

        assert DockerClient.is_available() is True
        mock_docker.from_env.assert_called_once()
        mock_client.ping.assert_called_once()

    @patch("keynet_train.clients.docker.docker")
    def test_is_available_failure(self, mock_docker):
        """Docker가 사용 불가능한 경우"""
        from keynet_train.clients.docker import DockerClient

        # Docker 연결 실패
        mock_docker.from_env.side_effect = Exception("Connection failed")

        assert DockerClient.is_available() is False
        mock_docker.from_env.assert_called_once()

    @patch("keynet_train.clients.docker.docker")
    def test_verify_harbor_credentials_success(self, mock_docker):
        """Harbor 인증 성공"""
        from keynet_train.clients.docker import DockerClient

        # Mock Docker client
        mock_client = Mock()
        mock_client.login.return_value = None
        mock_docker.from_env.return_value = mock_client

        harbor_config = {
            "url": "https://harbor.example.com",
            "username": "robot$test",
            "password": "test_password",
        }

        client = DockerClient(harbor_config)
        result = client.verify_harbor_credentials()

        assert result is True
        mock_client.login.assert_called_once_with(
            username="robot$test",
            password="test_password",
            registry="harbor.example.com",
        )

    @patch("keynet_train.clients.docker.docker")
    def test_verify_harbor_credentials_failure(self, mock_docker):
        """Harbor 인증 실패"""
        from keynet_train.clients.docker import DockerClient

        # Mock Docker client
        mock_client = Mock()
        mock_client.login.side_effect = Exception("Authentication failed")
        mock_docker.from_env.return_value = mock_client

        harbor_config = {
            "url": "https://harbor.example.com",
            "username": "robot$test",
            "password": "wrong_password",
        }

        client = DockerClient(harbor_config)
        result = client.verify_harbor_credentials()

        assert result is False


class TestDockerClientBuildImage:
    """Test DockerClient.build_image()"""

    @patch("keynet_train.clients.docker.docker")
    def test_build_image_with_auto_dockerfile(self, mock_docker, tmp_path):
        """자동 Dockerfile 생성으로 빌드"""
        from keynet_train.clients.docker import DockerClient

        # Mock Docker client
        mock_client = Mock()
        mock_logs = create_mock_build_logs("sha256:abc123")
        mock_client.api.build.return_value = iter(mock_logs)
        mock_docker.from_env.return_value = mock_client

        harbor_config = {
            "url": "https://harbor.example.com",
            "username": "robot$test",
            "password": "test_password",
        }

        client = DockerClient(harbor_config)
        image_id = client.build_image(
            entrypoint="train.py",
            context_path=str(tmp_path),
            dockerfile_path=None,
            base_image="python:3.10-slim",
        )

        assert image_id == "sha256:abc123"
        mock_client.api.build.assert_called_once()

    @patch("keynet_train.clients.docker.docker")
    def test_build_image_with_custom_dockerfile(self, mock_docker):
        """사용자 제공 Dockerfile로 빌드"""
        from keynet_train.clients.docker import DockerClient

        # Mock Docker client
        mock_client = Mock()
        mock_logs = create_mock_build_logs("sha256:def456")
        mock_client.api.build.return_value = iter(mock_logs)
        mock_docker.from_env.return_value = mock_client

        harbor_config = {
            "url": "https://harbor.example.com",
            "username": "robot$test",
            "password": "test_password",
        }

        client = DockerClient(harbor_config)
        image_id = client.build_image(
            entrypoint="train.py",
            context_path="/tmp/test",
            dockerfile_path="/tmp/test/Dockerfile",
        )

        assert image_id == "sha256:def456"
        mock_client.api.build.assert_called_once()


class TestDockerClientTagImage:
    """Test DockerClient.tag_image()"""

    @patch("keynet_train.clients.docker.docker")
    def test_tag_image_success(self, mock_docker):
        """이미지 태깅 성공"""
        from keynet_train.clients.docker import DockerClient

        # Mock Docker client
        mock_client = Mock()
        mock_image = Mock()
        mock_client.images.get.return_value = mock_image
        mock_docker.from_env.return_value = mock_client

        harbor_config = {
            "url": "https://harbor.example.com",
            "username": "robot$test",
            "password": "test_password",
        }

        client = DockerClient(harbor_config)
        tagged_image = client.tag_image(
            image_id="sha256:abc123", project="kitech-model", upload_key="test_key"
        )

        # 태그가 없는 upload_key는 ":latest" 추가
        assert tagged_image == "harbor.example.com/kitech-model/test_key:latest"
        mock_client.images.get.assert_called_once_with("sha256:abc123")
        # Docker SDK API: tag(repository, tag)
        mock_image.tag.assert_called_once_with(
            repository="harbor.example.com/kitech-model/test_key", tag="latest"
        )


class TestDockerClientPushImage:
    """Test DockerClient.push_image()"""

    @patch("keynet_train.clients.docker.docker")
    def test_push_image_success(self, mock_docker):
        """이미지 푸시 성공"""
        from keynet_train.clients.docker import DockerClient

        # Mock Docker client
        mock_client = Mock()
        mock_client.images.push.return_value = iter([{"status": "Pushed"}])
        mock_docker.from_env.return_value = mock_client

        harbor_config = {
            "url": "https://harbor.example.com",
            "username": "robot$test",
            "password": "test_password",
        }

        client = DockerClient(harbor_config)
        client.push_image("harbor.example.com/kitech-model/test_key")

        # Docker SDK API: push(repository, tag, stream, decode)
        mock_client.images.push.assert_called_once_with(
            repository="harbor.example.com/kitech-model/test_key",
            tag=None,
            stream=True,
            decode=True,
        )
