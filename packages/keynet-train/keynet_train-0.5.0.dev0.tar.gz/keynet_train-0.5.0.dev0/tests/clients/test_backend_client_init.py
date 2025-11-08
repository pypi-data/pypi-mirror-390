"""BackendClient 초기화 테스트"""

import httpx

from keynet_train.clients.backend import BackendClient


def test_backend_client_initialization():
    """BackendClient가 base_url과 api_key로 올바르게 초기화되는지 검증"""
    base_url = "http://api.test.com"
    api_key = "test-api-key"

    client = BackendClient(base_url=base_url, api_key=api_key)

    assert client.base_url == base_url
    assert client.api_key == api_key
    assert client._client is not None

    client.close()


def test_backend_client_bearer_token_header():
    """Bearer token 헤더가 자동으로 추가되는지 검증"""
    api_key = "test-api-key"

    client = BackendClient(base_url="http://api.test.com", api_key=api_key)

    # httpx.Client의 헤더에 Authorization이 포함되어 있는지 확인
    assert "Authorization" in client._client.headers
    assert client._client.headers["Authorization"] == f"Bearer {api_key}"

    client.close()


def test_backend_client_timeout_configuration():
    """타임아웃이 올바르게 설정되는지 검증"""
    client = BackendClient(
        base_url="http://api.test.com", api_key="test-key", timeout=30.0
    )

    # httpx.Client의 타임아웃 설정 확인
    assert client._client.timeout == httpx.Timeout(30.0)

    client.close()


def test_backend_client_default_timeout():
    """기본 타임아웃이 30초로 설정되는지 검증"""
    client = BackendClient(base_url="http://api.test.com", api_key="test-key")

    # 기본 타임아웃은 30초
    assert client._client.timeout == httpx.Timeout(30.0)

    client.close()


def test_backend_client_context_manager():
    """Context manager로 사용 가능한지 검증"""
    with BackendClient(base_url="http://api.test.com", api_key="test-key") as client:
        assert client._client is not None
        assert not client._client.is_closed

    # with 블록을 벗어나면 자동으로 close되어야 함
    assert client._client.is_closed
