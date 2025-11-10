"""Docker Client"""

import re
from pathlib import Path
from typing import Optional

import docker
from docker.errors import APIError, DockerException
from docker.errors import BuildError as DockerBuildError


# 에러 클래스 계층 구조
class DockerError(Exception):
    """Docker 에러 베이스 클래스"""

    pass


class BuildError(DockerError):
    """이미지 빌드 실패"""

    pass


class ImageNotFoundError(DockerError):
    """이미지를 찾을 수 없음"""

    pass


class PushError(DockerError):
    """이미지 푸시 실패"""

    pass


class DockerClient:
    """Docker Engine/Desktop 클라이언트"""

    def __init__(self, harbor_config: dict):
        """
        DockerClient 초기화

        Args:
            harbor_config: Harbor 설정 dict
                - url: Harbor Registry URL (필수)
                - username: Harbor 사용자명 (필수)
                - password: Harbor 비밀번호 (필수)

        Raises:
            ValueError: harbor_config 검증 실패

        """
        # harbor_config 검증
        self._validate_harbor_config(harbor_config)

        # Harbor 설정 저장
        self._harbor_url = harbor_config["url"]
        self._username = harbor_config["username"]
        self._password = harbor_config["password"]

        # Docker client 초기화
        self._client = docker.from_env()

    def _validate_harbor_config(self, config: dict) -> None:
        """
        Harbor 설정 검증

        Args:
            config: 검증할 harbor_config dict

        Raises:
            ValueError: 필수 키 누락 또는 빈 값

        """
        required_keys = ["url", "username", "password"]

        # 필수 키 존재 확인
        for key in required_keys:
            if key not in config:
                raise ValueError(
                    f"harbor_config must contain '{key}' key. "
                    f"Required keys: {required_keys}"
                )

        # 빈 값 확인
        for key in required_keys:
            if not config[key] or not config[key].strip():
                raise ValueError(f"harbor_config['{key}'] must not be empty")

    def _generate_dockerfile(self, entrypoint: str, base_image: str) -> str:
        """
        동적으로 Dockerfile 문자열 생성

        Args:
            entrypoint: 훈련 스크립트 파일명
            base_image: FROM 베이스 이미지

        Returns:
            str: Dockerfile 내용

        """
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

    def build_image(
        self,
        entrypoint: str,
        context_path: str = ".",
        dockerfile_path: Optional[str] = None,
        base_image: Optional[str] = None,
        no_cache: bool = False,
    ) -> str:
        """
        컨테이너 이미지 빌드 (진행 상황 표시 포함)

        Args:
            entrypoint: 훈련 스크립트 경로
            context_path: 빌드 컨텍스트 디렉토리
            dockerfile_path: Dockerfile 경로 (None이면 자동 생성)
            base_image: 베이스 이미지 (dockerfile_path=None일 때 필수, 그 외엔 무시됨)
            no_cache: 빌드 캐시 비활성화 (디버깅 또는 프로덕션 빌드 시 유용)

        Returns:
            image_id: 빌드된 이미지 ID

        Raises:
            BuildError: base_image가 필요한데 제공되지 않았을 때

        Note:
            requirements.txt는 context_path 내에 있으면 자동으로 감지되어 설치됩니다.

        """
        temp_dockerfile = None

        try:
            if dockerfile_path is None:
                # Auto-generate mode: base_image 필수
                if base_image is None:
                    raise BuildError(
                        "base_image is required when auto-generating Dockerfile. "
                        "Provide base_image or use custom Dockerfile with --dockerfile"
                    )
                # context_path에 임시 Dockerfile 생성
                temp_dockerfile = Path(context_path) / ".Dockerfile.keynet-train.tmp"

                # Dockerfile 생성
                dockerfile_content = self._generate_dockerfile(
                    entrypoint=entrypoint, base_image=base_image
                )
                temp_dockerfile.write_text(dockerfile_content)

                # 빌드 (stream=True로 로그 스트리밍)
                build_logs = self._client.api.build(
                    path=context_path,
                    dockerfile=str(temp_dockerfile.name),  # 상대 경로
                    nocache=no_cache,
                    decode=True,  # JSON 디코딩
                )
                image_id = self._process_build_logs(build_logs)
            else:
                # 사용자 제공 Dockerfile 사용
                build_logs = self._client.api.build(
                    path=context_path,
                    dockerfile=dockerfile_path,
                    nocache=no_cache,
                    decode=True,  # JSON 디코딩
                )
                image_id = self._process_build_logs(build_logs)

            if not image_id:
                raise BuildError("Failed to get image ID from build logs")

            return image_id

        except (DockerBuildError, DockerException) as e:
            raise BuildError(f"Image build failed: {e}")
        except Exception as e:
            raise BuildError(f"Unexpected error during build: {e}")
        finally:
            # 임시 Dockerfile 삭제
            if temp_dockerfile and temp_dockerfile.exists():
                temp_dockerfile.unlink()

    def _process_build_logs(self, build_logs) -> str:
        """
        빌드 로그를 처리하고 주요 단계를 실시간으로 표시

        Args:
            build_logs: Docker API의 빌드 로그 제너레이터

        Returns:
            image_id: 빌드된 이미지 ID

        Raises:
            BuildError: 빌드 실패 시

        """
        image_id = None
        error_messages = []

        for log in build_logs:
            # 에러 메시지 수집
            if "error" in log:
                error_messages.append(log.get("error", "Unknown error"))

            # 에러 세부 정보 수집
            if "errorDetail" in log:
                error_detail = log["errorDetail"]
                error_messages.append(error_detail.get("message", "Unknown error"))

            # 스트림 출력 (주요 단계만)
            if "stream" in log:
                stream_msg = log["stream"].strip()
                if stream_msg:
                    # "Step X/Y: ..." 형태의 메시지만 표시
                    if re.match(r"^Step \d+/\d+\s*:", stream_msg):
                        # Step 메시지는 간결하게 표시
                        print(f"   {stream_msg}")
                    elif stream_msg.startswith("---"):
                        # 구분선은 무시
                        pass
                    elif stream_msg.startswith(" ---> "):
                        # 이미지 ID나 중간 결과는 무시
                        pass
                    elif stream_msg.startswith("Successfully built"):
                        # 성공 메시지 표시
                        print(f"   ✓ {stream_msg}")
                    elif stream_msg.startswith("Successfully tagged"):
                        # 태그 메시지 표시
                        print(f"   ✓ {stream_msg}")

            # 이미지 ID 추출
            if "aux" in log and "ID" in log["aux"]:
                image_id = log["aux"]["ID"]

        # 에러 발생 시 예외 발생
        if error_messages:
            error_msg = "\n".join(error_messages)
            raise BuildError(f"Build failed:\n{error_msg}")

        return image_id

    def tag_image(self, image_id: str, project: str, upload_key: str) -> str:
        """
        이미지에 태그 추가

        Args:
            image_id: 이미지 ID
            project: Harbor 프로젝트명
            upload_key: 업로드 키 (형식: "model-name:version" 또는 "model-name")

        Returns:
            tagged_image: 태그된 전체 이미지 경로

        """
        registry = self._normalize_registry(self._harbor_url)

        # upload_key를 repository와 tag로 분리
        if ":" in upload_key:
            # upload_key에 태그가 포함된 경우 (예: "my-model:v1.0.0")
            model_name, tag = upload_key.rsplit(":", 1)
        else:
            # 태그가 없는 경우
            model_name = upload_key
            tag = "latest"

        repository = f"{registry}/{project}/{model_name}"

        try:
            image = self._client.images.get(image_id)
            # Docker SDK API: tag(repository, tag)
            image.tag(repository=repository, tag=tag)

            # 태그된 전체 이미지 경로 반환
            tagged_image = f"{repository}:{tag}"
            return tagged_image
        except (APIError, DockerException, Exception) as e:
            raise ImageNotFoundError(f"Image not found: {e}")

    def push_image(self, tagged_image: str) -> None:
        """
        Registry에 이미지 푸시

        Args:
            tagged_image: 푸시할 이미지 (태그 포함)

        """
        try:
            # tagged_image를 repository와 tag로 분리
            if ":" in tagged_image:
                # 마지막 콜론을 기준으로 분리 (포트 번호 고려)
                repository, tag = tagged_image.rsplit(":", 1)
            else:
                repository = tagged_image
                tag = None

            # Docker SDK API: push(repository, tag)
            self._client.images.push(repository=repository, tag=tag)
        except (APIError, DockerException, Exception) as e:
            raise PushError(f"Image push failed: {e}")

    def _normalize_registry(self, registry: str) -> str:
        """Harbor registry URL 정규화"""
        # 공백 제거 (먼저)
        registry = registry.strip()
        # 스킴 제거
        registry = registry.replace("https://", "").replace("http://", "")
        # 트레일링 슬래시 제거
        registry = registry.rstrip("/")
        return registry

    @classmethod
    def is_available(cls) -> bool:
        """
        현재 환경에서 Docker가 사용 가능한지 확인

        Returns:
            True if available, False otherwise

        """
        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    @classmethod
    def get_runtime_name(cls) -> str:
        """
        런타임 이름 반환

        Returns:
            "Docker"

        """
        return "Docker"
