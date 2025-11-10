# Backend 인증 아키텍처 사양서

## 문서 정보

- **버전**: 1.4
- **작성일**: 2025-11-04
- **최종 수정**: 2025-11-04 (암호화 포맷, 동시성 제어, 에러 응답 개선)
- **대상**: Backend API 서버

---

## 1. 개요

### 1.1 목적

본 문서는 keynet Platform의 **단일 로그인 기반 Harbor 자동 프로비저닝** 아키텍처를 Backend 관점에서 정의합니다.

### 1.2 핵심 가치

**사용자 경험 개선**:

- 사용자는 Platform에 1번만 로그인
- Harbor 인증은 완전히 자동화되어 사용자가 의식하지 않음
- CLI는 받은 credentials로 자동으로 `podman login` 실행

**보안 강화**:

- Harbor Robot Account를 User별로 격리하여 권한 분리
- Credentials 암호화 저장
- 필요시 수동 revoke 가능

**운영 효율성**:

- Robot Account 생성/관리 완전 자동화
- 수동 개입 없이 lifecycle 관리
- 감사 및 모니터링 가능

### 1.3 범위

**포함**:

- User 인증 및 JWT 발급
- Harbor Robot Account 자동 생성/조회
- Robot Account credentials 암호화 저장
- Robot Account credentials 관리
- OneTimeSignInResponse에 Harbor credentials 포함

**제외**:

- Harbor 자체 설치 및 구성
- CLI 구현
- Container 이미지 빌드 및 푸시

---

## 2. 핵심 설계 원칙

### 2.1 단일 책임 원칙

**Backend의 책임**:

1. User 인증 및 권한 확인
2. Harbor Robot Account 자동 프로비저닝
3. Credentials 보안 저장 및 관리
4. 필요시 수동 관리

**Backend가 하지 않는 것**:

- Harbor 직접 관리 (Harbor API를 통해서만)
- CLI 설치 또는 설정
- Container 이미지 빌드

### 2.2 보안 우선

**암호화**:

- Robot Account password는 DB에 암호화 저장 (필수)
- 전송 구간 HTTPS 강제 (내부망 포함)
- 로깅 시 credentials 노출 금지

**권한 최소화**:

- Robot Account는 kitech-model, kitech-runtime 프로젝트에만 접근
- Push 및 artifact 생성 권한만 부여(Pull/Admin 불필요)
- User별 Robot Account 격리

**Lifecycle 관리**:

- Robot Account 만료 기간: **Never** (무기한)
- 단순하고 운영 부담 없음
- 필요시 수동 revoke 가능 (보안 사고 등)

### 2.3 멱등성 보장

**로그인 시 동작**:

- 이미 Robot Account가 있으면 → 기존 것 반환
- 없으면 → 새로 생성 후 반환
- 여러 번 로그인해도 같은 Robot Account 사용

**재시도 안전성**:

- Harbor API 호출 실패 시 안전하게 재시도 가능
- 중복 생성 방지 (User ID를 Robot Account 이름에 직접 포함)

---

## 3. 데이터 모델

### 3.1 Users 테이블 확장 (Embeddable Pattern)

**목적**: User와 Harbor Robot Account 정보를 단일 테이블로 관리

**설계 결정**:

- **@Embeddable 패턴 사용**: 별도 테이블 없이 users 테이블에 컬럼 추가
- User와 Harbor credentials의 생명주기 동일
- JOIN 불필요, 빠른 조회 성능
- 코드 간결성

**추가 필드**:

| 필드명                | 타입         | 설명                                | 제약              |
| --------------------- | ------------ | ----------------------------------- | ----------------- |
| harbor_robot_name     | VARCHAR(255) | Harbor Robot 이름 (robot$xxx, 38자) | UNIQUE, NULL 허용 |
| harbor_robot_password | TEXT         | 암호화된 password (Base64)          | NULL 허용         |

**인덱스**:

```sql
-- Partial unique index (NULL 값 제외)
CREATE UNIQUE INDEX idx_users_harbor_robot_name
ON users(harbor_robot_name)
WHERE harbor_robot_name IS NOT NULL;
```

**Migration (V006)**:

