"""BackendClient 에러 클래스 테스트"""

from keynet_train.clients.backend import (
    AuthenticationError,
    BackendAPIError,
    NetworkError,
    ServerError,
    ValidationError,
)


def test_backend_api_error_is_base_exception():
    """BackendAPIError가 Exception을 상속하는지 검증"""
    error = BackendAPIError("Test error")
    assert isinstance(error, Exception)
    assert str(error) == "Test error"


def test_authentication_error_inherits_backend_api_error():
    """AuthenticationError가 BackendAPIError를 상속하는지 검증"""
    error = AuthenticationError("Auth failed")
    assert isinstance(error, BackendAPIError)
    assert isinstance(error, Exception)
    assert str(error) == "Auth failed"


def test_validation_error_inherits_backend_api_error():
    """ValidationError가 BackendAPIError를 상속하는지 검증"""
    error = ValidationError("Validation failed")
    assert isinstance(error, BackendAPIError)
    assert isinstance(error, Exception)
    assert str(error) == "Validation failed"


def test_network_error_inherits_backend_api_error():
    """NetworkError가 BackendAPIError를 상속하는지 검증"""
    error = NetworkError("Connection failed")
    assert isinstance(error, BackendAPIError)
    assert isinstance(error, Exception)
    assert str(error) == "Connection failed"


def test_server_error_inherits_backend_api_error():
    """ServerError가 BackendAPIError를 상속하는지 검증"""
    error = ServerError("Server error")
    assert isinstance(error, BackendAPIError)
    assert isinstance(error, Exception)
    assert str(error) == "Server error"


def test_error_hierarchy():
    """모든 에러가 올바른 계층 구조를 가지는지 검증"""
    # 모든 커스텀 에러는 BackendAPIError를 상속
    errors = [
        AuthenticationError("test"),
        ValidationError("test"),
        NetworkError("test"),
        ServerError("test"),
    ]

    for error in errors:
        assert isinstance(error, BackendAPIError)
        assert isinstance(error, Exception)


def test_error_message_preservation():
    """에러 메시지가 올바르게 보존되는지 검증"""
    test_message = "Custom error message with details"

    error = BackendAPIError(test_message)
    assert str(error) == test_message

    error = AuthenticationError(test_message)
    assert str(error) == test_message

    error = ValidationError(test_message)
    assert str(error) == test_message

    error = NetworkError(test_message)
    assert str(error) == test_message

    error = ServerError(test_message)
    assert str(error) == test_message
