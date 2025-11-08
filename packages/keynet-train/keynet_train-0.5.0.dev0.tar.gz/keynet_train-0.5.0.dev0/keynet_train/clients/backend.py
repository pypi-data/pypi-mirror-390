"""Backend API Client"""

import httpx

from keynet_train.clients.models import (
    FetchTrainableProjectsResponse,
    UploadKeyRequest,
    UploadKeyResponse,
)


# 에러 클래스 계층 구조
class BackendAPIError(Exception):
    """Backend API 에러 베이스 클래스"""

    pass


class AuthenticationError(BackendAPIError):
    """인증 실패 (401/403)"""

    pass


class ValidationError(BackendAPIError):
    """검증 실패 (400/422)"""

    pass


class NetworkError(BackendAPIError):
    """네트워크 연결 실패"""

    pass


class ServerError(BackendAPIError):
    """서버 에러 (5xx)"""

    pass


class BackendClient:
    """Backend API와 통신하는 클라이언트"""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0):
        """
        BackendClient 초기화

        Args:
            base_url: Backend API URL
            api_key: API 인증 키
            timeout: HTTP 요청 타임아웃 (초)

        """
        self.base_url = base_url
        self.api_key = api_key
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(timeout),
        )

    def close(self):
        """HTTP 클라이언트 종료"""
        self._client.close()

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """
        공통 HTTP 요청 래퍼

        Args:
            method: HTTP 메서드 (GET, POST 등)
            endpoint: API 엔드포인트 경로
            **kwargs: httpx.Client.request()에 전달할 추가 인자

        Returns:
            httpx.Response: HTTP 응답 객체

        Raises:
            AuthenticationError: 401/403 응답
            ValidationError: 400/422 응답
            ServerError: 5xx 응답
            NetworkError: 네트워크 연결 실패

        """
        try:
            response = self._client.request(
                method, f"{self.base_url}{endpoint}", **kwargs
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")

    def fetch_trainable_projects(
        self, page: int = 0, limit: int = 20
    ) -> FetchTrainableProjectsResponse:
        """
        훈련 가능한 프로젝트 목록 조회

        Args:
            page: 페이지 번호 (0부터 시작)
            limit: 페이지당 항목 수

        Returns:
            FetchTrainableProjectsResponse: 프로젝트 목록과 페이지네이션 정보

        Raises:
            NetworkError: 네트워크 연결 실패
            AuthenticationError: 인증 실패
            ServerError: 서버 에러

        """
        response = self._request(
            "GET", "/v1/projects/trainable", params={"page": page, "limit": limit}
        )
        return FetchTrainableProjectsResponse(**response.json())

    def request_upload_key(
        self, project_id: int, request: UploadKeyRequest
    ) -> UploadKeyResponse:
        """
        훈련 이미지 업로드 키 발급 요청

        Args:
            project_id: 프로젝트 ID
            request: UploadKey 요청 정보 (모델명, 하이퍼파라미터)

        Returns:
            UploadKeyResponse: 업로드 키 및 명령어 정보

        Raises:
            NetworkError: 네트워크 연결 실패
            AuthenticationError: 인증 실패
            ValidationError: 요청 검증 실패
            ServerError: 서버 에러

        """
        response = self._request(
            "POST",
            f"/v1/projects/{project_id}/trains/images",
            json=request.model_dump(by_alias=True),
        )
        return UploadKeyResponse(**response.json())

    def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
        """
        HTTP 에러를 적절한 예외로 변환

        Args:
            error: httpx.HTTPStatusError

        Raises:
            AuthenticationError: 401/403 응답
            ValidationError: 400/422 응답
            ServerError: 5xx 응답
            BackendAPIError: 기타 HTTP 에러

        """
        status_code = error.response.status_code

        if status_code in (401, 403):
            raise AuthenticationError(f"Authentication failed: {status_code}")
        elif status_code in (400, 422):
            raise ValidationError(f"Validation failed: {status_code}")
        elif 500 <= status_code < 600:
            raise ServerError(f"Server error: {status_code}")
        else:
            raise BackendAPIError(f"API error: {status_code}")