```sql
ALTER TABLE users ADD COLUMN harbor_robot_name VARCHAR(255);
ALTER TABLE users ADD COLUMN harbor_robot_password TEXT;

CREATE UNIQUE INDEX idx_users_harbor_robot_name
ON users(harbor_robot_name)
WHERE harbor_robot_name IS NOT NULL;

COMMENT ON COLUMN users.harbor_robot_name IS 'Harbor robot account name (format: robot$xxx, 38 chars)';
COMMENT ON COLUMN users.harbor_robot_password IS 'Encrypted robot password (AES-256-GCM, Base64)';
```

**도메인 모델 (Kotlin)**:

```kotlin
// Domain Value Object
@Embeddable
data class HarborCredentials(
    @Column(name = "harbor_robot_name", length = 255)
    val robotName: String,

    @Convert(converter = HarborPasswordConverter::class)
    @Column(name = "harbor_robot_password", columnDefinition = "TEXT")
    val robotPassword: String
)

// Domain Entity
data class UserDomainEntity(
    val id: UUID,
    val email: String,
    // ... other fields ...
    val harborCredentials: HarborCredentials?  // NULL 가능
)

// JPA Entity
@Entity
@Table(name = "users")
class User(
    @Id val id: UUID,
    // ... other fields ...

    @Embedded
    var harborCredentials: HarborCredentials?  // @Embedded!
)
```

**관계**:

- User : HarborCredentials = 1 : 0..1 (Embedded)
- User가 삭제되면 harbor credentials도 함께 삭제 (자동)
- Foreign Key 없음 (Embeddable이므로)

**동시성 제어**:

- 동일 User의 동시 로그인 시 중복 생성 방지를 위해 **DistributedLock** 사용
- Lock Key: `harbor_robot_account:create:{user_id}`
- Lock 획득 실패 시: 대기 후 재시도
- 예시 구현:

  ```kotlin
  distributedLock.execute(
      key = "harbor_robot_account:create:${userId}",
      func = {
          // 1. DB 조회 (이미 생성되었을 수 있음)
          val user = userRepository.getById(userId)
          if (user.harborCredentials != null) {
              return@execute user.harborCredentials
          }

          // 2. Harbor API 호출 및 생성
          val result = harborApiClient.createRobotAccount(...)

          // 3. User에 저장
          user.provisionHarborCredentials(credentials)
          return@execute userRepository.save(user).harborCredentials
      }
  )
  ```

### 3.2 Robot Account 네이밍 규칙

**최종 형식** (Harbor가 생성):

```
robot${user_id_without_hyphens}
```

**예시**:

Backend의 User ID가 `550e8400-e29b-41d4-a716-446655440000`인 경우:

```
Harbor API 요청 시: "550e8400e29b41d4a716446655440000"
Harbor가 반환하는 이름: "robot$550e8400e29b41d4a716446655440000"
DB에 저장할 이름: "robot$550e8400e29b41d4a716446655440000"
```

**구성 요소**:

- `robot$` prefix: Harbor가 자동으로 추가 (요청 시 제외)
- `{user_id_without_hyphens}`: User의 UUIDv4에서 하이픈(-) 제거한 32자리 문자열

**설계 근거**:

1. **멱등성**: User ID를 직접 사용하므로 같은 User는 항상 같은 Robot Account 이름 생성
2. **중복 방지**: User ID 자체가 globally unique하므로 충돌 불가능
3. **단순성**: 프로젝트 이름 불필요 (permissions.namespace로 지정)
4. **추적 가능성**: Robot Account 이름만으로 어떤 User인지 역추적 가능

**Harbor 제약사항**:

- 허용 문자: 영숫자, 하이픈(-), 언더스코어(\_), 플러스(+)
- UUIDv4 하이픈 제거 후 → 영숫자만 남으므로 허용됨
- 길이: 32자 (UUID 하이픈 제거) + 6자 (robot$ prefix) = 38자

---

## 4. Harbor API 연동

### 4.1 Harbor Robot Account 생성

**Harbor API Endpoint**:

```
POST /api/v2.0/robots
```

**요청 예시**:

User ID: `550e8400-e29b-41d4-a716-446655440000`

