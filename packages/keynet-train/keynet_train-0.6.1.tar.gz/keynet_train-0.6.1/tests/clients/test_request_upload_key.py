"""UploadKey 발급 테스트"""

import pytest

from keynet_train.clients.backend import (
    AuthenticationError,
    BackendClient,
    NetworkError,
    ServerError,
    ValidationError,
)
from keynet_train.clients.models import (
    ArgumentDefinition,
    ArgumentType,
    UploadKeyCommand,
    UploadKeyRequest,
)


def test_request_upload_key_success(httpx_mock):
    """UploadKey 발급 성공"""
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        json={
            "id": 456,
            "projectId": 207,
            "uploadKey": "abc-def-ghi",
            "model": {"id": 42, "name": "my_model"},
            "command": {
                "tag": "docker tag test",
                "push": "docker push kitech-harbor.wimcorp.dev/kitech-model/test:latest",
            },
        },
    )

    client = BackendClient("http://api.test", "token")
    request = UploadKeyRequest(
        model_name="my_model",
        hyper_parameters=[],
    )

    response = client.request_upload_key(project_id=123, request=request)

    assert response.id == 456
    assert response.upload_key == "abc-def-ghi"
    assert isinstance(response.command, UploadKeyCommand)
    assert response.command.tag == "docker tag test"
    assert (
        response.command.push
        == "docker push kitech-harbor.wimcorp.dev/kitech-model/test:latest"
    )

    client.close()


def test_request_upload_key_with_hyperparameters(httpx_mock):
    """하이퍼파라미터 포함하여 uploadKey 발급"""
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        json={
            "id": 789,
            "projectId": 207,
            "uploadKey": "xyz-123-456",
            "model": {"id": 43, "name": "advanced_model"},
            "command": {
                "tag": "docker tag test",
                "push": "docker push kitech-harbor.wimcorp.dev/kitech-model/test:latest",
            },
        },
    )

    client = BackendClient("http://api.test", "token")

    hyper_params = [
        ArgumentDefinition(
            name="learning_rate",
            type=ArgumentType.FLOAT,
            default=0.001,
            required=True,
            help="Learning rate",
        ),
        ArgumentDefinition(
            name="batch_size",
            type=ArgumentType.INTEGER,
            default=32,
            required=False,
        ),
    ]

    request = UploadKeyRequest(
        model_name="advanced_model",
        hyper_parameters=hyper_params,
    )

    response = client.request_upload_key(project_id=123, request=request)

    assert response.id == 789
    assert response.upload_key == "xyz-123-456"

    client.close()


def test_request_upload_key_sends_camelcase_json(httpx_mock):
    """하이퍼파라미터가 camelCase로 전송되는지 검증"""
    # match_json으로 전송되는 JSON 구조 검증
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        match_json={
            "modelName": "test_model",
            "hyperParameters": [
                {
                    "name": "learning_rate",
                    "type": "float",
                    "default": 0.001,
                    "required": True,
                    "help": "Learning rate",
                    "choices": None,
                },
                {
                    "name": "batch_size",
                    "type": "int",
                    "default": 32,
                    "required": False,
                    "help": None,
                    "choices": None,
                },
            ],
        },
        json={
            "id": 999,
            "projectId": 207,
            "uploadKey": "test-key",
            "model": {"id": 44, "name": "test_model"},
            "command": {
                "tag": "docker tag test",
                "push": "docker push kitech-harbor.wimcorp.dev/kitech-model/test:latest",
            },
        },
    )

    client = BackendClient("http://api.test", "token")

    hyper_params = [
        ArgumentDefinition(
            name="learning_rate",
            type=ArgumentType.FLOAT,
            default=0.001,
            required=True,
            help="Learning rate",
        ),
        ArgumentDefinition(
            name="batch_size",
            type=ArgumentType.INTEGER,
            default=32,
            required=False,
        ),
    ]

    request = UploadKeyRequest(
        model_name="test_model",
        hyper_parameters=hyper_params,
    )

    response = client.request_upload_key(project_id=123, request=request)

    # 응답 검증
    assert response.id == 999
    assert response.upload_key == "test-key"

    client.close()


def test_request_upload_key_authentication_error(httpx_mock):
    """401 응답 시 AuthenticationError 발생"""
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        status_code=401,
        json={"detail": "Unauthorized"},
    )

    client = BackendClient("http://api.test", "token")
    request = UploadKeyRequest(
        model_name="test_model",
        hyper_parameters=[],
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.request_upload_key(project_id=123, request=request)

    assert "401" in str(exc_info.value)

    client.close()


def test_request_upload_key_forbidden_error(httpx_mock):
    """403 응답 시 AuthenticationError 발생"""
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        status_code=403,
        json={"detail": "Forbidden"},
    )

    client = BackendClient("http://api.test", "token")
    request = UploadKeyRequest(
        model_name="test_model",
        hyper_parameters=[],
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client.request_upload_key(project_id=123, request=request)

    assert "403" in str(exc_info.value)

    client.close()


def test_request_upload_key_validation_error_400(httpx_mock):
    """400 응답 시 ValidationError 발생"""
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        status_code=400,
        json={"detail": "Bad Request"},
    )

    client = BackendClient("http://api.test", "token")
    request = UploadKeyRequest(
        model_name="test_model",
        hyper_parameters=[],
    )

    with pytest.raises(ValidationError) as exc_info:
        client.request_upload_key(project_id=123, request=request)

    assert "400" in str(exc_info.value)

    client.close()


def test_request_upload_key_validation_error_422(httpx_mock):
    """422 응답 시 ValidationError 발생"""
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        status_code=422,
        json={"detail": "Unprocessable Entity"},
    )

    client = BackendClient("http://api.test", "token")
    request = UploadKeyRequest(
        model_name="test_model",
        hyper_parameters=[],
    )

    with pytest.raises(ValidationError) as exc_info:
        client.request_upload_key(project_id=123, request=request)

    assert "422" in str(exc_info.value)

    client.close()


def test_request_upload_key_server_error(httpx_mock):
    """500 응답 시 ServerError 발생"""
    httpx_mock.add_response(
        method="POST",
        url="http://api.test/v1/projects/123/trains/images",
        status_code=500,
        json={"detail": "Internal Server Error"},
    )

    client = BackendClient("http://api.test", "token")
    request = UploadKeyRequest(
        model_name="test_model",
        hyper_parameters=[],
    )

    with pytest.raises(ServerError) as exc_info:
        client.request_upload_key(project_id=123, request=request)

    assert "500" in str(exc_info.value)

    client.close()


def test_request_upload_key_network_error(httpx_mock):
    """네트워크 연결 실패 시 NetworkError 발생"""
    import httpx

    # 네트워크 에러 시뮬레이션
    def raise_connect_error(request):
        raise httpx.ConnectError("Connection failed")

    httpx_mock.add_callback(raise_connect_error)

    client = BackendClient("http://api.test", "token")
    request = UploadKeyRequest(
        model_name="test_model",
        hyper_parameters=[],
    )

    with pytest.raises(NetworkError) as exc_info:
        client.request_upload_key(project_id=123, request=request)

    assert "Network error" in str(exc_info.value)

    client.close()
