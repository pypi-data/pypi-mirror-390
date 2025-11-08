"""
E2E 통합 테스트

이 모듈은 실제 Backend API와 Podman을 사용하여
전체 push 워크플로우를 검증합니다.

환경변수 요구사항:
- E2E_SERVER_URL: Backend API 서버 URL
- E2E_API_KEY: Backend API 인증 키
- E2E_HARBOR_URL: Harbor 레지스트리 URL
- E2E_HARBOR_USERNAME: Harbor 사용자명
- E2E_HARBOR_PASSWORD: Harbor 비밀번호
"""

import argparse
import os

import pytest

from keynet_train.cli.commands.push import handle_push


@pytest.fixture
def e2e_environment():
    """E2E 테스트 환경변수 검증 fixture"""
    required_vars = {
        "E2E_SERVER_URL": os.getenv("E2E_SERVER_URL"),
        "E2E_API_KEY": os.getenv("E2E_API_KEY"),
        "E2E_HARBOR_URL": os.getenv("E2E_HARBOR_URL"),
        "E2E_HARBOR_USERNAME": os.getenv("E2E_HARBOR_USERNAME"),
        "E2E_HARBOR_PASSWORD": os.getenv("E2E_HARBOR_PASSWORD"),
    }

    missing = [k for k, v in required_vars.items() if not v]

    if missing:
        pytest.skip(
            f"E2E test environment not configured. Missing: {', '.join(missing)}"
        )

    return required_vars


@pytest.fixture
def e2e_args(tmp_path):
    """E2E 테스트용 argparse.Namespace fixture"""
    # 임시 train.py 생성
    train_file = tmp_path / "train.py"
    train_file.write_text(
        """
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    print(f"Training with lr={args.lr}, epochs={args.epochs}")

if __name__ == "__main__":
    main()
"""
    )

    args = argparse.Namespace()
    args.entrypoint = str(train_file)
    args.dockerfile = None  # 자동 생성
    args.tag = None
    args.no_cache = False
    args.context = str(tmp_path)
    args.base_image = "python:3.10-slim"
    args.project = None  # 기본값 사용
    args.model_name = "e2e-test-model"
    return args


@pytest.mark.e2e
def test_full_push_workflow(e2e_environment, e2e_args, monkeypatch):
    """
    실제 Backend API + Podman으로 전체 워크플로우 테스트

    이 테스트는:
    1. 실제 Backend API에 인증
    2. 실제 프로젝트 선택 (자동 선택 또는 첫 번째 프로젝트)
    3. 실제 uploadKey 요청
    4. 실제 컨테이너 이미지 빌드
    5. 실제 Harbor 레지스트리에 푸시

    주의: 이 테스트는 실제 리소스를 사용하므로 신중하게 실행하세요.
    """
    # ConfigManager가 E2E 환경변수를 사용하도록 monkeypatch
    # (실제 ~/.keynet-train/config.json 대신 환경변수 사용)
    from keynet_train.cli.config.manager import ConfigManager

    def mock_get_server_url(self):
        return e2e_environment["E2E_SERVER_URL"]

    def mock_get_api_key(self):
        return e2e_environment["E2E_API_KEY"]

    def mock_get_harbor_credentials(self):
        return {
            "url": e2e_environment["E2E_HARBOR_URL"],
            "username": e2e_environment["E2E_HARBOR_USERNAME"],
            "password": e2e_environment["E2E_HARBOR_PASSWORD"],
        }

    monkeypatch.setattr(ConfigManager, "get_server_url", mock_get_server_url)
    monkeypatch.setattr(ConfigManager, "get_api_key", mock_get_api_key)
    monkeypatch.setattr(
        ConfigManager, "get_harbor_credentials", mock_get_harbor_credentials
    )

    # select_project를 자동으로 첫 번째 프로젝트 선택하도록 monkeypatch
    from unittest.mock import patch

    def mock_select_project(client, page=0, limit=20):
        """첫 번째 trainable 프로젝트 자동 선택"""
        response = client.fetch_trainable_projects(page=page, limit=limit)
        if not response.content:
            raise ValueError("No trainable projects found")
        return response.content[0].id

    with patch(
        "keynet_train.cli.commands.push.select_project", side_effect=mock_select_project
    ):
        # 실제 handle_push 실행
        exit_code = handle_push(e2e_args)

        # 검증: 성공적으로 완료되어야 함
        assert exit_code == 0, "E2E push workflow should complete successfully"


@pytest.mark.e2e
@pytest.mark.skipif(
    os.getenv("E2E_CLEANUP") != "true",
    reason="Cleanup test only runs when E2E_CLEANUP=true",
)
def test_e2e_cleanup():
    """
    E2E 테스트 후 정리 작업

    이 테스트는:
    - Harbor에 푸시된 테스트 이미지 삭제 (선택사항)
    - 로컬 Podman 이미지 정리

    E2E_CLEANUP=true 환경변수가 설정된 경우에만 실행됩니다.
    """
    import subprocess

    # 로컬 e2e-test-model 이미지 삭제
    result = subprocess.run(
        ["podman", "images", "-q", "e2e-test-model"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip():
        image_ids = result.stdout.strip().split("\n")
        for image_id in image_ids:
            subprocess.run(["podman", "rmi", "-f", image_id], check=False)

    # 검증: cleanup은 항상 성공으로 처리
    assert True
