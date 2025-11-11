# 인증 아키텍처

## 문제

**현재**: 사용자가 2번 인증

1. Platform API (JWT)
2. Harbor Registry (podman login)

**목표**: 1번 로그인으로 모든 작업 완료

---

## 해결책

**Single Login + Auto Harbor Provisioning**

```
사용자 로그인 (1회)
  ↓
Platform API
  1. User 인증
  2. Platform JWT 발급 (24시간)
  3. Harbor Robot Account 생성/조회 (없으면 생성)
  4. LoginResponse 반환 (JWT + Harbor credentials)
  ↓
CLI
  1. JSON 파일에 저장 (~/.config/keynet/config.json, 600)
  2. podman login 자동 실행 ← 핵심!
  3. 이후 모든 작업 자동 사용
```

**결과**: 사용자는 Platform에만 로그인, Harbor는 자동

---

## Backend API 계약

### POST /v1/auth/sign-in/one-time

**책임**:

- User 인증 (email/password)
- Platform JWT 발급
- Harbor Robot Account 자동 생성/관리
- Credentials 반환

**Request**:

```json
POST /v1/auth/sign-in/one-time
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "****"
}
```

**Response (Success)**:

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR...",
  "accessTokenExpiresAt": "2025-11-05T08:00:00Z",
  "harbor": {
    "url": "https://kitech-harbor.wimcorp.dev",
    "username": "robot$550e8400e29b41d4a716446655440000",
    "password": "ABCD1234XYZ..."
  }
}
```

**Response (Error)**:

```json
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "AUTHENTICATION_FAILED",
  "message": "Invalid email or password"
}
```

### Backend 책임

**Platform API가 처리해야 할 사항**:

- User 인증 후 Harbor Robot Account 자동 생성/조회 (User당 1:1)
- Robot account credentials 암호화 저장 및 관리
- Robot Account는 Never expiration (무기한), 필요시 수동 revoke만 지원
- LoginResponse에 Harbor credentials 포함 반환

---

## CLI 구현

### ConfigManager

**위치**: `cli/config/manager.py`

**책임**:

- JSON 파일 관리 (`~/.config/keynet/config.json`)
- Credentials 저장 (600 권한)
- Credentials 로드

**구현**:

```python
from pathlib import Path
import json
from datetime import datetime

class ConfigManager:
    """~/.config/keynet/config.json 관리"""

    def __init__(self):
        self.config_file = Path.home() / ".config" / "keynet" / "config.json"

    def save_credentials(
        self,
        server_url: str,
        username: str,
        api_token: str,
        api_token_expires_at: str,
        harbor: dict  # {"url": str, "username": str, "password": str}
    ):
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "server_url": server_url,
            "username": username,
            "api_token": api_token,
            "api_token_expires_at": api_token_expires_at,
            "harbor": harbor,
            "last_login": datetime.now().isoformat()
        }

        self.config_file.write_text(json.dumps(config, indent=2))
        self.config_file.chmod(0o600)  # 소유자만 읽기/쓰기

    def load_config(self) -> dict | None:
        if not self.config_file.exists():
            return None
        return json.loads(self.config_file.read_text())
```

**저장 파일 예시** (`~/.config/keynet/config.json`):

```json
{
  "server_url": "https://api.example.com",
  "username": "user@example.com",
  "api_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "api_token_expires_at": "2025-11-05T08:00:00Z",
  "harbor": {
    "url": "https://kitech-harbor.wimcorp.dev",
    "username": "robot$550e8400e29b41d4a716446655440000",
    "password": "ABCD1234XYZ..."
  },
  "last_login": "2025-11-04T08:30:00"
}
```

**Note**: username 필드에는 email 값이 저장됩니다 (하위 호환성 유지).

### Login Command

**위치**: `cli/commands/config.py`

**책임**:

1. Backend API 호출 (`POST /v1/auth/cli/sign-in`)
2. Credentials 저장 (ConfigManager)
3. **자동 podman login 실행** ← DX 핵심!

**구현**:

```python
from getpass import getpass
import httpx
import subprocess

