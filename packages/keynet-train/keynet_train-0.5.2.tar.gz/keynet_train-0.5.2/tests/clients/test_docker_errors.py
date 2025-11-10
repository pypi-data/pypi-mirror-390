"""Docker 클라이언트 에러 클래스 테스트"""

from keynet_train.clients.docker import (
    BuildError,
    DockerError,
    ImageNotFoundError,
    PushError,
)


def test_docker_error_inheritance():
    """DockerError가 Exception을 상속하는지 확인"""
    error = DockerError("test error")
    assert isinstance(error, Exception)
    assert str(error) == "test error"


def test_build_error_inheritance():
    """BuildError가 DockerError를 상속하는지 확인"""
    error = BuildError("build failed")
    assert isinstance(error, DockerError)
    assert isinstance(error, Exception)
    assert str(error) == "build failed"


def test_image_not_found_error_inheritance():
    """ImageNotFoundError가 DockerError를 상속하는지 확인"""
    error = ImageNotFoundError("image not found")
    assert isinstance(error, DockerError)
    assert isinstance(error, Exception)
    assert str(error) == "image not found"


def test_push_error_inheritance():
    """PushError가 DockerError를 상속하는지 확인"""
    error = PushError("push failed")
    assert isinstance(error, DockerError)
    assert isinstance(error, Exception)
    assert str(error) == "push failed"


def test_error_hierarchy():
    """에러 클래스 계층 구조 확인"""
    # BuildError -> DockerError -> Exception
    build_error = BuildError("test")
    assert isinstance(build_error, BuildError)
    assert isinstance(build_error, DockerError)
    assert isinstance(build_error, Exception)

    # ImageNotFoundError -> DockerError -> Exception
    image_error = ImageNotFoundError("test")
    assert isinstance(image_error, ImageNotFoundError)
    assert isinstance(image_error, DockerError)
    assert isinstance(image_error, Exception)

    # PushError -> DockerError -> Exception
    push_error = PushError("test")
    assert isinstance(push_error, PushError)
    assert isinstance(push_error, DockerError)
    assert isinstance(push_error, Exception)
