"""프로젝트 목록 조회 테스트"""

import pytest

from keynet_train.clients.backend import (
    AuthenticationError,
    BackendClient,
    NetworkError,
    ServerError,
)


def test_fetch_trainable_projects_success(httpx_mock):
    """프로젝트 목록 조회 성공"""
    httpx_mock.add_response(
        method="GET",
        url="http://api.test/v1/projects/trainable?page=0&limit=20",
        json={
            "content": [
                {
                    "id": 123,
                    "title": "객체 탐지",
                    "summary": "설명",
                    "taskType": "OBJECT_DETECTION",
                    "author": {"id": "uuid", "displayName": "홍길동"},
                }
            ],
            "meta": {"total": 1, "page": 0, "limit": 20, "maxPage": 0},
        },
    )

    client = BackendClient("http://api.test", "token")
    response = client.fetch_trainable_projects()

    assert len(response.content) == 1
    assert response.content[0].id == 123
    assert response.content[0].title == "객체 탐지"
    assert response.content[0].task_type == "OBJECT_DETECTION"

    client.close()


def test_fetch_trainable_projects_empty(httpx_mock):
    """빈 프로젝트 목록 처리"""
    httpx_mock.add_response(
        method="GET",
        url="http://api.test/v1/projects/trainable?page=0&limit=20",
        json={
            "content": [],
            "meta": {"total": 0, "page": 0, "limit": 20, "maxPage": 0},
        },
    )

    client = BackendClient("http://api.test", "token")
    response = client.fetch_trainable_projects()

    assert len(response.content) == 0
    assert response.meta.total == 0

    client.close()


def test_fetch_trainable_projects_with_pagination(httpx_mock):
    """페이지네이션 파라미터 전달 테스트"""
    httpx_mock.add_response(
        method="GET",
        url="http://api.test/v1/projects/trainable?page=1&limit=10",
        json={
            "content": [],
            "meta": {"total": 0, "page": 1, "limit": 10, "maxPage": 0},
        },
    )

    client = BackendClient("http://api.test", "token")
    response = client.fetch_trainable_projects(page=1, limit=10)

    assert response.meta.page == 1
    assert response.meta.limit == 10

    client.close()


def test_fetch_trainable_projects_authentication_error(httpx_mock):
    """401 응답 시 AuthenticationError 발생"""
    httpx_mock.add_response(
        method="GET",
        url="http://api.test/v1/projects/trainable?page=0&limit=20",
        status_code=401,
        json={"detail": "Unauthorized"},
    )

    client = BackendClient("http://api.test", "token")

    with pytest.raises(AuthenticationError) as exc_info:
        client.fetch_trainable_projects()

    assert "401" in str(exc_info.value)

    client.close()


def test_fetch_trainable_projects_forbidden_error(httpx_mock):
    """403 응답 시 AuthenticationError 발생"""
    httpx_mock.add_response(
        method="GET",
        url="http://api.test/v1/projects/trainable?page=0&limit=20",
        status_code=403,
        json={"detail": "Forbidden"},
    )

    client = BackendClient("http://api.test", "token")

    with pytest.raises(AuthenticationError) as exc_info:
        client.fetch_trainable_projects()

    assert "403" in str(exc_info.value)

    client.close()


def test_fetch_trainable_projects_server_error(httpx_mock):
    """500 응답 시 ServerError 발생"""
    httpx_mock.add_response(
        method="GET",
        url="http://api.test/v1/projects/trainable?page=0&limit=20",
        status_code=500,
        json={"detail": "Internal Server Error"},
    )

    client = BackendClient("http://api.test", "token")

    with pytest.raises(ServerError) as exc_info:
        client.fetch_trainable_projects()

    assert "500" in str(exc_info.value)

    client.close()


def test_fetch_trainable_projects_network_error(httpx_mock):
    """네트워크 연결 실패 시 NetworkError 발생"""
    import httpx

    # httpx_mock이 아닌 실제 네트워크 에러를 시뮬레이션하기 위해
    # httpx.ConnectError를 발생시키는 콜백 사용
    def raise_connect_error(request):
        raise httpx.ConnectError("Connection failed")

    httpx_mock.add_callback(raise_connect_error)

    client = BackendClient("http://api.test", "token")

    with pytest.raises(NetworkError) as exc_info:
        client.fetch_trainable_projects()

    assert "Network error" in str(exc_info.value)

    client.close()
