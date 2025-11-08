"""DockerClient _normalize_registry 메서드 테스트"""

from keynet_train.clients.docker import DockerClient


def test_normalize_registry_removes_https():
    """https:// 스킴 제거"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("https://harbor.example.com")

    assert result == "harbor.example.com"
    assert "https://" not in result


def test_normalize_registry_removes_http():
    """http:// 스킴 제거"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("http://harbor.example.com")

    assert result == "harbor.example.com"
    assert "http://" not in result


def test_normalize_registry_removes_trailing_slash():
    """트레일링 슬래시 제거"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("https://harbor.example.com/")

    assert result == "harbor.example.com"
    assert not result.endswith("/")


def test_normalize_registry_preserves_port():
    """포트 포함 URL 처리 - 포트는 유지되어야 함"""
    harbor_config = {
        "url": "https://harbor.example.com:8443",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("https://harbor.example.com:8443")

    assert result == "harbor.example.com:8443"
    assert ":8443" in result


def test_normalize_registry_removes_whitespace():
    """앞뒤 공백 제거"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("  https://harbor.example.com  ")

    assert result == "harbor.example.com"
    assert result == result.strip()


def test_normalize_registry_complex_case():
    """복합 케이스: https + 포트 + 트레일링 슬래시 + 공백"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("  https://harbor.example.com:8443/  ")

    assert result == "harbor.example.com:8443"
    assert "https://" not in result
    assert not result.endswith("/")
    assert ":8443" in result


def test_normalize_registry_already_normalized():
    """이미 정규화된 URL은 변경되지 않음"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("harbor.example.com")

    assert result == "harbor.example.com"


def test_normalize_registry_with_subdomain():
    """서브도메인이 포함된 URL 처리"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    result = client._normalize_registry("https://registry.harbor.example.com")

    assert result == "registry.harbor.example.com"
    assert "https://" not in result