```json
{
  "name": "550e8400e29b41d4a716446655440000",
  "description": "Auto-provisioned robot account for user (Never expires)",
  "level": "project",
  "duration": -1,
  "disable": false,
  "permissions": [
    {
      "kind": "project",
      "namespace": "kitech-model",
      "access": [
        {
          "resource": "repository",
          "action": "push"
        },
        {
          "resource": "artifact",
          "action": "create"
        }
      ]
    },
    {
      "kind": "project",
      "namespace": "kitech-runtime",
      "access": [
        {
          "resource": "repository",
          "action": "push"
        },
        {
          "resource": "artifact",
          "action": "create"
        }
      ]
    }
  ]
}
```

**중요 필드**:

- `name`: User ID에서 하이픈 제거한 32자리 문자열 (Harbor가 자동으로 `robot$` prefix 추가)
- `level`: "project" (프로젝트 레벨 Robot)
- `duration`: -1 (Never expiration)
- `permissions`: 여러 프로젝트에 권한 부여 가능 (배열로 추가)
  - `kitech-model`: 모델 이미지 저장용 프로젝트
  - `kitech-runtime`: 런타임 이미지 저장용 프로젝트
- `permissions.access`: push와 artifact create만 허용 (최소 권한 원칙)

**응답 처리**:

```json
{
  "id": 123,
  "name": "robot$550e8400e29b41d4a716446655440000",
  "secret": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "creation_time": "2025-11-04T08:00:00Z",
  "expires_at": -1
}
```

**중요 필드**:

- `name`: Harbor가 요청한 이름에 `robot$` prefix를 자동 추가한 전체 이름
- `secret`: **Harbor가 자동 생성한 복잡한 패스워드** (JWT 형태 또는 난수)
  - Backend는 이 값을 그대로 사용
  - 별도 패스워드 생성 불필요
  - AES-256-GCM으로 암호화하여 DB 저장
- `expires_at`: -1 (만료 없음, Unix timestamp 형식)
- `creation_time`: ISO 8601 형식의 생성 시각

### 4.2 구현 가이드

**패스워드 처리 흐름**:

```
1. Harbor API 호출
   ↓
2. Harbor 응답: { "secret": "eyJhbGciOiJSUzI1NiIs..." }
   ↓
3. secret 값을 AES-256-GCM으로 암호화
   ↓
4. DB에 harbor_robot_password로 저장 (users 테이블)
   ↓
5. 로그인 시 복호화하여 OneTimeSignInResponse에 포함
```

**중요**:

- Backend는 패스워드를 생성하지 않음 (Harbor가 자동 생성)
- DB에 저장 시 반드시 암호화 필요
- 복호화한 패스워드는 HTTPS를 통해서만 전송

### 4.3 에러 처리

**409 Conflict (이미 존재)**:

- 정상 케이스로 처리
- 기존 Robot Account 정보 조회하여 반환
- 로그 레벨: INFO

**401/403 (Harbor 인증 실패)**:

- Backend의 Harbor Admin credentials 확인 필요
- 사용자에게는 일반적인 에러 메시지 반환
- 로그 레벨: ERROR

**500 (Harbor 서버 오류)**:

- Exponential backoff로 재시도 (최대 3회)
- 최종 실패 시 사용자에게 "일시적 오류" 안내
- 로그 레벨: ERROR

---

## 5. API 계약

### 5.1 POST /v1/auth/sign-in/one-time

**책임**:

1. User 인증 (username/password)
2. Platform JWT 발급
3. Harbor Robot Account 자동 생성/조회
4. OneTimeSignInResponse 반환

**Request**:

```http
POST /v1/auth/sign-in/one-time
Content-Type: application/json

{
  "username": "myuser",
  "password": "****"
}
```

**Response (Success)**:

