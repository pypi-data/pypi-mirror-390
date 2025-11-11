"""DockerClient _generate_dockerfile 메서드 테스트"""

from keynet_train.clients.docker import DockerClient


def test_generate_dockerfile_basic_structure():
    """기본 Dockerfile 생성 (base_image + entrypoint)"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    dockerfile = client._generate_dockerfile(
        entrypoint="train.py", base_image="python:3.10-slim"
    )

    # FROM 구문 확인
    assert "FROM python:3.10-slim" in dockerfile
    # WORKDIR 확인
    assert "WORKDIR /workspace" in dockerfile
    # ENTRYPOINT 확인
    assert 'ENTRYPOINT ["python", "train.py"]' in dockerfile


def test_generate_dockerfile_includes_copy_workspace():
    """COPY . /workspace/ 포함 확인"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    dockerfile = client._generate_dockerfile(
        entrypoint="train.py", base_image="python:3.10-slim"
    )

    assert "COPY . /workspace/" in dockerfile


def test_generate_dockerfile_includes_requirements_install():
    """requirements.txt 자동 설치 로직 확인"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    dockerfile = client._generate_dockerfile(
        entrypoint="train.py", base_image="python:3.10-slim"
    )

    # requirements.txt 존재 시 설치하는 RUN 구문 확인
    assert "RUN" in dockerfile
    assert "requirements.txt" in dockerfile
    assert "pip install" in dockerfile


def test_generate_dockerfile_entrypoint_with_path():
    """entrypoint가 경로 포함 시 파일명만 추출"""
    harbor_config = {
        "url": "https://harbor.example.com",
        "username": "test_user",
        "password": "test_password",
    }
    client = DockerClient(harbor_config)

    dockerfile = client._generate_dockerfile(
        entrypoint="scripts/training/train.py", base_image="python:3.10-slim"
    )

    # 경로를 제거하고 파일명만 사용
    assert 'ENTRYPOINT ["python", "train.py"]' in dockerfile
    assert "scripts/training" not in dockerfile or "COPY" in dockerfile
