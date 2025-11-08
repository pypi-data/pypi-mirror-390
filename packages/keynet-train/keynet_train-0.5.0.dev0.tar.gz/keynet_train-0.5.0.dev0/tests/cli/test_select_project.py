"""프로젝트 선택 UI 테스트"""

from unittest.mock import MagicMock, patch

import pytest

from keynet_train.cli.commands.push import select_project
from keynet_train.clients.models import (
    FetchTrainableProjectsResponse,
    PageMeta,
    TrainingProjectBrief,
)


@pytest.fixture
def mock_client():
    """Mock BackendClient fixture"""
    return MagicMock()


@pytest.fixture
def sample_projects_response():
    """샘플 프로젝트 응답 데이터"""
    return FetchTrainableProjectsResponse(
        content=[
            TrainingProjectBrief(
                id=1,
                title="MNIST 분류 프로젝트",
                summary="손글씨 숫자 분류",
                taskType="classification",
                author={"displayName": "홍길동", "id": 123},
            ),
            TrainingProjectBrief(
                id=2,
                title="CIFAR-10 프로젝트",
                summary="이미지 분류 실험",
                taskType="classification",
                author={"displayName": "김철수", "id": 456},
            ),
        ],
        meta=PageMeta(total=2, page=0, limit=20, maxPage=1),
    )


def test_select_project_success(mock_client, sample_projects_response):
    """프로젝트 선택 성공 케이스: 사용자가 유효한 선택 입력"""
    # BackendClient.fetch_trainable_projects() Mock
    mock_client.fetch_trainable_projects.return_value = sample_projects_response

    # 사용자 입력 Mock (1번 선택)
    with patch("builtins.input", return_value="1"):
        project_id = select_project(mock_client)

        # fetch_trainable_projects() 호출 확인
        mock_client.fetch_trainable_projects.assert_called_once_with(page=0, limit=20)

        # 반환된 project_id 확인
        assert project_id == 1


def test_select_project_empty_list(mock_client):
    """빈 프로젝트 목록 처리: ValueError 발생"""
    # 빈 응답 Mock
    empty_response = FetchTrainableProjectsResponse(
        content=[],
        meta=PageMeta(total=0, page=0, limit=20, maxPage=0),
    )
    mock_client.fetch_trainable_projects.return_value = empty_response

    # ValueError 발생 확인
    with pytest.raises(ValueError) as exc_info:
        select_project(mock_client)

    # 에러 메시지 확인
    assert "No trainable projects found" in str(exc_info.value)


def test_select_project_invalid_input_then_valid(mock_client, sample_projects_response):
    """잘못된 입력 후 올바른 입력: 재시도 성공"""
    mock_client.fetch_trainable_projects.return_value = sample_projects_response

    # 사용자 입력 Mock: 먼저 "abc" (ValueError), 그 다음 "1" (성공)
    with patch("builtins.input", side_effect=["abc", "1"]):
        project_id = select_project(mock_client)

        # 반환된 project_id 확인
        assert project_id == 1


def test_select_project_out_of_range_then_valid(mock_client, sample_projects_response):
    """범위 밖 숫자 입력 후 올바른 입력: 재시도 성공"""
    mock_client.fetch_trainable_projects.return_value = sample_projects_response

    # 사용자 입력 Mock: 먼저 "0", 그 다음 "999", 그 다음 "2" (성공)
    with patch("builtins.input", side_effect=["0", "999", "2"]):
        project_id = select_project(mock_client)

        # 반환된 project_id 확인 (2번째 프로젝트 ID는 2)
        assert project_id == 2


def test_select_project_api_error_propagates(mock_client):
    """API 에러 시 예외 전파"""
    # fetch_trainable_projects()가 예외를 발생시키도록 설정
    mock_client.fetch_trainable_projects.side_effect = ConnectionError(
        "Failed to connect to API"
    )

    # ConnectionError가 그대로 전파되는지 확인
    with pytest.raises(ConnectionError) as exc_info:
        select_project(mock_client)

    # 에러 메시지 확인
    assert "Failed to connect to API" in str(exc_info.value)