User ID: `550e8400-e29b-41d4-a716-446655440000`

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "accessTokenExpiresAt": "2025-11-04T12:00:00Z",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "myuser@example.com",
    "displayName": "My User",
    "role": "GENERAL"
  },
  "harbor": {
    "url": "https://kitech-harbor.wimcorp.dev",
    "username": "robot$550e8400e29b41d4a716446655440000",
    "password": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**참고**:

- `accessToken`: Platform JWT 토큰
- `accessTokenExpiresAt`: JWT 토큰 만료시간 (ISO 8601 형식)
- `user`: 사용자 정보 (UserDto - id, email, displayName, role 등 포함)
- `harbor.url`: 환경변수에서 가져온 Harbor 레지스트리 URL (DB에 저장하지 않음)
  - 포맷: 스킴 포함한 전체 URL (예: `https://kitech-harbor.wimcorp.dev`)
  - 포트가 기본값(443)이 아닌 경우 포함 (예: `https://harbor.example.com:8443`)
- `harbor.username`: Harbor Robot Account 이름 (Harbor가 `robot$` prefix 추가한 전체 이름)
- `harbor.password`: Harbor Robot Account 패스워드 (DB에서 복호화한 값)

**처리 흐름**:

```
1. User 인증 검증
   ↓
2. JWT 토큰 생성
   ↓
3. User의 HarborCredentials 조회 (user.harborCredentials)
   ├─ 있으면: 기존 credentials 사용
   └─ 없으면: Harbor API로 Robot Account 생성 + User에 저장
   ↓
4. Robot password 복호화 (JPA Converter 자동 처리)
   ↓
5. OneTimeSignInResponse 반환
```

**참고**: Robot Account는 만료되지 않으므로 만료 확인 로직이 불필요합니다.

### 5.2 주의사항

**HTTPS 필수**:

- Harbor credentials가 response body에 평문으로 포함
- 내부 네트워크에서도 HTTPS 사용 필수
- Self-signed certificate 허용 가능, 단 validation 활성화

**Credentials 로깅 금지**:

```python
# ❌ 위험
logger.info(f"Response: {response_data}")

# ✅ 안전
logger.info(f"Login successful for user={username}")
```

---

## 6. 보안 요구사항

### 6.1 암호화 저장

**암호화 대상**:

- `robot_password` 필드 (필수)
- Harbor가 자동 생성한 `secret` 값을 암호화하여 저장

**암호화 방식**:

- 대칭키 암호화 (AES-256-GCM 권장)
- 암호화 키는 환경변수 또는 Secret Manager에서 관리
- DB에 암호화 키 저장 금지

**저장 포맷** (업계 표준):

- `robot_password` 필드에 **Base64(IV || Ciphertext || Auth Tag)** 형식으로 저장
- IV (Initialization Vector): 12 bytes (GCM 표준)
- Ciphertext: 가변 길이 (원본 데이터 크기)
- Auth Tag: 16 bytes (GCM 인증 태그)
- 예시 구현:

  ```python
  # 암호화
  iv = os.urandom(12)
  cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
  encryptor = cipher.encryptor()
  ciphertext = encryptor.update(plaintext) + encryptor.finalize()
  auth_tag = encryptor.tag

  # Base64 인코딩하여 DB 저장
  encrypted_data = base64.b64encode(iv + ciphertext + auth_tag).decode('utf-8')

  # 복호화
  decoded = base64.b64decode(encrypted_data)
  iv = decoded[:12]
  auth_tag = decoded[-16:]
  ciphertext = decoded[12:-16]
  ```

**패스워드 처리 흐름**:

1. Harbor API 호출 → `secret` 필드 획득
2. `secret` 값 암호화 → `harbor_robot_password`에 저장 (users 테이블)
3. 로그인 시 복호화 → OneTimeSignInResponse에 포함

**구현 가이드라인**:

- 암호화/복호화 로직을 별도 모듈로 분리
- 암호화 키 rotation 가능하도록 설계
- 복호화 실패 시 적절한 에러 처리
- **중요**: Backend는 패스워드를 생성하지 않음 (Harbor가 자동 생성)

### 6.2 권한 관리

**Harbor Robot Account 권한**:

```json
{
  "permissions": [
    {
      "kind": "project",
      "namespace": "kitech-model",
      "access": [
        {
          "resource": "repository",
          "action": "push"
        },
        {
          "resource": "artifact",
          "action": "create"
        }
      ]
    },
    {
      "kind": "project",
      "namespace": "kitech-runtime",
      "access": [
        {
          "resource": "repository",
          "action": "push"
        },
        {
          "resource": "artifact",
          "action": "create"
        }
      ]
    }
  ]
}
```

**최소 권한 원칙**:

- kitech-model, kitech-runtime 프로젝트만 접근
- push 및 artifact 생성만 허용
- pull, delete, admin 권한 불필요

### 6.3 Lifecycle 관리

**Robot Account 만료 기간**:

- **Never** (무기한): 만료 기간 없음
- 단순하고 운영 부담 최소화
- 보안 사고 등 특별한 경우에만 수동 revoke

**수동 Revoke 시나리오**:

- 보안 사고 발생 시 (credentials 유출 등)
- User 계정 삭제 시 (cascade delete로 자동 처리)
- 장기 미사용 계정 정리 (선택사항)

**Revoke 절차**:

1. Harbor API로 Robot Account 비활성화/삭제
2. DB에서 HarborRobotAccount 레코드 삭제
3. User 재로그인 시 새 Robot Account 자동 생성

### 6.4 Rate Limiting

**로그인 실패 방지 정책**:

- **차단 기준**: 로그인 시도한 **아이디(username) 기준**
- **차단 조건**: 5회 연속 로그인 실패
- **차단 시간**: 30분
- **IP 기반 차단 사용 안 함**: 공유 네트워크 환경에서 오차단 방지

**구현 요구사항**:

```
1. 로그인 실패 시 카운터 증가
   - Key: username
   - TTL: 30분 (Redis 권장)

2. 5회 실패 시 계정 임시 잠금
   - 로그인 시도 거부
   - HTTP 429 (Too Many Requests) 반환
   - 에러 응답: 서버 표준 에러 응답 형식 사용

3. 로그인 성공 시 카운터 초기화

4. 30분 경과 후 자동 잠금 해제
```

**모니터링 지표**:

- 로그인 실패 횟수 (username별)
- Rate limit 차단 횟수
- 평균 차단 해제까지의 시간

**알림 조건**:

- 동일 username에서 10회 이상 차단 발생 시 (brute-force 공격 의심)
- 5분 내 50개 이상의 서로 다른 username 차단 시 (대규모 공격 의심)

---

## 7. 에러 처리 전략

### 7.1 에러 카테고리

| 에러 유형               | HTTP 상태 | 처리 방법                                  |
| ----------------------- | --------- | ------------------------------------------ |
| User 인증 실패          | 401       | 즉시 반환, 로그인 재시도 안내              |
| Rate Limit 초과         | 429       | 서버 표준 에러 응답 형식 사용              |
| Harbor API 인증 실패    | 500       | 내부 에러로 처리, Backend credentials 확인 |
| Harbor API 일시적 오류  | 500       | Exponential backoff 재시도 (최대 3회)      |
| Robot Account 생성 실패 | 500       | 재시도 후 실패 시 일시적 오류 안내         |
| 암호화/복호화 실패      | 500       | 내부 에러로 처리, 암호화 키 확인           |
| DB 연결 실패            | 500       | Circuit breaker 패턴 적용                  |

### 7.2 로깅 가이드라인

**필수 로깅 항목**:

- User 로그인 시도 및 결과
- Harbor Robot Account 생성/조회
- Harbor API 호출 성공/실패
- Robot Account 수동 revoke (발생 시)

**로깅 시 주의사항**:

```python
# ✅ 안전한 로깅
logger.info(f"Harbor Robot Account created", extra={
    "user_id": user.id,
    "robot_name": robot.name,
    "created_at": robot.created_at
})

# ❌ 위험한 로깅
logger.info(f"Robot password: {robot.password}")  # 절대 금지
```

---

## 8. 테스트 가이드라인

### 8.1 Unit Tests

**테스트 대상**:

- Robot Account 생성 로직
- 암호화/복호화 로직
- Robot Account 이름 생성
- 멱등성 검증 (중복 생성 방지)

**Mock 대상**:

- Harbor API 호출
- DB 트랜잭션
- 암호화 키 조회

### 8.2 Integration Tests

**시나리오**:

1. 신규 User 로그인 → Robot Account 생성 확인
2. 기존 User 로그인 → 동일 Robot Account 반환 확인
3. 동일 User 여러 번 로그인 → 멱등성 확인
4. Harbor API 실패 시 재시도 확인
5. 암호화/복호화 정상 동작 확인

**주의사항**:

- Test Harbor 인스턴스 사용 (Production 아님)
- Test 후 생성된 Robot Account 정리
- 병렬 테스트 시 User ID 충돌 방지

### 8.3 E2E Tests

**전체 플로우 테스트**:

```
1. User 회원가입
   ↓
2. User cli 로그인 (Robot Account 자동 생성)
   ↓
3. CLI에서 credentials 사용하여 podman login
   ↓
4. 이미지 빌드 및 푸시
   ↓
5. Harbor에서 이미지 확인
```