def handle_login(args, config_manager):
    email = input("Email: ")
    password = getpass("Password: ")

    # 1. Backend API 호출
    response = httpx.post(
        f"{args.server_url}/v1/auth/sign-in/one-time",
        json={"email": email, "password": password},
        timeout=30.0
    )

    if response.status_code != 200:
        print(f"❌ Login failed: {response.json().get('message', 'Unknown error')}")
        sys.exit(1)

    data = response.json()

    # 2. Credentials 저장
    config_manager.save_credentials(
        server_url=args.server_url,
        username=email,  # email 값을 username 필드에 저장 (하위 호환성)
        api_token=data["accessToken"],
        api_token_expires_at=data["accessTokenExpiresAt"],
        harbor=data["harbor"]
    )

    # 3. 자동 podman login 실행 ← 핵심!
    print(f"🔐 Logging into Harbor ({data['harbor']['url']})...")
    result = subprocess.run(
        [
            "podman", "login",
            data["harbor"]["url"],
            "--username", data["harbor"]["username"],
            "--password-stdin"
        ],
        input=data["harbor"]["password"].encode(),
        capture_output=True
    )

    if result.returncode != 0:
        print(f"⚠️  Podman login failed: {result.stderr.decode()}")
        print("Credentials saved, but you may need to login manually:")
        print(f"  podman login {data['harbor']['url']}")
    else:
        print("✅ Harbor login successful!")

    print(f"\n✅ Login complete!")
    print(f"   API token expires: {data['accessTokenExpiresAt']}")
```

### Push Command

**위치**: `cli/commands/push.py`

**책임**:

- Stored credentials 사용 (자동)
- Backend API 호출 (uploadKey 요청)
- Container image build & push
- Harbor 인증은 이미 완료 상태 (podman login 되어있음)

**구현**:

```python
def handle_push(args, config_manager):
    config = config_manager.load_config()
    if not config:
        print("❌ Not logged in. Run: keynet-train login")
        sys.exit(1)

    # 1. Backend API 호출 (uploadKey 요청)
    # TODO: projectId 출처 명확화 필요 (config? CLI 인자? 하드코딩?)
    project_id = "???"  # 미정
    response = httpx.post(
        f"{config['server_url']}/v1/projects/{project_id}/trains/images",
        headers={"Authorization": f"Bearer {config['api_token']}"},
        json={
            "modelName": args.training_script,
            "hyperParameters": []  # TODO: 하이퍼파라미터 추출
        }
    )
    upload_key = response.json()["uploadKey"]

    # 2. Container build
    print("🐳 Building container image...")
    build_image(args.training_script, upload_key)

    # 3. Harbor push (podman login 이미 되어있음!)
    print(f"🚀 Pushing to Harbor...")
    # 프로젝트: kitech-model 또는 kitech-runtime
    # harbor url에서 스킴 제거 (podman은 registry/project/repo 형식 필요)
    harbor_registry = config['harbor']['url'].replace('https://', '').replace('http://', '')
    subprocess.run([
        "podman", "push",
        f"{harbor_registry}/kitech-model/{upload_key}:latest"
    ], check=True)

    print("✅ Push completed!")
```

### Backend API: Fetch Trainable Projects

**API**: `GET /v1/projects/trainable`

**목적**: 사용자가 학습 가능한 인공지능 프로젝트 목록을 조회하여 선택

**Request**:

```http
GET /v1/projects/trainable?page=0&limit=20
Authorization: Bearer {accessToken}
```

**Response (Success)**:

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "content": [
    {
      "id": 123,
      "title": "객체 탐지 모델",
      "summary": "COCO 데이터셋 기반 객체 탐지",
      "taskType": "OBJECT_DETECTION",
      "author": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "displayName": "홍길동"
      }
    }
  ],
  "meta": {
    "total": 42,
    "page": 0,
    "limit": 20,
    "maxPage": 2
  }
}
```

