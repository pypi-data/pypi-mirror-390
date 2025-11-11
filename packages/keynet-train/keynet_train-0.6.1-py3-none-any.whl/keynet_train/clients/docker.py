"""Docker Client"""

import re
from pathlib import Path
from typing import Optional

import docker
from docker.errors import APIError, DockerException
from docker.errors import BuildError as DockerBuildError
from rich.console import Console

# Global console instance for rich output
console = Console()


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
ENTRYPOINT ["python", "{entrypoint_name}"]
"""

    def build_image(
        self,
        entrypoint: str,
        context_path: str = ".",
        dockerfile_path: Optional[str] = None,
        base_image: Optional[str] = None,
        no_cache: bool = False,
        platform: Optional[str] = None,
    ) -> str:
        """
        컨테이너 이미지 빌드 (진행 상황 표시 포함)

        Args:
            entrypoint: 훈련 스크립트 경로
            context_path: 빌드 컨텍스트 디렉토리
            dockerfile_path: Dockerfile 경로 (None이면 자동 생성)
            base_image: 베이스 이미지 (dockerfile_path=None일 때 필수, 그 외엔 무시됨)
            no_cache: 빌드 캐시 비활성화 (디버깅 또는 프로덕션 빌드 시 유용)
            platform: 타겟 플랫폼 (예: "linux/amd64", "linux/arm64")
                     macOS에서 Linux 서버 배포 시 "linux/amd64" 권장

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
                build_args = {
                    "path": context_path,
                    "dockerfile": str(temp_dockerfile.name),  # 상대 경로
                    "nocache": no_cache,
                    "decode": True,  # JSON 디코딩
                }
                if platform:
                    build_args["platform"] = platform
                build_logs = self._client.api.build(**build_args)
                image_id = self._process_build_logs(build_logs)
            else:
                # 사용자 제공 Dockerfile 사용
                build_args = {
                    "path": context_path,
                    "dockerfile": dockerfile_path,
                    "nocache": no_cache,
                    "decode": True,  # JSON 디코딩
                }
                if platform:
                    build_args["platform"] = platform
                build_logs = self._client.api.build(**build_args)
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
        빌드 로그를 처리하고 상세한 내용을 실시간으로 표시 (Progress spinner 포함)

        Args:
            build_logs: Docker API의 빌드 로그 제너레이터

        Returns:
            image_id: 빌드된 이미지 ID

        Raises:
            BuildError: 빌드 실패 시

        """
        from rich.progress import Progress, SpinnerColumn, TextColumn

        image_id = None
        error_messages = []

        # Rich Progress로 spinner 표시 (하단 고정)
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Building image...", total=None)

            for log in build_logs:
                # 에러 메시지 수집
                if "error" in log:
                    error_messages.append(log.get("error", "Unknown error"))

                # 에러 세부 정보 수집
                if "errorDetail" in log:
                    error_detail = log["errorDetail"]
                    error_messages.append(error_detail.get("message", "Unknown error"))

                # 스트림 출력 (거의 모든 내용 표시)
                if "stream" in log:
                    stream_msg = log["stream"].strip()
                    if stream_msg:
                        # "Step X/Y: ..." 형태의 메시지를 "[X/Y]" 형식으로 변환
                        step_match = re.match(
                            r"^Step (\d+)/(\d+)\s*:\s*(.+)", stream_msg
                        )
                        if step_match:
                            current, total, instruction = step_match.groups()
                            progress.console.print(
                                f"   [bold cyan][{current}/{total}][/bold cyan] {instruction}",
                                highlight=False,
                            )
                        elif stream_msg.startswith("---"):
                            # 구분선은 무시 (너무 시끄러움)
                            pass
                        elif stream_msg.startswith(" ---> "):
                            # 중간 이미지 ID는 dim 스타일로 표시
                            progress.console.print(
                                f"   [dim]{stream_msg}[/dim]",
                                highlight=False,
                            )
                        elif stream_msg.startswith("Successfully built"):
                            # 성공 메시지 표시
                            progress.console.print(
                                f"   [bold green]✓[/bold green] {stream_msg}",
                                highlight=False,
                            )
                        elif stream_msg.startswith("Successfully tagged"):
                            # 태그 메시지 표시
                            progress.console.print(
                                f"   [bold green]✓[/bold green] {stream_msg}",
                                highlight=False,
                            )
                        elif stream_msg.startswith("Removing intermediate container"):
                            # 중간 컨테이너 제거 메시지는 dim으로 표시
                            progress.console.print(
                                f"   [dim]{stream_msg}[/dim]",
                                highlight=False,
                            )
                        else:
                            # 나머지 모든 출력 표시 (RUN 명령 결과 등)
                            # 들여쓰기를 추가하여 Step과 구분
                            progress.console.print(
                                f"      {stream_msg}",
                                highlight=False,
                            )

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
        Registry에 이미지 푸시 (진행 상황 표시 포함)

        Args:
            tagged_image: 푸시할 이미지 (태그 포함)

        """
        from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

        try:
            # tagged_image를 repository와 tag로 분리
            if ":" in tagged_image:
                # 마지막 콜론을 기준으로 분리 (포트 번호 고려)
                repository, tag = tagged_image.rsplit(":", 1)
            else:
                repository = tagged_image
                tag = None

            # Docker SDK API: push(repository, tag, stream=True, decode=True)
            push_stream = self._client.images.push(
                repository=repository, tag=tag, stream=True, decode=True
            )

            # 진행 상황을 추적하기 위한 dict
            layer_tasks = {}

            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                for line in push_stream:
                    # 에러 처리
                    if "error" in line:
                        raise PushError(f"Push failed: {line['error']}")

                    # status와 id 추출
                    status = line.get("status", "")
                    layer_id = line.get("id", "")

                    # layer_id가 없으면 일반 상태 메시지 (예: "The push refers to repository...")
                    if not layer_id:
                        if status:
                            console.print(f"   [dim]{status}[/dim]")
                        continue

                    # 진행 상황 정보
                    progress_detail = line.get("progressDetail", {})
                    current = progress_detail.get("current", 0)
                    total = progress_detail.get("total", 0)

                    # Layer 작업이 아직 추가되지 않았으면 추가
                    if layer_id not in layer_tasks:
                        # Layer ID를 12자리로 축약
                        short_id = layer_id[:12] if len(layer_id) > 12 else layer_id
                        task_id = progress.add_task(
                            f"[cyan]Layer {short_id}[/cyan]: {status}",
                            total=total if total > 0 else 100,
                        )
                        layer_tasks[layer_id] = task_id
                    else:
                        task_id = layer_tasks[layer_id]

                    # 상태에 따라 처리
                    if status == "Pushing" and total > 0:
                        # 진행 중: 진행률 업데이트
                        short_id = layer_id[:12] if len(layer_id) > 12 else layer_id
                        progress.update(
                            task_id,
                            description=f"[cyan]Layer {short_id}[/cyan]: Pushing",
                            completed=current,
                            total=total,
                        )
                    elif status == "Pushed":
                        # 완료: 100%로 설정
                        short_id = layer_id[:12] if len(layer_id) > 12 else layer_id
                        progress.update(
                            task_id,
                            description=f"[green]Layer {short_id}[/green]: Pushed ✓",
                            completed=100,
                            total=100,
                        )
                    elif status == "Layer already exists":
                        # 이미 존재: 100%로 설정
                        short_id = layer_id[:12] if len(layer_id) > 12 else layer_id
                        progress.update(
                            task_id,
                            description=f"[yellow]Layer {short_id}[/yellow]: Already exists ✓",
                            completed=100,
                            total=100,
                        )
                    elif status == "Preparing":
                        # 준비 중
                        short_id = layer_id[:12] if len(layer_id) > 12 else layer_id
                        progress.update(
                            task_id,
                            description=f"[cyan]Layer {short_id}[/cyan]: Preparing",
                            completed=0,
                            total=100,
                        )
                    elif status == "Waiting":
                        # 대기 중
                        short_id = layer_id[:12] if len(layer_id) > 12 else layer_id
                        progress.update(
                            task_id,
                            description=f"[dim]Layer {short_id}[/dim]: Waiting",
                            completed=0,
                            total=100,
                        )

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

    def verify_harbor_credentials(self) -> bool:
        """
        Harbor registry 인증 정보 검증

        실제로 Harbor registry에 로그인을 시도하여 인증 정보가 유효한지 확인합니다.

        Returns:
            bool: 인증 성공 시 True, 실패 시 False

        """
        try:
            registry = self._normalize_registry(self._harbor_url)
            self._client.login(
                username=self._username,
                password=self._password,
                registry=registry,
            )
            return True
        except Exception:
            return False

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
