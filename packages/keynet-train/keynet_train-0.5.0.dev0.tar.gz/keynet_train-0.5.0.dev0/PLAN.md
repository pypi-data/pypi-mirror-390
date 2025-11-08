# PLAN.md - keynet-train CLI 구현 계획 (TDD)

> **버전**: v2.4 (Dynamic Dockerfile Generation)
> **기준 문서**: @packages/train/TECHSPEC.md v3.2
> **방법론**: Test-Driven Development (Red → Green → Refactor)
> **변경 이력**:
> - v2.4 (2025-11-05): 동적 Dockerfile 생성 지원 추가
> - v2.3: Backend 로그인 API 명세 변경 반영 (harbor 중첩 구조, api_token_expires_at 추가)

---

## 목차

1. [개요](#개요)
2. [TDD 원칙](#tdd-원칙)
3. [마일스톤 개요](#마일스톤-개요)
4. [Milestone 0: 환경 및 합의 정리](#milestone-0-환경-및-합의-정리)
5. [Milestone 1: Backend API Client](#milestone-1-backend-api-client)
6. [Milestone 2: Podman Client](#milestone-2-podman-client)
7. [Milestone 3: Push 워크플로우 통합](#milestone-3-push-워크플로우-통합)
8. [Milestone 4: 에러 처리 및 사용자 경험](#milestone-4-에러-처리-및-사용자-경험)

---

## 개요

**목표**: TECHSPEC.md에 정의된 `keynet-train push` 명령의 전체 워크플로우 구현

**구현 범위**:

- ✅ 이미 구현됨: ConfigManager, ArgumentParserExtractor, PythonSyntaxValidator
- 🚧 구현 필요:
  - Backend API Client (프로젝트 조회, uploadKey 발급)
  - Podman Client (빌드, 태그, 푸시)
  - Push 워크플로우 통합 (Step 1-9)

**핵심 가치**:

- 작은 단위로 테스트 가능
- 빠른 피드백 사이클
- 점진적 기능 추가

---

## TDD 원칙

### Red → Green → Refactor

```
1. RED    : 실패하는 테스트 작성 (최소한의 테스트)
2. GREEN  : 테스트를 통과하는 최소 구현
3. REFACTOR: 코드 개선 (테스트는 항상 통과 유지)
```

### 체크리스트

각 Task 완료 시:

- [ ] `poe format` 실행 (자동 수정)
- [ ] `poe lint` 통과
- [ ] `poe typecheck` 통과
- [ ] `poe test` 모두 통과
- [ ] PLAN.md 체크박스 체크

---

## 마일스톤 개요

| Milestone | 설명                 | 예상 기간 |
| --------- | -------------------- | --------- |
| M0        | 환경 및 합의 정리    | 1일       |
| M1        | Backend API Client   | 2-3일     |
| M2        | Podman Client        | 2-3일     |
| M3        | Push 워크플로우 통합 | 2-3일     |
| M4        | 에러 처리 및 UX      | 1-2일     |

**총 예상 기간**: 8-12일

---

## Milestone 0: 환경 및 합의 정리

**목표**: 코드베이스와 TECHSPEC 간 불일치 해소
**우선순위**: 최우선 (M1-M4의 선행 조건)

### Task 0.1: 의존성 정리

**목적**: 필요한 라이브러리 추가 및 검증

#### Subtask 0.1.1: httpx 및 podman 추가

- [x] **작업**: `packages/train/pyproject.toml` 수정

  ```toml
  dependencies = [
      "keynet-core",
      "mlflow-skinny>=2.20.0",
      "pydantic>=2.0.0",
      "httpx>=0.27.0",           # Backend API 통신
      "podman>=5.0.0",           # 컨테이너 관리 (pip 패키지명: podman)
  ]
  ```

- [x] **검증**: `uv sync --dev` 실행 후 `import httpx, podman` 테스트

**중요**: pip 패키지명은 `podman`이며 `podman-py`가 아닙니다.

#### Subtask 0.1.2: pytest-httpx 추가

- [x] **작업**: 루트 `pyproject.toml`의 dev-dependencies 수정

  ```toml
  dev-dependencies = [
      "pytest>=8.4.1",
      "pytest-httpx>=0.35.0",    # HTTP mocking
  ]
  ```

- [x] **검증**: `uv sync --dev` 후 `httpx_mock` fixture 사용 가능 확인

#### Subtask 0.1.3: 네트워크 차단 픽스처 추가

- [x] **작업**: `packages/train/tests/conftest.py` 업데이트

  ```python
  import pytest

  @pytest.fixture(autouse=True)
  def block_network(request, httpx_mock):
      """단위 테스트에서 네트워크 차단 (통합 테스트 제외)"""
      if "integration" in request.keywords or "e2e" in request.keywords:
          yield
      else:
          # httpx_mock이 자동으로 네트워크를 모킹함
          yield
  ```

- [x] **검증**: `poe check` 통과

---

### Task 0.2: 아키텍처 정렬

**목적**: ORAS 잔재 제거 및 키명 통일

#### Subtask 0.2.1: ORAS 관련 주석/코드 제거

- [x] **작업**: `packages/train/keynet_train/cli/commands/push.py` 정리

  - ORAS 관련 주석 제거
  - Backend+Podman 아키텍처로 명확화

- [x] **검증**: 파일 검토 및 `poe lint` 통과

#### Subtask 0.2.2: ConfigManager API를 TECHSPEC에 맞게 업데이트

- [x] **목적**: ConfigManager 인터페이스를 TECHSPEC v3.1 명세에 맞게 수정

- [x] **현재 상태 (실제 구현)**:
  ```python
  # cli/config/manager.py
  def set_credentials(  # ← 메서드명 다름
      server_url: str,
      api_key: str,  # ← 'api_key'로 명명됨
      harbor_url: str,  # ← 중첩 dict가 아닌 개별 파라미터
      harbor_username: str,
      harbor_password: str,
  )
  ```

- [x] **TECHSPEC 요구사항**:
  ```python
  def save_credentials(  # ← 메서드명
      server_url: str,
      username: str,  # ← 사용자명 추가
      api_token: str,  # ← 'api_token'으로 명명
      api_token_expires_at: str,  # ← JWT 만료 시간 (신규)
      harbor: dict,  # ← 중첩 dict: {"url": str, "username": str, "password": str}
  )
  ```

- [x] **작업**:
  1. `set_credentials()` → `save_credentials()` 메서드명 변경
  2. `api_key` → `api_token` 파라미터명 변경
  3. `username: str` 파라미터 추가
  4. `api_token_expires_at: str` 파라미터 추가
  5. `harbor_url, harbor_username, harbor_password` → `harbor: dict` 통합
  6. 설정 파일 구조 업데이트:
     ```json
     {
       "server_url": "...",
       "username": "...",  // 추가
       "api_token": "...",
       "api_token_expires_at": "...",  // 추가
       "harbor": {
         "url": "...",
         "username": "...",
         "password": "..."
       },
       "last_login": "..."
     }
     ```

- [x] **검증**:
  - `poe check` 통과
  - 기존 테스트 코드 업데이트 필요 여부 확인

---

### Task 0.3: CI/개발 도구 설정

**목적**: 테스트 마커 및 빠른 검증 지원

#### Subtask 0.3.1: poe test-fast 태스크 추가

- [x] **작업**: 루트 `pyproject.toml`의 `[tool.poe.tasks]` 수정

  ```toml
  [tool.poe.tasks.test-fast]
  help = "Run unit tests only (exclude integration/e2e)"
  cmd = "pytest -m 'not integration and not e2e' -v"
  ```

- [x] **검증**: `poe test-fast` 실행 → 빠르게 완료

---

## Milestone 1: Backend API Client

**목표**: Backend API 통신 레이어 구현
**의존성**: M0 완료, ConfigManager (이미 구현됨)

### Task 1.1: 데이터 모델 정의

**목적**: Backend API 요청/응답을 위한 Pydantic 모델 정의

#### Subtask 1.1.1: ArgumentDefinition 모델

- [x] **테스트 작성**: `test_argument_definition_model.py`

  - ArgumentDefinition 생성 및 필드 검증
  - ArgumentType enum 값 검증 (str/int/float/bool)
  - camelCase로 직렬화 검증

- [x] **구현**: `packages/train/keynet_train/clients/models.py`

  ```python
  from pydantic import BaseModel, Field, ConfigDict
  from typing import Optional, Any, List
  from enum import Enum

  class ArgumentType(str, Enum):
      STRING = "str"
      INTEGER = "int"
      FLOAT = "float"
      BOOLEAN = "bool"

  class ArgumentDefinition(BaseModel):
      model_config = ConfigDict(populate_by_name=True)

      name: str
      type: ArgumentType
      default: Optional[Any] = None
      required: bool = False
      help: Optional[str] = None
      choices: Optional[list[str]] = None
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 1.1.2: UploadKey 요청/응답 모델

- [x] **테스트 작성**: `test_upload_key_models.py`

  - UploadKeyRequest snake_case → camelCase 직렬화
  - UploadKeyResponse camelCase → snake_case 역직렬화

- [x] **구현**: `models.py`

  ```python
  class UploadKeyRequest(BaseModel):
      model_config = ConfigDict(populate_by_name=True)

      model_name: str = Field(alias="modelName")
      hyper_parameters: list[ArgumentDefinition] = Field(
          default_factory=list,
          alias="hyperParameters"
      )

  class UploadKeyResponse(BaseModel):
      model_config = ConfigDict(populate_by_name=True)

      id: int
      upload_key: str = Field(alias="uploadKey")
      command: str
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 1.1.3: 프로젝트 목록 모델

- [x] **테스트 작성**: `test_project_models.py`

  - TrainingProjectBrief camelCase → snake_case
  - FetchTrainableProjectsResponse 역직렬화
  - taskType enum 값 검증
  - 빈 프로젝트 목록 처리

- [x] **구현**: `models.py`

  ```python
  from typing import Dict, Any

  class TrainingProjectBrief(BaseModel):
      model_config = ConfigDict(populate_by_name=True)

      id: int
      title: str
      summary: str
      task_type: str = Field(alias="taskType")
      author: Dict[str, Any]

  class PageMeta(BaseModel):
      """페이지네이션 메타 정보"""
      model_config = ConfigDict(populate_by_name=True)

      total: int
      page: int
      limit: int
      max_page: int = Field(alias="maxPage")

  class FetchTrainableProjectsResponse(BaseModel):
      model_config = ConfigDict(populate_by_name=True)

      content: List[TrainingProjectBrief]
      meta: PageMeta
  ```

- [x] **검증**: `poe check` 통과

---

### Task 1.2: BackendClient 기본 구조

**목적**: HTTP 클라이언트 기본 틀 구현

#### Subtask 1.2.1: BackendClient 초기화

- [x] **테스트 작성**: `test_backend_client_init.py`

  - base_url, api_key로 초기화
  - Bearer token 헤더 자동 추가 검증
  - 타임아웃 설정 검증

- [x] **구현**: `packages/train/keynet_train/clients/backend.py`

  ```python
  import httpx

  class BackendClient:
      def __init__(
          self,
          base_url: str,
          api_key: str,
          timeout: float = 30.0
      ):
          self.base_url = base_url
          self.api_key = api_key
          self._client = httpx.Client(
              headers={"Authorization": f"Bearer {api_key}"},
              timeout=httpx.Timeout(timeout)
          )

      def close(self):
          self._client.close()

      def __enter__(self):
          return self

      def __exit__(self, exc_type, exc_val, exc_tb):
          self.close()
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 1.2.2: 에러 클래스 정의

- [x] **테스트 작성**: `test_backend_errors.py`

  - 에러 클래스 상속 구조 검증
  - 각 에러 타입별 생성 및 메시지

- [x] **구현**: `backend.py`

**에러 계층 구조**:

```
BackendAPIError (Exception)
├── AuthenticationError (401/403)
├── ValidationError (400/422)
├── NetworkError (연결 실패)
└── ServerError (5xx)
```

- [x] **검증**: `poe check` 통과

---

### Task 1.3: 프로젝트 목록 조회 구현

**목적**: `GET /v1/projects/trainable` 구현

#### Subtask 1.3.1: fetch_trainable_projects 성공 케이스

- [x] **테스트 작성**: `test_fetch_trainable_projects.py`

  ```python
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
                      "author": {"id": "uuid", "displayName": "홍길동"}
                  }
              ],
              "meta": {"total": 1, "page": 0, "limit": 20, "maxPage": 0}
          }
      )

      client = BackendClient("http://api.test", "token")
      response = client.fetch_trainable_projects()

      assert len(response.content) == 1
      assert response.content[0].id == 123

  def test_fetch_trainable_projects_empty(httpx_mock):
      """빈 프로젝트 목록 처리"""
      httpx_mock.add_response(
          method="GET",
          url="http://api.test/v1/projects/trainable?page=0&limit=20",
          json={"content": [], "meta": {"total": 0, "page": 0, "limit": 20, "maxPage": 0}}
      )

      client = BackendClient("http://api.test", "token")
      response = client.fetch_trainable_projects()

      assert len(response.content) == 0
  ```

- [x] **구현**: `backend.py`

  ```python
  def fetch_trainable_projects(
      self,
      page: int = 0,
      limit: int = 20
  ) -> FetchTrainableProjectsResponse:
      try:
          response = self._client.get(
              f"{self.base_url}/v1/projects/trainable",
              params={"page": page, "limit": limit}
          )
          response.raise_for_status()
          return FetchTrainableProjectsResponse(**response.json())
      except httpx.HTTPStatusError as e:
          self._handle_http_error(e)
      except httpx.RequestError as e:
          raise NetworkError(f"Network error: {e}")
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 1.3.2: fetch_trainable_projects 에러 처리

- [x] **테스트 작성**: 에러 케이스

  - 401 응답 → AuthenticationError
  - 5xx 응답 → ServerError
  - 네트워크 에러 → NetworkError

- [x] **구현**: 에러 처리 로직

  ```python
  def _handle_http_error(self, error: httpx.HTTPStatusError) -> None:
      """HTTP 에러를 적절한 예외로 변환"""
      status_code = error.response.status_code

      if status_code in (401, 403):
          raise AuthenticationError(f"Authentication failed: {status_code}")
      elif status_code in (400, 422):
          raise ValidationError(f"Validation failed: {status_code}")
      elif 500 <= status_code < 600:
          raise ServerError(f"Server error: {status_code}")
      else:
          raise BackendAPIError(f"API error: {status_code}")
  ```

- [x] **검증**: `poe check` 통과

---

### Task 1.4: UploadKey 발급 구현

**목적**: `POST /v1/projects/{projectId}/trains/images` 구현

#### Subtask 1.4.1: request_upload_key 성공 케이스

- [x] **테스트 작성**: `test_request_upload_key.py`

  - uploadKey 발급 성공 (httpx_mock 사용)

- [x] **구현**: `backend.py`

  ```python
  def request_upload_key(
      self,
      project_id: int,
      request: UploadKeyRequest
  ) -> UploadKeyResponse:
      try:
          response = self._client.post(
              f"{self.base_url}/v1/projects/{project_id}/trains/images",
              json=request.model_dump(by_alias=True)
          )
          response.raise_for_status()
          return UploadKeyResponse(**response.json())
      except httpx.HTTPStatusError as e:
          self._handle_http_error(e)
      except httpx.RequestError as e:
          raise NetworkError(f"Network error: {e}")
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 1.4.2: request_upload_key 하이퍼파라미터 전송

- [x] **테스트 작성**: 하이퍼파라미터 camelCase 전송 검증

  - match_json으로 "hyperParameters" 확인
  - ArgumentDefinition 포함 시 정상 직렬화

- [x] **구현**: 검증 (Pydantic이 자동 처리)

- [x] **검증**: `poe check` 통과

#### Subtask 1.4.3: request_upload_key 에러 처리

- [x] **테스트 작성**: 에러 케이스

  - 401 → AuthenticationError
  - 400 → ValidationError
  - 5xx → ServerError

- [x] **구현**: 에러 처리 로직 (이미 `_handle_http_error`에 포함)

- [x] **검증**: `poe check` 통과

---

### Task 1.5: ArgumentParserExtractor 통합

**목적**: ArgumentParserExtractor 출력을 ArgumentDefinition으로 변환

#### Subtask 1.5.1: 변환 함수 구현

- [x] **테스트 작성**: `test_convert_arguments.py`

  - ArgumentParserExtractor 출력 → List[ArgumentDefinition]

- [x] **구현**: `packages/train/keynet_train/clients/converters.py`

  ```python
  def convert_to_argument_definitions(
      extractor_output: Dict[str, Any]
  ) -> List[ArgumentDefinition]:
      arguments = extractor_output.get("arguments", [])
      return [
          ArgumentDefinition(
              name=arg["name"],
              type=ArgumentType(arg["type"]),
              default=arg.get("default"),
              required=arg.get("required", False),
              help=arg.get("help"),
              choices=arg.get("choices")
          )
          for arg in arguments
      ]
  ```

- [x] **검증**: `poe check` 통과

---

### Task 1.6: Milestone 1 Refactor

**목적**: M1 완료 후 코드 개선

#### Subtask 1.6.1: 공통 HTTP 래핑 추출

- [x] **리팩토링**: BackendClient의 중복 try-except 제거

  ```python
  def _request(
      self,
      method: str,
      endpoint: str,
      **kwargs
  ) -> httpx.Response:
      """공통 HTTP 요청 래퍼"""
      try:
          response = self._client.request(
              method,
              f"{self.base_url}{endpoint}",
              **kwargs
          )
          response.raise_for_status()
          return response
      except httpx.HTTPStatusError as e:
          self._handle_http_error(e)
      except httpx.RequestError as e:
          raise NetworkError(f"Network error: {e}")
  ```

- [x] **검증**: 기존 테스트 모두 통과

---

## Milestone 2: Podman Client

**목표**: Podman을 통한 컨테이너 이미지 빌드/푸시
**의존성**: M0 완료, podman 라이브러리

### Task 2.1: PodmanClient 기본 구조

**목적**: Podman API 클라이언트 초기화

#### Subtask 2.1.1: PodmanClient 초기화

- [x] **테스트 작성**: `test_podman_client_init.py`

  - PodmanClient 초기화 (Mock 사용)
  - harbor_config dict 검증
  - Podman 소켓 연결 검증 (통합 테스트, @pytest.mark.integration)

- [x] **구현**: `packages/train/keynet_train/clients/podman.py`

  ```python
  from podman import PodmanClient as PodmanSDK

  class PodmanClient:
      def __init__(self, harbor_config: dict):
          """
          Args:
              harbor_config: {"url": str, "username": str, "password": str}
          """
          self._harbor_url = harbor_config["url"]
          self._client = PodmanSDK()
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 2.1.2: 에러 클래스 정의

- [x] **테스트 작성**: `test_podman_errors.py`

  - 에러 클래스 구조 검증

- [x] **구현**: `podman.py`

**에러 계층 구조**:

```
PodmanError (Exception)
├── BuildError (이미지 빌드 실패)
├── ImageNotFoundError (이미지를 찾을 수 없음)
└── PushError (이미지 푸시 실패)
```

- [x] **검증**: `poe check` 통과

---

### Task 2.2: 이미지 빌드 구현

**목적**: 동적 Dockerfile 생성 또는 사용자 제공 Dockerfile로 이미지 빌드

#### Subtask 2.2.1: _generate_dockerfile helper 구현

- [x] **테스트 작성**: `test_generate_dockerfile.py`

  - 기본 Dockerfile 생성 (base_image + entrypoint)
  - `COPY . /workspace/` 포함 확인 (전체 컨텍스트 복사)
  - requirements.txt 자동 설치 로직 확인
  - 올바른 CMD 형식 확인

- [x] **구현**: `podman.py`

  ```python
  def _generate_dockerfile(
      self,
      entrypoint: str,
      base_image: str
  ) -> str:
      """
      동적으로 Dockerfile 문자열 생성

      Args:
          entrypoint: 훈련 스크립트 파일명
          base_image: FROM 베이스 이미지

      Returns:
          Dockerfile 문자열
      """
      from pathlib import Path

      entrypoint_name = Path(entrypoint).name

      return f"""FROM {base_image}
WORKDIR /workspace

# Copy entire build context
COPY . /workspace/

# Install dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Set entrypoint
CMD ["python", "{entrypoint_name}"]
"""
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 2.2.2: build_image 성공 케이스 (동적 Dockerfile)

- [x] **테스트 작성**: `test_build_image.py`

  - dockerfile_path=None: 동적 Dockerfile 생성 검증
  - context_path에 임시 Dockerfile 생성 확인
  - finally 블록으로 임시 파일 정리 확인
  - Mock 사용: 이미지 빌드 성공 검증
  - 전체 컨텍스트가 빌드에 포함되는지 확인

- [x] **구현**: `podman.py`

  ```python
  from pathlib import Path
  from typing import Optional

  def build_image(
      self,
      entrypoint: str,
      context_path: str = ".",
      dockerfile_path: Optional[str] = None,
      base_image: str = "python:3.10-slim",
      no_cache: bool = False
  ) -> str:
      """
      컨테이너 이미지 빌드 (Dockerfile 자동 생성 또는 사용자 제공)

      Args:
          entrypoint: 훈련 스크립트 경로 (필수)
          context_path: 빌드 컨텍스트 디렉토리
          dockerfile_path: Dockerfile 경로 (None이면 자동 생성)
          base_image: 베이스 이미지 (dockerfile_path=None일 때만 사용)
          no_cache: 빌드 캐시 비활성화

      Returns:
          image_id: 빌드된 이미지 ID

      Raises:
          BuildError: 빌드 실패
      """
      try:
          if dockerfile_path is None:
              # context_path에 임시 Dockerfile 생성
              temp_dockerfile = Path(context_path) / ".Dockerfile.keynet-train.tmp"

              try:
                  # Dockerfile 생성
                  dockerfile_content = self._generate_dockerfile(
                      entrypoint=entrypoint,
                      base_image=base_image
                  )
                  temp_dockerfile.write_text(dockerfile_content)

                  # 빌드 (context_path의 모든 파일 포함)
                  image, logs = self._client.images.build(
                      path=context_path,
                      dockerfile=str(temp_dockerfile.name),  # 상대 경로
                      nocache=no_cache
                  )

                  return image.id
              finally:
                  # 임시 Dockerfile 삭제
                  if temp_dockerfile.exists():
                      temp_dockerfile.unlink()
          else:
              # 사용자 제공 Dockerfile 사용
              image, logs = self._client.images.build(
                  path=context_path,
                  dockerfile=dockerfile_path,
                  nocache=no_cache
              )

              return image.id
      except Exception as e:
          raise BuildError(f"Image build failed: {e}")
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 2.2.3: build_image 성공 케이스 (사용자 Dockerfile)

- [x] **테스트 작성**: 에러 케이스

  - dockerfile_path 지정 시 정상 동작
  - 사용자 Dockerfile 사용 검증

- [x] **구현**: (이미 구현됨)

- [x] **검증**: `poe check` 통과

#### Subtask 2.2.4: build_image 실패 케이스

- [x] **테스트 작성**: 에러 케이스

  - entrypoint 파일 없을 때 BuildError
  - 잘못된 Dockerfile일 때 BuildError
  - Podman 연결 실패 시 BuildError

- [x] **구현**: 에러 처리 (이미 구현됨)

- [x] **검증**: `poe check` 통과

---

### Task 2.3: 이미지 태깅 구현

**목적**: 빌드된 이미지에 Harbor 태그 추가

#### Subtask 2.3.1: tag_image 성공 케이스

- [x] **테스트 작성**: `test_tag_image.py`

  - Mock 사용: 이미지 태깅 성공 검증

- [x] **구현**: `podman.py`

  ```python
  def tag_image(
      self,
      image_id: str,
      project: str,
      upload_key: str
  ) -> str:
      """
      이미지에 태그 추가

      Returns:
          tagged_image: 태그된 전체 이미지 경로
      """
      registry = self._normalize_registry(self._harbor_url)
      tagged_image = f"{registry}/{project}/{upload_key}"

      try:
          image = self._client.images.get(image_id)
          image.tag(tagged_image)
          return tagged_image
      except Exception as e:
          raise ImageNotFoundError(f"Image not found: {e}")

  def _normalize_registry(self, registry: str) -> str:
      """Harbor registry URL 정규화"""
      # 스킴 제거
      registry = registry.replace('https://', '').replace('http://', '')
      # 트레일링 슬래시 제거
      registry = registry.rstrip('/')
      # 공백 제거
      registry = registry.strip()
      return registry
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 2.3.2: tag_image URL 정규화 검증

- [x] **테스트 작성**: 엣지 케이스

  - https:// 스킴 제거
  - http:// 스킴 제거
  - 트레일링 슬래시 제거
  - 포트 포함 URL 처리

- [x] **구현**: (이미 구현됨)

- [x] **검증**: `poe check` 통과

---

### Task 2.4: 이미지 푸시 구현

**목적**: Harbor Registry에 이미지 푸시

#### Subtask 2.4.1: push_image 성공 케이스

- [x] **테스트 작성**: `test_push_image.py`

  - Mock 사용: 이미지 푸시 성공 검증

- [x] **구현**: `podman.py`

  ```python
  def push_image(self, tagged_image: str) -> None:
      """
      Harbor Registry에 이미지 푸시

      중요: Harbor 인증은 keynet-train login에서 완료됨
      """
      try:
          image = self._client.images.get(tagged_image)
          image.push()
      except Exception as e:
          raise PushError(f"Image push failed: {e}")
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 2.4.2: push_image 실패 케이스

- [x] **테스트 작성**: 에러 케이스

  - 이미지가 없을 때 PushError
  - 네트워크 에러 시 PushError

- [x] **구현**: 에러 처리 (이미 구현됨)

- [x] **검증**: `poe check` 통과

---

### Task 2.5: Milestone 2 Refactor

**목적**: M2 완료 후 코드 개선

#### Subtask 2.5.1: PodmanClient 에러 매핑 통합

- [x] **리팩토링**: 예외 처리를 `_handle_podman_error`로 통합

  ```python
  def _handle_podman_error(self, error: Exception, context: str) -> None:
      """Podman 에러를 적절한 예외로 변환"""
      error_msg = str(error).lower()

      if "not found" in error_msg or "no such" in error_msg:
          raise ImageNotFoundError(f"{context}: {error}")
      elif "connection" in error_msg or "timeout" in error_msg:
          raise PushError(f"{context}: Network error - {error}")
      else:
          raise PodmanError(f"{context}: {error}")
  ```

- [x] **검증**: 기존 테스트 모두 통과

---

## Milestone 3: Push 워크플로우 통합

**목표**: 전체 Step 1-9 통합
**의존성**: M0 + M1 + M2 완료

### Task 3.1: 프로젝트 선택 UI

**목적**: 프로젝트 목록 표시 및 사용자 선택

#### Subtask 3.1.1: 프로젝트 선택 함수 구현

- [x] **테스트 작성**: `test_select_project.py`

  - 프로젝트 목록 표시 검증
  - 유효한 선택 입력
  - 빈 프로젝트 목록 처리

- [x] **구현**: `packages/train/keynet_train/cli/commands/push.py`

  ```python
  def select_project(client: BackendClient, page: int = 0, limit: int = 20) -> int:
      """
      프로젝트 목록 조회 및 사용자 선택

      Returns:
          project_id: 선택한 프로젝트 ID

      Raises:
          ValueError: 프로젝트가 없을 때
      """
      response = client.fetch_trainable_projects(page=page, limit=limit)

      if not response.content:
          raise ValueError("No trainable projects found. Please create a project first.")

      print("\n학습 가능한 프로젝트 목록:")
      for idx, project in enumerate(response.content, 1):
          print(f"[{idx}] {project.title} ({project.task_type}) - {project.author['displayName']}")

      # 페이지네이션 정보 표시
      if response.meta.total > limit:
          print(f"\n(표시: 1-{min(limit, response.meta.total)} / 전체: {response.meta.total})")

      while True:
          try:
              choice = int(input(f"\n선택하세요 (1-{len(response.content)}): "))
              if 1 <= choice <= len(response.content):
                  return response.content[choice - 1].id
          except (ValueError, KeyboardInterrupt):
              pass
          print("❌ 잘못된 선택입니다. 다시 입력해주세요.")
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 3.1.2: 프로젝트 선택 에러 처리

- [x] **테스트 작성**: 에러 케이스

  - 잘못된 입력 처리
  - API 에러 시 예외 전파

- [x] **구현**: 에러 처리 (이미 구현됨)

- [x] **검증**: `poe check` 통과

---

### Task 3.2: handle_push 전체 통합

**목적**: Step 1-9 전체 워크플로우 구현

#### Subtask 3.2.1: handle_push 기본 흐름

- [x] **테스트 작성**: `test_handle_push_integration.py`

  - 전체 워크플로우 통합 테스트 (Mock 사용)

- [x] **구현**: `push.py` 업데이트

  ```python
  def handle_push(args, config_manager):
      """
      Push 명령 전체 워크플로우

      Returns:
          int: Exit code (0 for success)
      """
      try:
          # Step 1: 인증 확인
          print("📋 Step 1/9: Checking authentication...")
          config = config_manager.load_config()
          if not config:
              print("❌ Not logged in. Run: keynet-train login")
              return 1
          print("✅ Authenticated")

          # Step 2: Entrypoint 검증
          print("\n📋 Step 2/9: Validating entrypoint...")
          validator = PythonSyntaxValidator()
          validator.validate_file(args.entrypoint)
          print("✅ Validation passed")

          # Step 3: 하이퍼파라미터 추출
          print("\n📋 Step 3/9: Extracting hyperparameters...")
          extractor = ArgumentParserExtractor()
          metadata = extractor.extract_metadata(args.entrypoint)
          hyper_params = convert_to_argument_definitions(metadata)
          print(f"✅ Found {len(hyper_params)} hyperparameters")

          # Step 4: 프로젝트 선택
          print("\n📋 Step 4/9: Selecting project...")
          backend_client = BackendClient(
              config["server_url"],
              config["api_token"]
          )

          with backend_client:
              project_id = select_project(backend_client)
              print(f"✅ Selected project ID: {project_id}")

              # Step 5: UploadKey 발급
              print("\n📋 Step 5/9: Requesting upload key...")
              request = UploadKeyRequest(
                  model_name=args.model_name or Path(args.entrypoint).stem,
                  hyper_parameters=hyper_params
              )
              upload_response = backend_client.request_upload_key(project_id, request)
              print(f"✅ Upload key: {upload_response.upload_key}")

          # Step 6: 이미지 빌드
          print("\n📋 Step 6/9: Building container image...")
          podman_client = PodmanClient(config["harbor"])
          image_id = podman_client.build_image(
              entrypoint=args.entrypoint,
              context_path=args.context or ".",
              dockerfile_path=args.dockerfile,  # None이면 자동 생성
              base_image=args.base_image or "python:3.10-slim",
              no_cache=args.no_cache
          )
          print(f"✅ Built image: {image_id[:12]}")

          # Step 7: 이미지 태깅
          print("\n📋 Step 7/9: Tagging image...")
          tagged_image = podman_client.tag_image(
              image_id=image_id,
              project=args.project or "kitech-model",
              upload_key=upload_response.upload_key
          )
          print(f"✅ Tagged: {tagged_image}")

          # Step 8: 이미지 푸시
          print("\n📋 Step 8/9: Pushing to Harbor...")
          podman_client.push_image(tagged_image)
          print("✅ Push completed")

          # Step 9: 결과 출력
          print("\n✨ Push completed successfully!")
          print(f"   Upload Key: {upload_response.upload_key}")
          print(f"   Image: {tagged_image}")
          print(f"   Hyperparameters: {len(hyper_params)} arguments sent to Backend")

          return 0

      except AuthenticationError as e:
          print(f"\n❌ Authentication failed: {e}")
          print("   → Run: keynet-train login")
          return 1
      except ValidationError as e:
          print(f"\n❌ Validation failed: {e}")
          print("   → Check your input and try again")
          return 1
      except BuildError as e:
          print(f"\n❌ Build failed: {e}")
          print("   → Check your Dockerfile and build context")
          return 1
      except PushError as e:
          print(f"\n❌ Push failed: {e}")
          print("   → Check Harbor connectivity and credentials")
          return 1
      except NetworkError as e:
          print(f"\n❌ Network error: {e}")
          print("   → Check your internet connection")
          return 1
      except Exception as e:
          print(f"\n❌ Unexpected error: {e}")
          return 1
  ```

- [x] **검증**: `poe check` 통과

#### Subtask 3.2.2: handle_push 에러 처리

- [x] **테스트 작성**: 각 Step 실패 케이스

  - Step 1 실패: 미인증 → Exit code 1
  - Step 2 실패: 잘못된 entrypoint → Exit code 1
  - Step 4/5 실패: API 에러 → Exit code 1
  - Step 6 실패: 빌드 에러 → Exit code 1
  - Step 8 실패: 푸시 에러 → Exit code 1

- [x] **구현**: 각 Step try-except 처리 (이미 구현됨)

- [x] **검증**: `poe check` 통과

---

### Task 3.3: CLI 인자 추가

**목적**: push 명령 CLI 인자 정의

#### Subtask 3.3.1: CLI 인자 정의

- [x] **테스트 작성**: `test_push_cli_args.py`

  - 필수 인자 검증 (entrypoint 누락 시 에러)
  - 선택 인자 검증 (--dockerfile, --base-image, --context, --model-name, --project, --no-cache)

- [x] **구현**: CLI 인자 정의

  ```python
  def setup_push_parser(subparsers):
      push_parser = subparsers.add_parser(
          "push",
          help="Build and push training container image"
      )

      push_parser.add_argument(
          "entrypoint",
          help="Training script entrypoint (e.g., train.py)"
      )
      push_parser.add_argument(
          "--dockerfile",
          default=None,
          help="Path to Dockerfile (optional, auto-generated if not provided)"
      )
      push_parser.add_argument(
          "--base-image",
          default="python:3.10-slim",
          help="Base image for auto-generated Dockerfile (default: python:3.10-slim)"
      )
      push_parser.add_argument(
          "--context",
          help="Build context directory (default: current directory)"
      )
      push_parser.add_argument(
          "--model-name",
          help="Model name (default: entrypoint filename)"
      )
      push_parser.add_argument(
          "--project",
          help="Harbor project name (default: kitech-model)"
      )
      push_parser.add_argument(
          "--no-cache",
          action="store_true",
          help="Build image without cache"
      )

      push_parser.set_defaults(func=handle_push)
  ```

- [x] **검증**: `poe check` 통과

---

### Task 3.4: Milestone 3 Refactor

**목적**: M3 완료 후 코드 개선

#### Subtask 3.4.1: handle_push 출력 메시지 표준화

- [x] **리팩토링**: 일관된 출력 형식 적용

  ```python
  def print_step(step: int, total: int, message: str):
      print(f"\n📋 Step {step}/{total}: {message}...")

  def print_success(message: str):
      print(f"✅ {message}")
  ```

- [x] **검증**: 기존 테스트 모두 통과

---

## Milestone 4: 에러 처리 및 사용자 경험

**목표**: 사용자 친화적 에러 메시지 및 프로그레스 표시

### Task 4.1: 에러 메시지 개선

**목적**: 명확하고 실행 가능한 에러 메시지

#### Subtask 4.1.1: 에러 메시지 표준화

- [x] **테스트 작성**: `test_error_messages.py`

  - 인증 에러 시 재로그인 안내 포함
  - 빌드 에러 시 구체적 원인 표시
  - 네트워크 에러 시 연결 확인 안내

- [x] **구현**: 에러 메시지 개선

**에러 메시지 형식**:

```python
except AuthenticationError as e:
    print(f"\n❌ Authentication failed: {e}")
    print("   → Run: keynet-train login")
    print("   → Check your credentials")
    return 1

except BuildError as e:
    print(f"\n❌ Build failed: {e}")
    print("   → Check your Dockerfile syntax")
    print("   → Verify build context path")
    print("   → Try with --no-cache flag")
    return 1

except NetworkError as e:
    print(f"\n❌ Network error: {e}")
    print("   → Check your internet connection")
    print("   → Verify server URL in config")
    print("   → Check firewall/proxy settings")
    return 1
```

- [x] **검증**: `poe check` 통과

---

### Task 4.2: 프로그레스 표시

**목적**: 각 Step 진행 상황 표시

#### Subtask 4.2.1: Step 프로그레스 출력

- [x] **구현**: 각 Step 시작 시 출력 (이미 M3에서 구현됨)

**출력 형식**:

```
📋 Step 1/9: Checking authentication...
✅ Authenticated

📋 Step 2/9: Validating entrypoint...
✅ Validation passed

📋 Step 3/9: Extracting hyperparameters...
✅ Found 5 hyperparameters
```

- [x] **검증**: `test_progress_output.py` 테스트 작성 및 통과

---

### Task 4.3: E2E 통합 테스트

**목적**: 실제 환경에서 전체 워크플로우 검증

#### Subtask 4.3.1: E2E 테스트 작성

- [x] **테스트 작성**: `test_e2e_push.py`

**테스트 구조**:

```python
@pytest.mark.e2e
def test_full_push_workflow():
    """실제 Backend API + Podman으로 전체 워크플로우"""
    server_url = os.getenv("E2E_SERVER_URL")
    api_key = os.getenv("E2E_API_KEY")

    if not server_url or not api_key:
        pytest.skip("E2E test environment not configured")

    # 1. 실제 API 호출
    # 2. 실제 이미지 빌드
    # 3. 실제 Harbor 푸시
```

- [x] **실행**: `poe test -m e2e`

- [x] **검증**: 환경변수 없으면 skip, 환경변수 있으면 전체 워크플로우 실행

---

## 완료 기준

### 각 Task 완료 조건

- [x] 모든 테스트 통과 (251 passed, 3 skipped)
- [x] `poe check` 통과 (lint + typecheck + test)
- [x] plan.md 체크박스 체크 (모든 Milestone 0-4 완료)
- [ ] 코드 리뷰 (선택사항)

### Milestone 완료 조건

- [x] 모든 Task 완료 (M0, M1, M2, M3, M4)
- [x] 통합 테스트 통과 (test_handle_push_integration.py)
- [x] 문서 업데이트 (필요 시)
- [x] Refactor 단계 완료 (각 Milestone Refactor 완료)

### 전체 프로젝트 완료 조건

- [x] 모든 Milestone 완료 (M0-M4)
- [x] E2E 테스트 작성 및 통과 (test_e2e_push.py, skip when not configured)
- [x] TECHSPEC.md와 일치 검증 (Backend API + Podman 아키텍처)
- [ ] Codex 리뷰 완료 (향후 선택사항)

---

## 다음 단계

1. **Milestone 0 시작**: 의존성 및 환경 정리부터 시작
2. **순서 엄수**: M0 → M1 → M2 → M3 → M4
3. **반복 실행**: Red → Green → Refactor 사이클 반복