**Response Schema** (Backend):

```kotlin
data class FetchTrainableProjectsResponse(
    val content: List<TrainingProjectBrief>,
    val meta: OffSetPageMeta
)

data class TrainingProjectBrief(
    val id: Long,                    // projectId로 사용
    val title: String,
    val summary: String,
    val taskType: TrainingTaskType,  // OBJECT_DETECTION, SEGMENTATION, OBJECT_CLASSIFICATION
    val author: Author
)

data class OffSetPageMeta(
    val total: Long,
    val page: Long,
    val limit: Int,
    val maxPage: Long                // 계산된 최대 페이지 번호
)
```

---

### Backend API: Upload Keys

**API**: `POST /v1/projects/{projectId}/trains/images`

**projectId 출처**:
- `GET /v1/projects/trainable`로 조회한 프로젝트 목록에서 사용자가 선택
- 선택한 `TrainingProjectBrief.id` 값을 사용

**Request Schema** (Backend):

```kotlin
data class CreateTrainingImageRequest(
    val modelName: String,              // 모델 명 (예: "object_detection")
    val hyperParameters: List<ArgumentDefinition> = emptyList()  // 선택사항
)
```

**Request Example**:

```http
POST /v1/projects/{projectId}/trains/images
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "modelName": "object_detection",
  "hyperParameters": [
    {
      "name": "learning_rate",
      "type": "float",
      "default": "0.001",
      "required": false,
      "help": "Learning rate for training"
    },
    {
      "name": "batch_size",
      "type": "int",
      "default": "32",
      "required": true,
      "help": "Batch size for training"
    }
  ]
}
```

**Response (Success)**:

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 123,
  "uploadKey": "abc123xyz456789012345",
  "command": "python train.py --learning_rate 0.001 --batch_size 32"
}
```

**Response (Error)**:

```json
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "INVALID_TOKEN",
  "message": "Authentication token is invalid or expired"
}
```

### Helper: build_image()

**책임**:

- Training script를 포함한 Dockerfile 생성
- Podman으로 container image 빌드
- Image tagging: `{harbor_url}/kitech-model/{upload_key}:latest` (또는 kitech-runtime)

**구현 위치**: `cli/commands/push.py` 또는 `cli/utils/container.py`

---

## 보안

### HTTPS 필수

- **내부 네트워크에서도 HTTPS 사용**
- Harbor credentials가 response body에 평문 포함
- Self-signed 허용, 단 certificate validation 활성화

### CLI Credential Storage

**파일**: `~/.config/keynet/config.json`

**권한**: `600` (소유자만 읽기/쓰기)

```bash
-rw------- (600) myuser mygroup config.json
```

**왜 JSON 파일로 충분한가?**:

- ✅ AWS CLI (`~/.aws/credentials`), gcloud, kubectl 모두 동일 방식
- ✅ 600 권한으로 다른 사용자 접근 불가
- ✅ 온프레미스 내부망 환경
- ✅ keyring 의존성 문제 없음 (서버, CI/CD 호환)

### 로깅 주의

**Backend/CLI 모두 적용**:

```python
# ❌ 위험
logger.info(f"Response: {response.json()}")

# ✅ 안전
logger.info(f"Login successful for {username}")
```

---

## 사용자 경험

### Before (2번 인증)

```bash
# 1. Platform 인증
keynet-train config set-api-key xxx

# 2. Harbor 인증 (수동)
podman login harbor.example.com

# 3. 작업
keynet-train push train.py
```

### After (1번 인증)

```bash
# 1. 로그인 (Platform + Harbor 자동)
keynet-train login https://api.example.com
# Email: user@example.com
# Password: ****
# ✅ Login complete!

# 2. 작업 (seamless!)
keynet-train push train.py
```

**핵심**: 사용자는 Platform에만 로그인, Harbor는 완전 자동
