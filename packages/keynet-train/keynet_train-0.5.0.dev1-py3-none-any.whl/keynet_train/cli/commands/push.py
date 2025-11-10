"""
Push command implementation.

This module implements the 'push' command that builds and pushes
container images for training templates.

ARCHITECTURE (Backend API + Docker):
1. Extract hyperparameters from training script
2. Request uploadKey from Backend API (with hyperparameters)
3. Build container image with Docker
4. Tag and push image to Harbor Registry
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..config.manager import ConfigManager
from ..parser.decorator import (
    extract_trace_pytorch_base_image,
    extract_trace_pytorch_model_name,
)
from ..parser.extractor import ArgumentParserExtractor
from ..validator import PythonSyntaxValidator


def print_step(step: int, total: int, message: str) -> None:
    """
    Print a step header message.

    Args:
        step: Current step number
        total: Total number of steps
        message: Step description

    """
    print(f"\n📋 Step {step}/{total}: {message}...")


def print_success(message: str) -> None:
    """
    Print a success message.

    Args:
        message: Success message to display

    """
    print(f"✅ {message}")


def setup_push_parser(subparsers: argparse._SubParsersAction) -> None:
    """
    Set up the push command parser.

    Args:
        subparsers: Subparsers action from parent parser

    """
    parser = subparsers.add_parser(
        "push",
        help="Build and push training container image",
        description="Build container image with Docker and send metadata to Backend API",
        epilog="""
Examples:
    # Build and push training image (requirements.txt auto-detected)
    keynet-train push train.py

    # Specify requirements.txt location
    keynet-train push train.py --requirements ./deps/requirements.txt

    # Use custom Dockerfile (ignores requirements)
    keynet-train push train.py --dockerfile ./Dockerfile

    # Custom base image (overrides @trace_pytorch base_image)
    keynet-train push train.py --base-image pytorch/pytorch:2.0.1

    # Custom build context
    keynet-train push train.py --context ./my-project

