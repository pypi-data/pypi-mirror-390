"""Shared test fixtures and helpers for client tests"""


def create_mock_build_logs(image_id="sha256:abc123", error=None):
    """
    빌드 로그를 시뮬레이션하는 헬퍼 함수

    Args:
        image_id: 반환할 이미지 ID
        error: 에러 메시지 (None이면 성공)

    Returns:
        빌드 로그 리스트 (iterable)

    """
    if error:
        return [
            {"stream": "Step 1/3: FROM python:3.10-slim"},
            {"error": error, "errorDetail": {"message": error}},
        ]
    else:
        return [
            {"stream": "Step 1/3: FROM python:3.10-slim"},
            {"stream": "Step 2/3: WORKDIR /workspace"},
            {"stream": "Step 3/3: COPY . ."},
            {"stream": "Successfully built abc123"},
            {"aux": {"ID": image_id}},
        ]