Notes:
    - Requires 'keynet-train login' first
    - Uses Harbor credentials and API token from config
    - Requires Docker installed and running
    - Hyperparameters extracted automatically from argparse/click/typer
    - Hyperparameters sent to Backend API during uploadKey request
    - Image tag is automatically generated from uploadKey
    - Without --dockerfile, requirements.txt is required (auto-detected or --requirements)
    - Base image priority: --base-image > @trace_pytorch base_image > python:3.10-slim
        """,
    )

    parser.add_argument(
        "entrypoint",
        type=str,
        help="Path to training script entrypoint (e.g., train.py)",
    )

    parser.add_argument(
        "--dockerfile",
        type=str,
        default=None,
        help="Path to custom Dockerfile (if not provided, auto-generates from requirements.txt)",
    )

    parser.add_argument(
        "--requirements",
        type=str,
        default=None,
        help="Path to requirements.txt (default: auto-detect in current/parent directories)",
    )

    parser.add_argument(
        "--context",
        type=str,
        default=".",
        help="Build context directory (default: current directory)",
    )

    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="Model name for uploadKey (default: auto-detect from @trace_pytorch or entrypoint filename)",
    )

    parser.add_argument(
        "--base-image",
        type=str,
        default=None,
        help="Base Docker image (default: auto-detect from @trace_pytorch or python:3.10-slim)",
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Build without using cache (useful for debugging or production builds)",
    )

    parser.set_defaults(func=handle_push)


def find_requirements_txt(start_path: Path) -> Optional[Path]:
    """
    자동으로 requirements.txt 파일을 찾습니다.

    현재 디렉토리와 상위 디렉토리를 검색합니다.

    Args:
        start_path: 검색을 시작할 경로

    Returns:
        requirements.txt 경로 또는 None

    """
    current = start_path if start_path.is_dir() else start_path.parent

    # 현재 디렉토리에서 찾기
    requirements = current / "requirements.txt"
    if requirements.exists():
        return requirements

    # 상위 디렉토리에서 찾기 (최대 2단계)
    for _ in range(2):
        current = current.parent
        requirements = current / "requirements.txt"
        if requirements.exists():
            return requirements

    return None


def select_project(client, page: int = 0, limit: int = 20) -> int:
    """
    프로젝트 목록 조회 및 사용자 선택 (페이징 지원)

    Returns:
        project_id: 선택한 프로젝트 ID

    Raises:
        ValueError: 프로젝트가 없을 때

    """
    current_page = page

    while True:
        response = client.fetch_trainable_projects(page=current_page, limit=limit)

        if not response.content:
            if current_page == 0:
                raise ValueError(
                    "No trainable projects found. Please create a project first."
                )
            else:
                print("\n❌ 이 페이지에 프로젝트가 없습니다.")
                current_page = max(0, current_page - 1)
                continue

        # 페이지 정보 계산
        total_pages = (response.meta.total + limit - 1) // limit
        start_idx = current_page * limit + 1
        end_idx = min((current_page + 1) * limit, response.meta.total)

        # 프로젝트 목록 표시
        print(
            f"\n학습 가능한 프로젝트 목록 ({start_idx}-{end_idx} / 전체: {response.meta.total})"
        )
        for idx, project in enumerate(response.content, 1):
            print(
                f"[{idx}] {project.title} ({project.task_type}) - {project.author['displayName']}"
            )

        # 페이지 네비게이션 안내
        nav_options = []
        if current_page > 0:
            nav_options.append("'p' for prev")
        if current_page < total_pages - 1:
            nav_options.append("'n' for next")

        nav_text = f", {', '.join(nav_options)}" if nav_options else ""

        # 사용자 입력
        while True:
            try:
                user_input = input(
                    f"\n선택하세요 (1-{len(response.content)}{nav_text}): "
                ).strip()

                # 페이지 네비게이션
                if user_input.lower() == "n" and current_page < total_pages - 1:
                    current_page += 1
                    break
                elif user_input.lower() == "p" and current_page > 0:
                    current_page -= 1
                    break
                elif user_input.lower() in ["n", "p"]:
                    print("❌ 더 이상 페이지가 없습니다.")
                    continue

                # 프로젝트 선택
                choice = int(user_input)
                if 1 <= choice <= len(response.content):
                    return response.content[choice - 1].id
                else:
                    print(f"❌ 1-{len(response.content)} 범위의 숫자를 입력해주세요.")
            except ValueError:
                print("❌ 잘못된 입력입니다. 숫자 또는 'n'/'p'를 입력해주세요.")
            except KeyboardInterrupt:
                print("\n\n❌ 취소되었습니다.")
                sys.exit(1)


def handle_push(args: argparse.Namespace) -> int:
    """
    Handle push command execution.

    WORKFLOW:
    1. Check authentication (Harbor credentials + API key)
    2. Validate entrypoint file (exists + valid Python syntax)
    3. Extract hyperparameters from entrypoint
    4. Select project from Backend API
    5. Determine model_name (CLI > decorator; required)
    6. Request uploadKey from Backend API (with model_name and hyperparameters)
    7. Resolve requirements.txt (auto-detect or explicit path)
    8. Build container image with Docker
    9. Tag image with uploadKey
    10. Push image to Harbor Registry
    11. Display success message

    Args:
        args: Parsed command-line arguments containing:
            - entrypoint: Path to training script
            - dockerfile: Path to Dockerfile (None for auto-generation)
            - requirements: Path to requirements.txt (None for auto-detection)
            - context: Build context path (default: ".")
            - model_name: Model name (None for auto-detect from decorator; required)
            - base_image: Base Docker image (None for auto-detect from decorator)

    Returns:
        Exit code:
            - 0: Success
            - 1: Error

    """
    from docker.errors import DockerException

    from keynet_train.clients.backend import (
        AuthenticationError,
        BackendClient,
        NetworkError,
    )
    from keynet_train.clients.converters import convert_to_argument_definitions
    from keynet_train.clients.docker import BuildError, DockerClient
    from keynet_train.clients.models import UploadKeyRequest

    try:
        # Step 1: Check authentication
        print_step(1, 10, "Checking authentication")
        config_manager = ConfigManager()

        # Check for Harbor credentials
        harbor_creds = config_manager.get_harbor_credentials()
        if not harbor_creds:
            print(
                "❌ Not logged in. Run: keynet-train login <server-url>",
                file=sys.stderr,
            )
            return 1

        # Check for API key
        api_key = config_manager.get_api_key()
        if not api_key:
            print("❌ API key not found", file=sys.stderr)
            return 1

        # Check for server URL
        server_url = config_manager.get_server_url()
        if not server_url:
            print("❌ Server URL not found", file=sys.stderr)
            return 1

        print_success("Authenticated")

        # Step 2: Validate entrypoint
        print_step(2, 10, "Validating entrypoint")
        entrypoint = Path(args.entrypoint)

        if not entrypoint.exists():
            print(f"❌ Entrypoint file not found: {args.entrypoint}", file=sys.stderr)
            return 1

        if not entrypoint.is_file():
            print(f"❌ Entrypoint is not a file: {args.entrypoint}", file=sys.stderr)
            return 1

        # Validate Python syntax
        validator = PythonSyntaxValidator()
        success, error = validator.validate_file(entrypoint)

        if not success:
            print(f"❌ Validation failed:\n{error}", file=sys.stderr)
            return 1

        print_success("Validation passed")

        # Extract model_name from decorator (if available)
        decorator_model_name = extract_trace_pytorch_model_name(str(entrypoint))
        if decorator_model_name:
            print(f"   🏷️  Found model_name in @trace_pytorch: {decorator_model_name}")

        # Extract base_image from decorator (if available)
        decorator_base_image = extract_trace_pytorch_base_image(str(entrypoint))
        if decorator_base_image:
            print(f"   📦 Found base_image in @trace_pytorch: {decorator_base_image}")

        # Step 3: Extract hyperparameters
        print_step(3, 10, "Extracting hyperparameters")
        extractor = ArgumentParserExtractor()
        metadata = extractor.extract_metadata(str(entrypoint))
        hyper_params = convert_to_argument_definitions(metadata)
        print_success(f"Found {len(hyper_params)} hyperparameters")

        # Step 4: Select project
        print_step(4, 10, "Selecting project")
        backend_client = BackendClient(server_url, api_key)

        with backend_client:
            project_id = select_project(backend_client)
            print_success(f"Selected project ID: {project_id}")

            # Step 5: Determine model_name (priority: CLI > decorator)
            print_step(5, 10, "Determining model name")
            if args.model_name is not None:
                # CLI argument has highest priority
                final_model_name = args.model_name
                print(f"   🎯 Using CLI model_name: {final_model_name}")
            elif decorator_model_name is not None:
                # Use decorator value if CLI not provided
                final_model_name = decorator_model_name
                print(f"   🎯 Using decorator model_name: {final_model_name}")
            else:
                # model_name is required
                print(
                    f"\n❌ model_name not specified.\n"
                    f"\n"
                    f"Please specify model_name in one of the following ways:\n"
                    f"\n"
                    f"1. In @trace_pytorch decorator (recommended):\n"
                    f"   @trace_pytorch(\n"
                    f"       \"experiment_name\",\n"
                    f"       torch.randn(1, 3, 224, 224),\n"
                    f"       model_name=\"resnet50-classifier\"  # Add this!\n"
                    f"   )\n"
                    f"\n"
                    f"2. Via CLI argument:\n"
                    f"   keynet-train push {args.entrypoint} --model-name resnet50-classifier\n",
                    file=sys.stderr,
                )
                return 1

            # Step 6: Request upload key
            print_step(6, 10, "Requesting upload key")
            request = UploadKeyRequest(
                modelName=final_model_name,
                hyperParameters=hyper_params,
            )
            upload_response = backend_client.request_upload_key(project_id, request)
            print_success(f"Upload key: {upload_response.upload_key}")

        # Step 7: Dockerfile type handling
        if args.dockerfile:
            # Custom Dockerfile: base_image not needed
            print_step(7, 11, "Using custom Dockerfile")
            print_success(f"Dockerfile: {args.dockerfile}")
            final_base_image = None  # Ignored by DockerClient
        else:
            # Auto-generate mode: requirements.txt + base_image required
            print_step(7, 11, "Resolving dependencies")

            # Check requirements.txt
            requirements_path = None
            if args.requirements:
                # Explicit requirements path
                requirements_path = Path(args.requirements)
                if not requirements_path.exists():
                    print(
                        f"❌ Requirements file not found: {args.requirements}",
                        file=sys.stderr,
                    )
                    return 1
                print_success(f"Using requirements: {requirements_path}")
            else:
                # Auto-detect requirements.txt
                requirements_path = find_requirements_txt(entrypoint)
                if requirements_path:
                    print_success(f"Found requirements: {requirements_path}")
                else:
                    print(
                        "❌ requirements.txt not found",
                        file=sys.stderr,
                    )
                    print(
                        "   → Add requirements.txt to your project",
                        file=sys.stderr,
                    )
                    print(
                        "   → Or use --requirements to specify path",
                        file=sys.stderr,
                    )
                    print(
                        "   → Or use --dockerfile to provide custom Dockerfile",
                        file=sys.stderr,
                    )
                    return 1

            # Determine base_image (required for auto-generate)
            if args.base_image is not None:
                # CLI argument has highest priority
                final_base_image = args.base_image
                print(f"   🎯 Using CLI base_image: {final_base_image}")
            elif decorator_base_image is not None:
                # Use decorator value if CLI not provided
                final_base_image = decorator_base_image
                print(f"   🎯 Using decorator base_image: {final_base_image}")
            else:
                # Error: base_image required for auto-generate
                print(
                    "❌ base_image not specified",
                    file=sys.stderr,
                )
                print(
                    "   → Add base_image parameter to @trace_pytorch decorator",
                    file=sys.stderr,
                )
                print(
                    "   → Or use --base-image CLI option",
                    file=sys.stderr,
                )
                print(
                    "   → Or provide custom Dockerfile with --dockerfile",
                    file=sys.stderr,
                )
                return 1

        # Step 8: Build container image
        print_step(8, 11, "Building container image")
        client = DockerClient(harbor_creds)
        image_id = client.build_image(
            entrypoint=str(entrypoint),
            context_path=args.context,
            dockerfile_path=args.dockerfile,
            base_image=final_base_image,
            no_cache=args.no_cache,
        )
        print_success(f"Built image: {image_id[:12]}")

        # Step 9: Tag image
        print_step(9, 11, "Tagging image")
        # Use full image reference from Backend API response
        target_image = upload_response.get_image_reference()
        # Tag the image using Docker SDK directly
        # Use rsplit to handle registries with ports (e.g., "registry.com:5000/project/model:tag")
        image = client._client.images.get(image_id)
        if ":" in target_image:
            repository, tag = target_image.rsplit(":", 1)
            image.tag(repository, tag=tag)
        else:
            image.tag(target_image, tag="latest")
        print_success(f"Tagged: {target_image}")

        # Step 10: Push image
        print_step(10, 11, "Pushing to Harbor")
        client.push_image(target_image)
        print_success("Push completed")

        # Step 11: Display success message
        print("\n✨ Push completed successfully!")
        print(f"   Upload Key: {upload_response.upload_key}")
        print(f"   Image: {target_image}")
        print(f"   Hyperparameters: {len(hyper_params)} arguments sent to Backend")

        return 0

    except AuthenticationError as e:
        print(f"\n❌ Authentication failed: {e}", file=sys.stderr)
        print("   → Run: keynet-train login", file=sys.stderr)
        print("   → Check your credentials", file=sys.stderr)
        return 1

    except BuildError as e:
        print(f"\n❌ Build failed: {e}", file=sys.stderr)
        print("   → Check your Dockerfile syntax", file=sys.stderr)
        print("   → Verify build context path", file=sys.stderr)
        print(
            "   → Check requirements.txt if using auto-generated Dockerfile",
            file=sys.stderr,
        )
        print("   → Try with --no-cache flag to force clean build", file=sys.stderr)
        return 1

    except NetworkError as e:
        print(f"\n❌ Network error: {e}", file=sys.stderr)
        print("   → Check your internet connection", file=sys.stderr)
        print("   → Verify server URL in config", file=sys.stderr)
        print("   → Check firewall/proxy settings", file=sys.stderr)
        return 1

    except DockerException as e:
        print(f"\n❌ Docker is not available: {e}", file=sys.stderr)
        print(
            "   → Install Docker Desktop: https://www.docker.com/products/docker-desktop",
            file=sys.stderr,
        )
        print("   → Start Docker Desktop", file=sys.stderr)
        print("   → Run: docker version", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
